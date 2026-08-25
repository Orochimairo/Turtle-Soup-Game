from typing import Protocol

from .models import GameSession, Puzzle


class PuzzleRepository(Protocol):
    def save(self, *, puzzle: Puzzle) -> None: ...

    def get(self, *, puzzle_id: str) -> Puzzle | None: ...

    def list_enabled(self) -> tuple[Puzzle, ...]: ...


class GameSessionRepository(Protocol):
    def save(self, *, session: GameSession) -> None: ...

    def get(self, *, session_id: str) -> GameSession | None: ...
