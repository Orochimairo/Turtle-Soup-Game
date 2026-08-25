from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from turtle_soup.domain.models import (
    GameSession,
    GameStatus,
    GuessRecord,
    Puzzle,
    PuzzleStatus,
    QuestionRecord,
    Verdict,
)
from turtle_soup.domain.ports import GameSessionRepository, PuzzleRepository

_SCHEMA_VERSION = 1
_M3_TABLE_NAMES = ("puzzles", "game_sessions", "question_records", "guess_records")

_EXPECTED_TABLES = {
    "puzzles": (
        ("id", "TEXT", 1, 1),
        ("title", "TEXT", 1, 0),
        ("surface", "TEXT", 1, 0),
        ("solution", "TEXT", 1, 0),
        ("key_facts_json", "TEXT", 1, 0),
        ("status", "TEXT", 1, 0),
    ),
    "game_sessions": (
        ("id", "TEXT", 1, 1),
        ("puzzle_id", "TEXT", 1, 0),
        ("status", "TEXT", 1, 0),
        ("started_at", "TEXT", 1, 0),
        ("ended_at", "TEXT", 0, 0),
    ),
    "question_records": (
        ("session_id", "TEXT", 1, 1),
        ("position", "INTEGER", 1, 0),
        ("record_id", "TEXT", 1, 2),
        ("question", "TEXT", 1, 0),
        ("verdict", "TEXT", 1, 0),
        ("created_at", "TEXT", 1, 0),
    ),
    "guess_records": (
        ("session_id", "TEXT", 1, 1),
        ("position", "INTEGER", 1, 0),
        ("record_id", "TEXT", 1, 2),
        ("guess", "TEXT", 1, 0),
        ("solved", "INTEGER", 1, 0),
        ("created_at", "TEXT", 1, 0),
    ),
}

_SCHEMA_STATEMENTS = (
    (
        "CREATE TABLE puzzles ("
        " id TEXT NOT NULL PRIMARY KEY,"
        " title TEXT NOT NULL,"
        " surface TEXT NOT NULL,"
        " solution TEXT NOT NULL,"
        " key_facts_json TEXT NOT NULL,"
        " status TEXT NOT NULL CHECK (status IN ('ENABLED', 'DISABLED')))"
    ),
    "CREATE INDEX idx_puzzles_status_id ON puzzles(status, id)",
    (
        "CREATE TABLE game_sessions ("
        " id TEXT NOT NULL PRIMARY KEY,"
        " puzzle_id TEXT NOT NULL REFERENCES puzzles(id),"
        " status TEXT NOT NULL CHECK (status IN ('PLAYING', 'SOLVED', 'ABANDONED')),"
        " started_at TEXT NOT NULL,"
        " ended_at TEXT,"
        " CHECK ((status = 'PLAYING' AND ended_at IS NULL)"
        " OR (status IN ('SOLVED', 'ABANDONED') AND ended_at IS NOT NULL)))"
    ),
    (
        "CREATE TABLE question_records ("
        " session_id TEXT NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,"
        " position INTEGER NOT NULL CHECK (position >= 0),"
        " record_id TEXT NOT NULL,"
        " question TEXT NOT NULL,"
        " verdict TEXT NOT NULL CHECK (verdict IN ('YES', 'NO', 'IRRELEVANT')),"
        " created_at TEXT NOT NULL,"
        " PRIMARY KEY (session_id, record_id),"
        " UNIQUE (session_id, position))"
    ),
    (
        "CREATE TABLE guess_records ("
        " session_id TEXT NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,"
        " position INTEGER NOT NULL CHECK (position >= 0),"
        " record_id TEXT NOT NULL,"
        " guess TEXT NOT NULL,"
        " solved INTEGER NOT NULL CHECK (solved IN (0, 1)),"
        " created_at TEXT NOT NULL,"
        " PRIMARY KEY (session_id, record_id),"
        " UNIQUE (session_id, position))"
    ),
)


class SQLiteSchemaError(RuntimeError):
    """SQLite Schema 版本、结构或初始化前提错误。"""


def _validate_database_path(database_path) -> Path:
    if type(database_path) is str:
        if not database_path.strip():
            raise ValueError("database_path must not be blank")
        raw = database_path
        path = Path(database_path)
    elif isinstance(database_path, Path):
        raw = str(database_path)
        path = database_path
    else:
        raise ValueError("database_path must be a str or pathlib.Path instance")
    if raw == ":memory:":
        raise ValueError("in-memory databases are not supported")
    if raw.lower().startswith("file:"):
        raise ValueError("SQLite URI paths are not supported")
    if not path.parent.is_dir():
        raise ValueError("the database parent directory must exist")
    if path.is_dir():
        raise ValueError("database_path must not be a directory")
    return path


@contextmanager
def _connection(database_path: Path):
    connection = sqlite3.connect(str(database_path))
    try:
        connection.isolation_level = None
        connection.execute("PRAGMA foreign_keys = ON")
        yield connection
    except BaseException:
        try:
            connection.rollback()
        except sqlite3.Error:
            pass
        raise
    finally:
        connection.close()


def _require_id(value: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError("id must be a non-blank str")


def _encode_key_facts(key_facts: tuple[str, ...]) -> str:
    return json.dumps(list(key_facts), ensure_ascii=False)


def _rebuild_puzzle(row: sqlite3.Row) -> Puzzle:
    facts = json.loads(row["key_facts_json"])
    if type(facts) is not list:
        raise ValueError("key_facts_json must decode to a JSON array")
    return Puzzle(
        id=row["id"],
        title=row["title"],
        surface=row["surface"],
        solution=row["solution"],
        key_facts=tuple(facts),
        status=PuzzleStatus(row["status"]),
    )


def _rebuild_question(row: sqlite3.Row) -> QuestionRecord:
    return QuestionRecord(
        id=row["record_id"],
        question=row["question"],
        verdict=Verdict(row["verdict"]),
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _rebuild_guess(row: sqlite3.Row) -> GuessRecord:
    solved_raw = row["solved"]
    if solved_raw not in (0, 1):
        raise ValueError("corrupt solved value")
    return GuessRecord(
        id=row["record_id"],
        guess=row["guess"],
        solved=bool(solved_raw),
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _verify_status_id_index(connection: sqlite3.Connection) -> None:
    index_rows = connection.execute("PRAGMA index_list('puzzles')").fetchall()
    candidate = None
    for row in index_rows:
        if row[1] == "idx_puzzles_status_id":
            candidate = row
            break
    if candidate is None:
        raise SQLiteSchemaError("index idx_puzzles_status_id is missing on puzzles")
    if candidate[2] != 0:
        raise SQLiteSchemaError("index idx_puzzles_status_id must not be UNIQUE")
    if candidate[3] != "c":
        raise SQLiteSchemaError("index idx_puzzles_status_id must be an explicit CREATE INDEX")
    if candidate[4] != 0:
        raise SQLiteSchemaError("index idx_puzzles_status_id must not be partial")
    column_rows = connection.execute(
        "PRAGMA index_info('idx_puzzles_status_id')"
    ).fetchall()
    columns = [row[2] for row in column_rows]
    if columns != ["status", "id"]:
        raise SQLiteSchemaError("index idx_puzzles_status_id must be defined on (status, id)")


def _verify_schema_v1(connection: sqlite3.Connection) -> None:
    for table_name, expected in _EXPECTED_TABLES.items():
        rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        actual = [(row[1], str(row[2]).upper(), row[3], row[5]) for row in rows]
        if actual != list(expected):
            raise SQLiteSchemaError(f"table {table_name} does not match the M3 schema")
    _verify_status_id_index(connection)


def initialize_sqlite_database(*, database_path: str | Path) -> None:
    path = _validate_database_path(database_path)
    with _connection(path) as connection:
        user_version = connection.execute("PRAGMA user_version").fetchone()[0]
        if user_version == 0:
            existing = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name IN (?, ?, ?, ?)",
                _M3_TABLE_NAMES,
            ).fetchall()
            if existing:
                raise SQLiteSchemaError("version 0 database already contains M3 tables")
            connection.execute("BEGIN")
            for statement in _SCHEMA_STATEMENTS:
                connection.execute(statement)
            connection.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
            connection.execute("COMMIT")
            return
        if user_version == 1:
            _verify_schema_v1(connection)
            return
        raise SQLiteSchemaError(f"unsupported user_version {user_version}")


class SQLitePuzzleRepository(PuzzleRepository):
    def __init__(self, *, database_path: str | Path) -> None:
        self._database_path = _validate_database_path(database_path)

    def save(self, *, puzzle: Puzzle) -> None:
        if not isinstance(puzzle, Puzzle):
            # SDD 冻结契约：Port 输入类型错误统一抛 ValueError。
            raise ValueError("puzzle must be a Puzzle instance")  # noqa: TRY004
        with _connection(self._database_path) as connection:
            connection.execute("BEGIN")
            connection.execute(
                "INSERT INTO puzzles"
                " (id, title, surface, solution, key_facts_json, status)"
                " VALUES (?, ?, ?, ?, ?, ?)"
                " ON CONFLICT(id) DO UPDATE SET"
                " title = excluded.title,"
                " surface = excluded.surface,"
                " solution = excluded.solution,"
                " key_facts_json = excluded.key_facts_json,"
                " status = excluded.status",
                (
                    puzzle.id,
                    puzzle.title,
                    puzzle.surface,
                    puzzle.solution,
                    _encode_key_facts(puzzle.key_facts),
                    puzzle.status.value,
                ),
            )
            connection.execute("COMMIT")

    def get(self, *, puzzle_id: str) -> Puzzle | None:
        _require_id(puzzle_id)
        with _connection(self._database_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT id, title, surface, solution, key_facts_json, status"
                " FROM puzzles WHERE id = ?",
                (puzzle_id,),
            ).fetchone()
        if row is None:
            return None
        return _rebuild_puzzle(row)

    def list_enabled(self) -> tuple[Puzzle, ...]:
        with _connection(self._database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT id, title, surface, solution, key_facts_json, status"
                " FROM puzzles WHERE status = ? ORDER BY id ASC",
                (PuzzleStatus.ENABLED.value,),
            ).fetchall()
        return tuple(_rebuild_puzzle(row) for row in rows)


class SQLiteGameSessionRepository(GameSessionRepository):
    def __init__(self, *, database_path: str | Path) -> None:
        self._database_path = _validate_database_path(database_path)

    def save(self, *, session: GameSession) -> None:
        if not isinstance(session, GameSession):
            # SDD 冻结契约：Port 输入类型错误统一抛 ValueError。
            raise ValueError("session must be a GameSession instance")  # noqa: TRY004
        with _connection(self._database_path) as connection:
            connection.execute("BEGIN")
            connection.execute(
                "INSERT INTO game_sessions (id, puzzle_id, status, started_at, ended_at)"
                " VALUES (?, ?, ?, ?, ?)"
                " ON CONFLICT(id) DO UPDATE SET"
                " puzzle_id = excluded.puzzle_id,"
                " status = excluded.status,"
                " started_at = excluded.started_at,"
                " ended_at = excluded.ended_at",
                (
                    session.id,
                    session.puzzle_id,
                    session.status.value,
                    session.started_at.isoformat(timespec="microseconds"),
                    (
                        None
                        if session.ended_at is None
                        else session.ended_at.isoformat(timespec="microseconds")
                    ),
                ),
            )
            connection.execute(
                "DELETE FROM question_records WHERE session_id = ?", (session.id,)
            )
            connection.execute(
                "DELETE FROM guess_records WHERE session_id = ?", (session.id,)
            )
            for position, record in enumerate(session.questions):
                connection.execute(
                    "INSERT INTO question_records"
                    " (session_id, position, record_id, question, verdict, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        session.id,
                        position,
                        record.id,
                        record.question,
                        record.verdict.value,
                        record.created_at.isoformat(timespec="microseconds"),
                    ),
                )
            for position, record in enumerate(session.guesses):
                connection.execute(
                    "INSERT INTO guess_records"
                    " (session_id, position, record_id, guess, solved, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        session.id,
                        position,
                        record.id,
                        record.guess,
                        int(record.solved),
                        record.created_at.isoformat(timespec="microseconds"),
                    ),
                )
            connection.execute("COMMIT")

    def get(self, *, session_id: str) -> GameSession | None:
        _require_id(session_id)
        with _connection(self._database_path) as connection:
            connection.row_factory = sqlite3.Row
            session_row = connection.execute(
                "SELECT id, puzzle_id, status, started_at, ended_at"
                " FROM game_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            if session_row is None:
                return None
            question_rows = connection.execute(
                "SELECT record_id, question, verdict, created_at"
                " FROM question_records WHERE session_id = ? ORDER BY position ASC",
                (session_id,),
            ).fetchall()
            guess_rows = connection.execute(
                "SELECT record_id, guess, solved, created_at"
                " FROM guess_records WHERE session_id = ? ORDER BY position ASC",
                (session_id,),
            ).fetchall()
        return GameSession(
            id=session_row["id"],
            puzzle_id=session_row["puzzle_id"],
            status=GameStatus(session_row["status"]),
            started_at=datetime.fromisoformat(session_row["started_at"]),
            ended_at=(
                None
                if session_row["ended_at"] is None
                else datetime.fromisoformat(session_row["ended_at"])
            ),
            questions=tuple(_rebuild_question(row) for row in question_rows),
            guesses=tuple(_rebuild_guess(row) for row in guess_rows),
        )
