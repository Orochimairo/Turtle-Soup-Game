from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum


class PuzzleStatus(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class GameStatus(str, Enum):
    PLAYING = "PLAYING"
    SOLVED = "SOLVED"
    ABANDONED = "ABANDONED"


class Verdict(str, Enum):
    YES = "YES"
    NO = "NO"
    IRRELEVANT = "IRRELEVANT"


class InvalidGameStateError(RuntimeError):
    """在非 PLAYING 状态下执行仅限进行中的游戏操作时抛出。"""


def _require_non_blank(value: str) -> None:
    if type(value) is not str:
        raise ValueError("expected a plain str value")
    if not value.strip():
        raise ValueError("value must not be blank")


def _require_aware_datetime(value: datetime) -> None:
    if not isinstance(value, datetime):
        # SDD 冻结契约：字段类型错误统一抛 ValueError，而非 TRY004 建议的 TypeError。
        raise ValueError("expected a datetime instance")  # noqa: TRY004
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("expected a timezone-aware datetime")


@dataclass(frozen=True, kw_only=True)
class Puzzle:
    id: str
    title: str
    surface: str
    solution: str
    key_facts: tuple[str, ...]
    status: PuzzleStatus

    def __post_init__(self) -> None:
        _require_non_blank(self.id)
        _require_non_blank(self.title)
        _require_non_blank(self.surface)
        _require_non_blank(self.solution)
        if type(self.key_facts) is not tuple:
            raise ValueError("key_facts must be a plain tuple")
        if not self.key_facts:
            raise ValueError("key_facts must not be empty")
        for fact in self.key_facts:
            if type(fact) is not str:
                raise ValueError("key_facts items must be plain str")
            if not fact.strip():
                raise ValueError("key_facts items must not be blank")
        if type(self.status) is not PuzzleStatus:
            raise ValueError("status must be a PuzzleStatus instance")


@dataclass(frozen=True, kw_only=True)
class QuestionRecord:
    id: str
    question: str
    verdict: Verdict
    created_at: datetime

    def __post_init__(self) -> None:
        _require_non_blank(self.id)
        _require_non_blank(self.question)
        if type(self.verdict) is not Verdict:
            raise ValueError("verdict must be a Verdict instance")
        _require_aware_datetime(self.created_at)


@dataclass(frozen=True, kw_only=True)
class GuessRecord:
    id: str
    guess: str
    solved: bool
    created_at: datetime

    def __post_init__(self) -> None:
        _require_non_blank(self.id)
        _require_non_blank(self.guess)
        if type(self.solved) is not bool:
            raise ValueError("solved must be a plain bool")
        _require_aware_datetime(self.created_at)


def _validate_session(session: GameSession) -> None:
    _require_non_blank(session.id)
    _require_non_blank(session.puzzle_id)
    if type(session.status) is not GameStatus:
        raise ValueError("status must be a GameStatus instance")
    _require_aware_datetime(session.started_at)
    if session.ended_at is not None:
        _require_aware_datetime(session.ended_at)
        if session.ended_at < session.started_at:
            raise ValueError("ended_at must not be earlier than started_at")
    if type(session.questions) is not tuple:
        raise ValueError("questions must be a plain tuple")
    if type(session.guesses) is not tuple:
        raise ValueError("guesses must be a plain tuple")

    for record in session.questions:
        if not isinstance(record, QuestionRecord):
            # SDD 冻结契约：字段类型错误统一抛 ValueError。
            raise ValueError(  # noqa: TRY004
                "questions must contain only QuestionRecord instances"
            )
        if record.created_at < session.started_at:
            raise ValueError("record times must not be earlier than started_at")
    for record in session.guesses:
        if not isinstance(record, GuessRecord):
            # SDD 冻结契约：字段类型错误统一抛 ValueError。
            raise ValueError("guesses must contain only GuessRecord instances")  # noqa: TRY004
        if record.created_at < session.started_at:
            raise ValueError("record times must not be earlier than started_at")

    previous_question_time = None
    for record in session.questions:
        if previous_question_time is not None and record.created_at < previous_question_time:
            raise ValueError("question record times must not regress")
        previous_question_time = record.created_at
    previous_guess_time = None
    for record in session.guesses:
        if previous_guess_time is not None and record.created_at < previous_guess_time:
            raise ValueError("guess record times must not regress")
        previous_guess_time = record.created_at

    question_ids = [record.id for record in session.questions]
    if len(set(question_ids)) != len(question_ids):
        raise ValueError("question record ids must be unique within a session")
    guess_ids = [record.id for record in session.guesses]
    if len(set(guess_ids)) != len(guess_ids):
        raise ValueError("guess record ids must be unique within a session")

    if session.ended_at is not None:
        for record in (*session.questions, *session.guesses):
            if record.created_at > session.ended_at:
                raise ValueError("record times must not be later than ended_at")

    if session.status is GameStatus.PLAYING:
        if session.ended_at is not None:
            raise ValueError("PLAYING sessions must not have ended_at")
        if any(record.solved for record in session.guesses):
            raise ValueError("PLAYING sessions must not contain solved guesses")
    elif session.status is GameStatus.SOLVED:
        if session.ended_at is None:
            raise ValueError("SOLVED sessions must have ended_at")
        if not session.guesses:
            raise ValueError("SOLVED sessions must contain the solved guess")
        if not session.guesses[-1].solved:
            raise ValueError("the last guess of a SOLVED session must be solved")
        if any(record.solved for record in session.guesses[:-1]):
            raise ValueError("only the last guess of a SOLVED session may be solved")
    else:
        if session.ended_at is None:
            raise ValueError("ABANDONED sessions must have ended_at")
        if any(record.solved for record in session.guesses):
            raise ValueError("ABANDONED sessions must not contain solved guesses")


@dataclass(frozen=True, kw_only=True)
class GameSession:
    id: str
    puzzle_id: str
    status: GameStatus
    started_at: datetime
    ended_at: datetime | None
    questions: tuple[QuestionRecord, ...] = ()
    guesses: tuple[GuessRecord, ...] = ()

    def __post_init__(self) -> None:
        _validate_session(self)

    @classmethod
    def start(cls, *, id: str, puzzle_id: str, started_at: datetime) -> GameSession:
        return cls(
            id=id,
            puzzle_id=puzzle_id,
            status=GameStatus.PLAYING,
            started_at=started_at,
            ended_at=None,
        )

    def record_question(self, record: QuestionRecord) -> GameSession:
        if self.status is not GameStatus.PLAYING:
            raise InvalidGameStateError("questions can only be recorded while PLAYING")
        if not isinstance(record, QuestionRecord):
            # SDD 冻结契约：字段类型错误统一抛 ValueError。
            raise ValueError("record must be a QuestionRecord instance")  # noqa: TRY004
        return replace(self, questions=self.questions + (record,))

    def record_guess(self, record: GuessRecord) -> GameSession:
        if self.status is not GameStatus.PLAYING:
            raise InvalidGameStateError("guesses can only be recorded while PLAYING")
        if not isinstance(record, GuessRecord):
            # SDD 冻结契约：字段类型错误统一抛 ValueError。
            raise ValueError("record must be a GuessRecord instance")  # noqa: TRY004
        if record.solved:
            return replace(
                self,
                guesses=self.guesses + (record,),
                status=GameStatus.SOLVED,
                ended_at=record.created_at,
            )
        return replace(self, guesses=self.guesses + (record,))

    def abandon(self, *, ended_at: datetime) -> GameSession:
        if self.status is not GameStatus.PLAYING:
            raise InvalidGameStateError("only PLAYING sessions can be abandoned")
        return replace(self, status=GameStatus.ABANDONED, ended_at=ended_at)

    @property
    def can_reveal_solution(self) -> bool:
        return self.status is not GameStatus.PLAYING
