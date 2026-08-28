"""M5 真实模型语义评测 runner。

只通过固定 CLI 显式执行，不得由 pytest 自动收集（文件名不匹配收集规则）。
所有确定性校验完成前零模型调用、零目录创建。
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

import agently

from turtle_soup.catalog import load_puzzle_catalog
from turtle_soup.domain import QuestionRecord, Verdict
from turtle_soup.domain.model_ports import ModelJudgmentError
from turtle_soup.infrastructure import model as infra_model

_CASE_FIELDS = {"case_id", "puzzle_id", "category", "operation", "input", "history", "expected"}
_HISTORY_FIELDS = {"question", "verdict"}
_CATEGORIES = (
    "QUESTION_YES",
    "QUESTION_NO",
    "QUESTION_IRRELEVANT",
    "QUESTION_COLLOQUIAL",
    "QUESTION_INJECTION",
    "GUESS_SOLVED_PARAPHRASE",
    "GUESS_PARTIAL",
)
_QUESTION_CATEGORIES = _CATEGORIES[:5]
_GUESS_CATEGORIES = _CATEGORIES[5:]
_RUN_ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_BASE_TIME = datetime(2026, 1, 1, 8, 0, 0, tzinfo=UTC)


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _validate_result_path(result_path: str) -> Path:
    if os.path.isabs(result_path):
        raise ValueError("result-path must be a relative path under var/model_eval/m5/runs/")
    path = Path(result_path)
    parts = path.parts
    if len(parts) != 6 or ".." in parts:
        raise ValueError("result-path must be var/model_eval/m5/runs/<run-id>/results.v1.json")
    if parts[0] != "var" or parts[1] != "model_eval" or parts[2] != "m5" or parts[3] != "runs":
        raise ValueError("result-path must be var/model_eval/m5/runs/<run-id>/results.v1.json")
    if parts[5] != "results.v1.json":
        raise ValueError("result-path file must be named results.v1.json")
    run_id = parts[4]
    if not _RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError("run-id must contain only lowercase ASCII letters, digits and hyphens")
    repo_path = REPO_ROOT.joinpath(*parts)
    runs_dir = repo_path.parent.parent
    if runs_dir != REPO_ROOT / "var" / "model_eval" / "m5" / "runs":
        raise ValueError("result-path must resolve inside the repository var/model_eval/m5/runs/")
    if not runs_dir.is_dir():
        raise ValueError("var/model_eval/m5/runs/ must already exist")
    if repo_path.parent.exists():
        raise ValueError("run directory already exists")
    return repo_path


def _load_cases(cases_path: Path) -> list[dict]:
    raw = cases_path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("cases document must not start with a BOM")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("cases document is not valid UTF-8") from exc
    try:
        doc = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("cases document is not valid JSON") from exc
    if type(doc) is not dict or set(doc.keys()) != {"evaluation_version", "cases"}:
        raise ValueError("cases document top level is invalid")
    if type(doc["evaluation_version"]) is not int or doc["evaluation_version"] != 1:
        raise ValueError("evaluation_version must be the plain integer 1")
    cases = doc["cases"]
    if type(cases) is not list or len(cases) != 7:
        raise ValueError("cases must be an array of exactly 7 items")
    seen_ids = set()
    seen_categories = set()
    puzzle_ids = set()
    for case in cases:
        if type(case) is not dict or set(case.keys()) != _CASE_FIELDS:
            raise ValueError("case field set is invalid")
        case_id = case["case_id"]
        if type(case_id) is not str or not case_id.strip() or case_id in seen_ids:
            raise ValueError("case_id must be unique and non-blank")
        seen_ids.add(case_id)
        puzzle_id = case["puzzle_id"]
        if type(puzzle_id) is not str or not puzzle_id.strip():
            raise ValueError("puzzle_id must be a non-blank plain string")
        puzzle_ids.add(puzzle_id)
        category = case["category"]
        if type(category) is not str or category not in _CATEGORIES or category in seen_categories:
            raise ValueError("category must be one of the seven kinds, each exactly once")
        seen_categories.add(category)
        operation = case["operation"]
        if type(operation) is not str or operation not in ("QUESTION", "GUESS"):
            raise ValueError("operation must be QUESTION or GUESS")
        text_input = case["input"]
        if type(text_input) is not str or not text_input.strip():
            raise ValueError("input must be a non-blank plain string")
        history = case["history"]
        if type(history) is not list:
            raise ValueError("history must be an array")
        for item in history:
            if type(item) is not dict or set(item.keys()) != _HISTORY_FIELDS:
                raise ValueError("history item field set is invalid")
            if type(item["question"]) is not str or not item["question"].strip():
                raise ValueError("history question must be a non-blank plain string")
            if type(item["verdict"]) is not str or item["verdict"] not in ("YES", "NO", "IRRELEVANT"):
                raise ValueError("history verdict is invalid")
        expected = case["expected"]
        if category in _QUESTION_CATEGORIES:
            if operation != "QUESTION":
                raise ValueError("question category requires operation QUESTION")
            if category == "QUESTION_YES" and expected != "YES":
                raise ValueError("QUESTION_YES must expect YES")
            if category == "QUESTION_NO" and expected != "NO":
                raise ValueError("QUESTION_NO must expect NO")
            if category in ("QUESTION_IRRELEVANT", "QUESTION_INJECTION") and expected != "IRRELEVANT":
                raise ValueError("irrelevant question categories must expect IRRELEVANT")
            if category == "QUESTION_COLLOQUIAL" and (
                type(expected) is not str or expected not in ("YES", "NO", "IRRELEVANT")
            ):
                raise ValueError("QUESTION_COLLOQUIAL must expect a valid Verdict value")
        else:
            if operation != "GUESS":
                raise ValueError("guess category requires operation GUESS")
            if type(expected) is not bool:
                raise ValueError("guess categories must expect a plain boolean")
            if category == "GUESS_SOLVED_PARAPHRASE" and expected is not True:
                raise ValueError("GUESS_SOLVED_PARAPHRASE must expect true")
            if category == "GUESS_PARTIAL" and expected is not False:
                raise ValueError("GUESS_PARTIAL must expect false")
    if len(seen_categories) != 7:
        raise ValueError("all seven categories must appear exactly once")
    if len(puzzle_ids) < 3:
        raise ValueError("cases must cover at least 3 distinct puzzles")
    return cases


def _elapsed_ms(start: float) -> int:
    return round((time.monotonic() - start) * 1000)


def _build_history(case_index: int, history: list[dict]) -> tuple[QuestionRecord, ...]:
    return tuple(
        QuestionRecord(
            id=f"runner-history-{case_index}-{index}",
            question=item["question"],
            verdict=Verdict(item["verdict"]),
            created_at=_BASE_TIME,
        )
        for index, item in enumerate(history)
    )


async def _execute(cases: list[dict], puzzles_by_id: dict, judge, *, run_id: str, catalog_sha256: str) -> dict:
    run_start = time.monotonic()
    case_results = []
    actual_calls = 0
    stopped = False
    for case_index, case in enumerate(cases):
        base = {
            "case_id": case["case_id"],
            "puzzle_id": case["puzzle_id"],
            "category": case["category"],
            "operation": case["operation"],
            "expected": case["expected"],
        }
        if stopped:
            case_results.append(
                {**base, "observed": None, "status": "NOT_RUN", "error_category": "NOT_RUN", "elapsed_ms": 0}
            )
            continue
        puzzle = puzzles_by_id[case["puzzle_id"]]
        history = _build_history(case_index, case["history"])
        start = time.monotonic()
        try:
            if case["operation"] == "QUESTION":
                verdict = await judge.judge_question(
                    puzzle=puzzle, question=case["input"], history=history
                )
                observed = verdict.value
                matched = observed == case["expected"]
            else:
                solved = await judge.judge_guess(puzzle=puzzle, guess=case["input"], history=history)
                observed = solved
                matched = observed is case["expected"]
            actual_calls += 1
            case_results.append(
                {
                    **base,
                    "observed": observed,
                    "status": "PASSED" if matched else "MISMATCH",
                    "error_category": "NONE",
                    "elapsed_ms": _elapsed_ms(start),
                }
            )
        except ModelJudgmentError:
            actual_calls += 1
            stopped = True
            case_results.append(
                {
                    **base,
                    "observed": None,
                    "status": "ERROR",
                    "error_category": "MODEL_JUDGMENT_ERROR",
                    "elapsed_ms": _elapsed_ms(start),
                }
            )
    passed = sum(1 for item in case_results if item["status"] == "PASSED")
    mismatched = sum(1 for item in case_results if item["status"] == "MISMATCH")
    error = sum(1 for item in case_results if item["status"] == "ERROR")
    not_run = sum(1 for item in case_results if item["status"] == "NOT_RUN")
    overall_pass = passed == 7
    model_name = os.environ["MODEL_NAME"]
    return {
        "evaluation_version": 1,
        "run": {
            "run_id": run_id,
            "evaluation_date": datetime.now(UTC).date().isoformat(),
            "catalog_sha256": catalog_sha256,
            "provider_type": "OpenAICompatible",
            "model_name": model_name,
            "agently_version": agently.__version__,
            "status": "PASSED" if overall_pass else "FAILED",
            "configured_case_count": 7,
            "actual_logical_call_count": actual_calls,
            "configured_max_physical_attempt_count": 14,
            "observed_physical_attempt_count": "unavailable",
            "elapsed_ms": _elapsed_ms(run_start),
            "provider_usage": "unavailable",
        },
        "cases": case_results,
        "summary": {
            "total_cases": 7,
            "completed_cases": passed + mismatched + error,
            "passed_cases": passed,
            "mismatched_cases": mismatched,
            "error_cases": error,
            "not_run_cases": not_run,
            "overall_pass": overall_pass,
        },
    }


def _fail(category: str) -> int:
    print(f"puzzle model evaluation preflight failed: {category}", file=sys.stderr)
    return 1


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python backend/tests/model/run_real_model_evaluation.py")
    parser.add_argument("--catalog-path", required=True)
    parser.add_argument("--cases-path", required=True)
    parser.add_argument("--result-path", required=True)
    args = parser.parse_args(argv)

    try:
        result_path = _validate_result_path(args.result_path)
    except ValueError:
        return _fail("result path")

    try:
        cases = _load_cases(Path(args.cases_path))
    except (ValueError, OSError):
        return _fail("cases document")

    try:
        catalog_bytes = Path(args.catalog_path).read_bytes()
    except OSError:
        return _fail("catalog")
    try:
        puzzles = load_puzzle_catalog(catalog_path=args.catalog_path)
    except ValueError:
        return _fail("catalog")
    puzzles_by_id = {puzzle.id: puzzle for puzzle in puzzles}
    for case in cases:
        if case["puzzle_id"] not in puzzles_by_id:
            return _fail("cases document")

    try:
        judge = infra_model.create_agently_model_judge_from_environment()
    except ValueError:
        return _fail("environment")

    run_id = result_path.parent.name
    catalog_sha256 = hashlib.sha256(catalog_bytes).hexdigest().upper()

    result_path.parent.mkdir()
    results = asyncio.run(
        _execute(cases, puzzles_by_id, judge, run_id=run_id, catalog_sha256=catalog_sha256)
    )

    payload = json.dumps(results, ensure_ascii=False) + "\n"
    with open(result_path, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    return 0 if results["summary"]["overall_pass"] is True else 1


def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
