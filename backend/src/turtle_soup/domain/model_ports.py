from typing import Protocol

from .models import Puzzle, QuestionRecord, Verdict


class ModelJudgmentError(RuntimeError):
    """模型语义判定失败（超时、供应商失败、解析失败或宿主结构校验失败）。"""


class QuestionJudgmentPort(Protocol):
    async def judge_question(
        self,
        *,
        puzzle: Puzzle,
        question: str,
        history: tuple[QuestionRecord, ...],
    ) -> Verdict: ...


class GuessJudgmentPort(Protocol):
    async def judge_guess(
        self,
        *,
        puzzle: Puzzle,
        guess: str,
        history: tuple[QuestionRecord, ...],
    ) -> bool: ...


__all__ = [
    "GuessJudgmentPort",
    "ModelJudgmentError",
    "QuestionJudgmentPort",
]
