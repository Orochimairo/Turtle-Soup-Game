from __future__ import annotations

import json
import re
from pathlib import Path

from turtle_soup.domain.models import Puzzle, PuzzleStatus
from turtle_soup.infrastructure.sqlite import SQLitePuzzleRepository

_ID_PATTERN = re.compile(r"ts-(?!0000)[0-9]{4}")
_SOURCE_KINDS = ("ORIGINAL", "LICENSED", "PERMISSION", "PUBLIC_DOMAIN")
_PUZZLE_FIELDS = {"id", "title", "surface", "solution", "key_facts", "status", "provenance"}
_PROVENANCE_FIELDS = {"source_kind", "source_reference", "adaptation_note"}
_MIN_ENABLED = 8


class PuzzleCatalogError(ValueError):
    """题库资源格式、契约、路径或身份冲突错误。"""


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PuzzleCatalogError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _require_plain_non_blank(value, *, label: str) -> None:
    if type(value) is not str or not value.strip():
        raise PuzzleCatalogError(f"{label} must be a non-blank plain string")


def _parse_document(document: bytes) -> tuple[Puzzle, ...]:
    if document.startswith(b"\xef\xbb\xbf"):
        raise PuzzleCatalogError("catalog must not start with a UTF-8 BOM")
    try:
        text = document.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PuzzleCatalogError("catalog is not valid UTF-8") from exc
    if not text.endswith("\n"):
        raise PuzzleCatalogError("catalog must end with a newline")
    try:
        doc = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError) as exc:
        raise PuzzleCatalogError("catalog is not valid JSON") from exc

    if type(doc) is not dict or set(doc.keys()) != {"catalog_version", "puzzles"}:
        raise PuzzleCatalogError("catalog top level must contain exactly catalog_version and puzzles")
    version = doc["catalog_version"]
    if type(version) is not int or version != 1:
        raise PuzzleCatalogError("catalog_version must be the plain integer 1")
    puzzles = doc["puzzles"]
    if type(puzzles) is not list:
        raise PuzzleCatalogError("puzzles must be a JSON array")

    built = []
    enabled = 0
    previous_id = None
    for index, item in enumerate(puzzles):
        if type(item) is not dict or set(item.keys()) != _PUZZLE_FIELDS:
            raise PuzzleCatalogError(f"puzzle {index} has an invalid field set")
        _require_plain_non_blank(item["id"], label=f"puzzle {index} id")
        _require_plain_non_blank(item["title"], label=f"puzzle {index} title")
        _require_plain_non_blank(item["surface"], label=f"puzzle {index} surface")
        _require_plain_non_blank(item["solution"], label=f"puzzle {index} solution")
        if not _ID_PATTERN.fullmatch(item["id"]):
            raise PuzzleCatalogError(f"puzzle {index} id must match ts-NNNN")
        if previous_id is not None and item["id"] <= previous_id:
            raise PuzzleCatalogError("puzzle ids must be unique and strictly ascending")
        previous_id = item["id"]
        key_facts = item["key_facts"]
        if type(key_facts) is not list or not key_facts:
            raise PuzzleCatalogError(f"puzzle {index} key_facts must be a non-empty array")
        for fact_index, fact in enumerate(key_facts):
            if type(fact) is not str or not fact.strip():
                raise PuzzleCatalogError(f"puzzle {index} key_facts {fact_index} must be a non-blank plain string")
        status = item["status"]
        if type(status) is not str or status not in ("ENABLED", "DISABLED"):
            raise PuzzleCatalogError(f"puzzle {index} status must be ENABLED or DISABLED")
        provenance = item["provenance"]
        if type(provenance) is not dict or set(provenance.keys()) != _PROVENANCE_FIELDS:
            raise PuzzleCatalogError(f"puzzle {index} provenance has an invalid field set")
        source_kind = provenance["source_kind"]
        if type(source_kind) is not str or source_kind not in _SOURCE_KINDS:
            raise PuzzleCatalogError(f"puzzle {index} source_kind is unknown")
        _require_plain_non_blank(
            provenance["source_reference"], label=f"puzzle {index} source_reference"
        )
        adaptation_note = provenance["adaptation_note"]
        if adaptation_note is not None:
            _require_plain_non_blank(
                adaptation_note, label=f"puzzle {index} adaptation_note"
            )
        try:
            puzzle = Puzzle(
                id=item["id"],
                title=item["title"],
                surface=item["surface"],
                solution=item["solution"],
                key_facts=tuple(key_facts),
                status=PuzzleStatus(status),
            )
        except ValueError as exc:
            raise PuzzleCatalogError("catalog puzzle failed domain validation") from exc
        built.append(puzzle)
        if puzzle.status is PuzzleStatus.ENABLED:
            enabled += 1

    if enabled < _MIN_ENABLED:
        raise PuzzleCatalogError(f"catalog must contain at least {_MIN_ENABLED} ENABLED puzzles")
    return tuple(built)


def parse_puzzle_catalog_document(*, document: bytes) -> tuple[Puzzle, ...]:
    if type(document) is not bytes:
        raise PuzzleCatalogError("document must be a plain bytes value")
    return _parse_document(document)


def load_puzzle_catalog(*, catalog_path: str | Path) -> tuple[Puzzle, ...]:
    if type(catalog_path) is str:
        raw = catalog_path
        if not raw.strip():
            raise PuzzleCatalogError("catalog_path must not be blank")
        path = Path(raw)
    elif isinstance(catalog_path, Path):
        raw = str(catalog_path)
        path = catalog_path
    else:
        raise PuzzleCatalogError("catalog_path must be a str or pathlib.Path instance")
    if "://" in raw or raw.lower().startswith("file:"):
        raise PuzzleCatalogError("catalog_path must be a local file path, not a URL or URI")
    if not path.is_file():
        raise PuzzleCatalogError("catalog_path must point to an existing regular file")
    with open(path, "rb") as stream:
        document = stream.read()
    return parse_puzzle_catalog_document(document=document)


def import_puzzle_catalog(*, catalog_path: str | Path, database_path: str | Path) -> None:
    puzzles = load_puzzle_catalog(catalog_path=catalog_path)
    repository = SQLitePuzzleRepository(database_path=database_path)
    pending = []
    for puzzle in puzzles:
        existing = repository.get(puzzle_id=puzzle.id)
        if existing is None:
            pending.append(puzzle)
            continue
        core_unchanged = (
            existing.title == puzzle.title
            and existing.surface == puzzle.surface
            and existing.solution == puzzle.solution
            and existing.key_facts == puzzle.key_facts
        )
        if not core_unchanged:
            raise PuzzleCatalogError(f"puzzle {puzzle.id} conflicts with existing content")
        if existing.status is not puzzle.status:
            pending.append(puzzle)
    for puzzle in pending:
        repository.save(puzzle=puzzle)
