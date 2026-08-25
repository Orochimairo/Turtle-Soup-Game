import sqlite3
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from turtle_soup.domain import (
    GameSession,
    GameStatus,
    GuessRecord,
    Puzzle,
    PuzzleStatus,
    QuestionRecord,
    Verdict,
)
from turtle_soup.infrastructure import (
    SQLiteGameSessionRepository,
    SQLitePuzzleRepository,
    SQLiteSchemaError,
    initialize_sqlite_database,
)

T0 = datetime(2026, 1, 1, 8, 0, 0, tzinfo=UTC)
TZ8 = timezone(timedelta(hours=8))


def make_puzzle(**overrides):
    fields = {
        "id": "puzzle-1",
        "title": "经典海龟汤",
        "surface": "一个人走进餐厅点了一碗海龟汤。",
        "solution": "他曾在海难中靠喝汤维生，汤的味道让他想起往事。",
        "key_facts": ("他经历过海难", "他想起往事"),
        "status": PuzzleStatus.ENABLED,
    }
    fields.update(overrides)
    return Puzzle(**fields)


def make_question(**overrides):
    fields = {
        "id": "q-1",
        "question": "他点的是海龟汤吗？",
        "verdict": Verdict.YES,
        "created_at": T0 + timedelta(minutes=1),
    }
    fields.update(overrides)
    return QuestionRecord(**fields)


def make_guess(**overrides):
    fields = {
        "id": "g-1",
        "guess": "他曾在海难中靠喝汤维生，所以现在想喝那碗汤。",
        "solved": False,
        "created_at": T0 + timedelta(minutes=2),
    }
    fields.update(overrides)
    return GuessRecord(**fields)


def make_session(**overrides):
    fields = {
        "id": "session-1",
        "puzzle_id": "puzzle-1",
        "status": GameStatus.PLAYING,
        "started_at": T0,
        "ended_at": None,
    }
    fields.update(overrides)
    return GameSession(**fields)


def init_db(tmp_path: Path, name: str = "test.sqlite3") -> Path:
    db = tmp_path / name
    initialize_sqlite_database(database_path=db)
    return db


def raw_connection(db: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db)
    connection.isolation_level = None
    return connection


def table_names(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return [row[0] for row in rows]


PUZZLES_DDL = (
    "CREATE TABLE puzzles ("
    " id TEXT NOT NULL PRIMARY KEY,"
    " title TEXT NOT NULL,"
    " surface TEXT NOT NULL,"
    " solution TEXT NOT NULL,"
    " key_facts_json TEXT NOT NULL,"
    " status TEXT NOT NULL CHECK (status IN ('ENABLED', 'DISABLED')))"
)

SESSIONS_DDL = (
    "CREATE TABLE game_sessions ("
    " id TEXT NOT NULL PRIMARY KEY,"
    " puzzle_id TEXT NOT NULL REFERENCES puzzles(id),"
    " status TEXT NOT NULL CHECK (status IN ('PLAYING', 'SOLVED', 'ABANDONED')),"
    " started_at TEXT NOT NULL,"
    " ended_at TEXT,"
    " CHECK ((status = 'PLAYING' AND ended_at IS NULL)"
    " OR (status IN ('SOLVED', 'ABANDONED') AND ended_at IS NOT NULL)))"
)

QUESTIONS_DDL = (
    "CREATE TABLE question_records ("
    " session_id TEXT NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,"
    " position INTEGER NOT NULL CHECK (position >= 0),"
    " record_id TEXT NOT NULL,"
    " question TEXT NOT NULL,"
    " verdict TEXT NOT NULL CHECK (verdict IN ('YES', 'NO', 'IRRELEVANT')),"
    " created_at TEXT NOT NULL,"
    " PRIMARY KEY (session_id, record_id),"
    " UNIQUE (session_id, position))"
)

GUESSES_DDL = (
    "CREATE TABLE guess_records ("
    " session_id TEXT NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,"
    " position INTEGER NOT NULL CHECK (position >= 0),"
    " record_id TEXT NOT NULL,"
    " guess TEXT NOT NULL,"
    " solved INTEGER NOT NULL CHECK (solved IN (0, 1)),"
    " created_at TEXT NOT NULL,"
    " PRIMARY KEY (session_id, record_id),"
    " UNIQUE (session_id, position))"
)

INDEX_DDL = "CREATE INDEX idx_puzzles_status_id ON puzzles(status, id)"


def create_manual_v1(
    db: Path,
    *,
    puzzles: str = PUZZLES_DDL,
    sessions: str = SESSIONS_DDL,
    questions: str = QUESTIONS_DDL,
    guesses: str = GUESSES_DDL,
    with_index: bool = True,
    user_version: int = 1,
) -> None:
    with raw_connection(db) as connection:
        for statement in (puzzles, sessions, questions, guesses):
            connection.execute(statement)
        if with_index:
            connection.execute(INDEX_DDL)
        connection.execute(f"PRAGMA user_version = {user_version}")


class TestInitializeSchema:
    def test_new_database_reaches_version_one(self, tmp_path):
        db = tmp_path / "fresh.sqlite3"
        initialize_sqlite_database(database_path=db)
        with raw_connection(db) as connection:
            assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
            names = table_names(connection)
        assert set(names) == {
            "puzzles",
            "game_sessions",
            "question_records",
            "guess_records",
        }

    def test_new_database_has_required_index(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            indexes = [row[1] for row in connection.execute("PRAGMA index_list('puzzles')")]
        assert "idx_puzzles_status_id" in indexes

    def test_repeated_initialization_preserves_data(self, tmp_path):
        db = init_db(tmp_path)
        puzzle_repo = SQLitePuzzleRepository(database_path=db)
        puzzle_repo.save(puzzle=make_puzzle())
        initialize_sqlite_database(database_path=db)
        assert puzzle_repo.get(puzzle_id="puzzle-1") == make_puzzle()
        with raw_connection(db) as connection:
            assert connection.execute("SELECT COUNT(*) FROM puzzles").fetchone()[0] == 1

    def test_version_zero_partial_schema_fails_without_repair(self, tmp_path):
        db = tmp_path / "partial.sqlite3"
        with raw_connection(db) as connection:
            connection.execute("CREATE TABLE question_records (x TEXT)")
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)
        with raw_connection(db) as connection:
            assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
            assert table_names(connection) == ["question_records"]

    def test_version_one_missing_table_fails(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("DROP TABLE question_records")
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_version_one_extra_column_fails(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("ALTER TABLE puzzles ADD COLUMN extra TEXT")
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_version_one_missing_column_fails(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("ALTER TABLE puzzles DROP COLUMN surface")
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_version_one_missing_index_fails(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("DROP INDEX idx_puzzles_status_id")
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_wrong_column_index_rejected_without_repair(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("DROP INDEX idx_puzzles_status_id")
            connection.execute("CREATE INDEX idx_puzzles_status_id ON puzzles(title)")
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)
        with raw_connection(db) as connection:
            columns = [
                row[2] for row in connection.execute("PRAGMA index_info('idx_puzzles_status_id')")
            ]
        assert columns == ["title"]

    def test_reversed_column_order_index_rejected_without_repair(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("DROP INDEX idx_puzzles_status_id")
            connection.execute("CREATE INDEX idx_puzzles_status_id ON puzzles(id, status)")
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)
        with raw_connection(db) as connection:
            columns = [
                row[2] for row in connection.execute("PRAGMA index_info('idx_puzzles_status_id')")
            ]
        assert columns == ["id", "status"]

    @pytest.mark.parametrize(
        "column_list",
        [
            "status",
            "status, title, id",
        ],
    )
    def test_index_column_count_mismatch_rejected(self, tmp_path, column_list):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("DROP INDEX idx_puzzles_status_id")
            connection.execute(
                f"CREATE INDEX idx_puzzles_status_id ON puzzles({column_list})"
            )
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_unique_index_with_expected_name_rejected(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("DROP INDEX idx_puzzles_status_id")
            connection.execute(
                "CREATE UNIQUE INDEX idx_puzzles_status_id ON puzzles(status, id)"
            )
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_partial_index_with_expected_name_rejected(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("DROP INDEX idx_puzzles_status_id")
            connection.execute(
                "CREATE INDEX idx_puzzles_status_id ON puzzles(status, id)"
                " WHERE status = 'ENABLED'"
            )
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_same_named_index_on_other_table_rejected(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("DROP INDEX idx_puzzles_status_id")
            connection.execute(
                "CREATE INDEX idx_puzzles_status_id ON game_sessions(status)"
            )
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_version_one_declared_type_mismatch_fails(self, tmp_path):
        db = tmp_path / "typed.sqlite3"
        create_manual_v1(db, puzzles=PUZZLES_DDL.replace("title TEXT NOT NULL", "title INTEGER NOT NULL"))
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_version_one_not_null_mismatch_fails(self, tmp_path):
        db = tmp_path / "nullable.sqlite3"
        create_manual_v1(db, sessions=SESSIONS_DDL.replace("puzzle_id TEXT NOT NULL", "puzzle_id TEXT"))
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_version_one_pk_ordinal_mismatch_fails(self, tmp_path):
        db = tmp_path / "pk.sqlite3"
        create_manual_v1(
            db,
            questions=QUESTIONS_DDL.replace(
                "PRIMARY KEY (session_id, record_id)", "PRIMARY KEY (record_id, session_id)"
            ),
        )
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)

    def test_non_m3_tables_are_preserved(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY, note TEXT)")
            connection.execute("INSERT INTO unrelated (note) VALUES ('keep me')")
        initialize_sqlite_database(database_path=db)
        with raw_connection(db) as connection:
            rows = connection.execute("SELECT note FROM unrelated").fetchall()
        assert rows == [("keep me",)]

    def test_other_user_versions_fail(self, tmp_path):
        db = tmp_path / "future.sqlite3"
        with raw_connection(db) as connection:
            connection.execute("PRAGMA user_version = 2")
        with pytest.raises(SQLiteSchemaError):
            initialize_sqlite_database(database_path=db)


class TestSchemaConstraints:
    def test_puzzles_id_null_fails(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection, pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO puzzles (id, title, surface, solution, key_facts_json, status)"
                " VALUES (NULL, 't', 's', 'sol', '[]', 'ENABLED')"
            )

    def test_game_sessions_id_null_fails(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute(
                "INSERT INTO puzzles (id, title, surface, solution, key_facts_json, status)"
                " VALUES ('puzzle-1', 't', 's', 'sol', '[]', 'ENABLED')"
            )
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO game_sessions (id, puzzle_id, status, started_at, ended_at)"
                    " VALUES (NULL, 'puzzle-1', 'PLAYING', '2026-01-01T08:00:00+00:00', NULL)"
                )

    def test_question_records_session_id_null_fails(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute(
                "INSERT INTO puzzles (id, title, surface, solution, key_facts_json, status)"
                " VALUES ('puzzle-1', 't', 's', 'sol', '[]', 'ENABLED')"
            )
            connection.execute(
                "INSERT INTO game_sessions (id, puzzle_id, status, started_at, ended_at)"
                " VALUES ('s-1', 'puzzle-1', 'PLAYING', '2026-01-01T08:00:00+00:00', NULL)"
            )
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO question_records"
                    " (session_id, position, record_id, question, verdict, created_at)"
                    " VALUES (NULL, 0, 'q-1', 'q', 'YES', '2026-01-01T08:01:00+00:00')"
                )

    def test_guess_records_session_id_null_fails(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute(
                "INSERT INTO puzzles (id, title, surface, solution, key_facts_json, status)"
                " VALUES ('puzzle-1', 't', 's', 'sol', '[]', 'ENABLED')"
            )
            connection.execute(
                "INSERT INTO game_sessions (id, puzzle_id, status, started_at, ended_at)"
                " VALUES ('s-1', 'puzzle-1', 'PLAYING', '2026-01-01T08:00:00+00:00', NULL)"
            )
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO guess_records"
                    " (session_id, position, record_id, guess, solved, created_at)"
                    " VALUES (NULL, 0, 'g-1', 'g', 0, '2026-01-01T08:02:00+00:00')"
                )

    def test_foreign_key_rejects_unknown_puzzle(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO game_sessions (id, puzzle_id, status, started_at, ended_at)"
                    " VALUES ('s-1', 'missing', 'PLAYING', '2026-01-01T08:00:00+00:00', NULL)"
                )

    def test_check_constraints(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute(
                "INSERT INTO puzzles (id, title, surface, solution, key_facts_json, status)"
                " VALUES ('puzzle-1', 't', 's', 'sol', '[]', 'ENABLED')"
            )
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO puzzles (id, title, surface, solution, key_facts_json, status)"
                    " VALUES ('puzzle-2', 't', 's', 'sol', '[]', 'WEIRD')"
                )
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO game_sessions (id, puzzle_id, status, started_at, ended_at)"
                    " VALUES ('s-1', 'puzzle-1', 'WEIRD', '2026-01-01T08:00:00+00:00', NULL)"
                )
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO game_sessions (id, puzzle_id, status, started_at, ended_at)"
                    " VALUES ('s-1', 'puzzle-1', 'PLAYING',"
                    " '2026-01-01T08:00:00+00:00', '2026-01-01T08:05:00+00:00')"
                )
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO game_sessions (id, puzzle_id, status, started_at, ended_at)"
                    " VALUES ('s-1', 'puzzle-1', 'ABANDONED', '2026-01-01T08:00:00+00:00', NULL)"
                )

    def test_unique_and_position_checks(self, tmp_path):
        db = init_db(tmp_path)
        with raw_connection(db) as connection:
            connection.execute(
                "INSERT INTO puzzles (id, title, surface, solution, key_facts_json, status)"
                " VALUES ('puzzle-1', 't', 's', 'sol', '[]', 'ENABLED')"
            )
            connection.execute(
                "INSERT INTO game_sessions (id, puzzle_id, status, started_at, ended_at)"
                " VALUES ('s-1', 'puzzle-1', 'PLAYING', '2026-01-01T08:00:00+00:00', NULL)"
            )
            base = (
                "INSERT INTO question_records"
                " (session_id, position, record_id, question, verdict, created_at)"
                " VALUES ('s-1', ?, ?, 'q', 'YES', '2026-01-01T08:01:00+00:00')"
            )
            connection.execute(base, (0, "q-1"))
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(base, (0, "q-2"))
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(base, (1, "q-1"))
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(base, (-1, "q-3"))
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO question_records"
                    " (session_id, position, record_id, question, verdict, created_at)"
                    " VALUES ('s-1', 2, 'q-4', 'q', 'MAYBE', '2026-01-01T08:04:00+00:00')"
                )
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO guess_records"
                    " (session_id, position, record_id, guess, solved, created_at)"
                    " VALUES ('s-1', 0, 'g-1', 'g', 2, '2026-01-01T08:02:00+00:00')"
                )

    def test_foreign_keys_active_in_repository_connection(self, tmp_path):
        db = init_db(tmp_path)
        session_repo = SQLiteGameSessionRepository(database_path=db)
        with pytest.raises(sqlite3.Error):
            session_repo.save(session=make_session())
        with raw_connection(db) as connection:
            assert connection.execute("SELECT COUNT(*) FROM game_sessions").fetchone()[0] == 0


class TestPathValidation:
    @pytest.mark.parametrize("value", [5, None, b"db.sqlite3", ["db.sqlite3"]])
    def test_initialize_rejects_wrong_types(self, tmp_path, value):
        with pytest.raises(ValueError):
            initialize_sqlite_database(database_path=value)

    @pytest.mark.parametrize("value", ["", "   "])
    def test_initialize_rejects_blank_strings(self, tmp_path, value):
        with pytest.raises(ValueError):
            initialize_sqlite_database(database_path=value)

    @pytest.mark.parametrize("value", [":memory:", "file:test.sqlite3", "file:///tmp/x.sqlite3"])
    def test_initialize_rejects_memory_and_uris(self, tmp_path, value):
        with pytest.raises(ValueError):
            initialize_sqlite_database(database_path=value)

    def test_initialize_rejects_missing_parent(self, tmp_path):
        missing = tmp_path / "no-such-dir" / "db.sqlite3"
        with pytest.raises(ValueError):
            initialize_sqlite_database(database_path=missing)

    def test_initialize_rejects_directory_target(self, tmp_path):
        with pytest.raises(ValueError):
            initialize_sqlite_database(database_path=tmp_path)

    def test_initialize_accepts_str_and_path(self, tmp_path):
        as_str = tmp_path / "str.sqlite3"
        as_path = tmp_path / "path.sqlite3"
        initialize_sqlite_database(database_path=str(as_str))
        initialize_sqlite_database(database_path=as_path)
        assert as_str.exists()
        assert as_path.exists()

    @pytest.mark.parametrize("repo_class", [SQLitePuzzleRepository, SQLiteGameSessionRepository])
    @pytest.mark.parametrize("value", [5, None, b"db.sqlite3", "", "   ", ":memory:", "file:x.sqlite3"])
    def test_constructors_reject_invalid_paths(self, tmp_path, repo_class, value):
        with pytest.raises(ValueError):
            repo_class(database_path=value)

    @pytest.mark.parametrize("repo_class", [SQLitePuzzleRepository, SQLiteGameSessionRepository])
    def test_constructors_reject_missing_parent_and_directory(self, tmp_path, repo_class):
        with pytest.raises(ValueError):
            repo_class(database_path=tmp_path / "no-such-dir" / "db.sqlite3")
        with pytest.raises(ValueError):
            repo_class(database_path=tmp_path)

    @pytest.mark.parametrize("repo_class", [SQLitePuzzleRepository, SQLiteGameSessionRepository])
    def test_constructor_creates_no_file(self, tmp_path, repo_class):
        db = tmp_path / "not-created.sqlite3"
        repo_class(database_path=db)
        assert not db.exists()

    @pytest.mark.parametrize("repo_class", [SQLitePuzzleRepository, SQLiteGameSessionRepository])
    def test_constructor_does_not_check_schema(self, tmp_path, repo_class):
        db = tmp_path / "future.sqlite3"
        with raw_connection(db) as connection:
            connection.execute("PRAGMA user_version = 2")
        repo_class(database_path=db)

    @pytest.mark.parametrize("repo_class", [SQLitePuzzleRepository, SQLiteGameSessionRepository])
    def test_first_operation_on_uninitialized_database_fails(self, tmp_path, repo_class):
        db = tmp_path / "bare.sqlite3"
        repo = repo_class(database_path=db)
        with pytest.raises(sqlite3.Error):
            repo.get(**{("puzzle_id" if repo_class is SQLitePuzzleRepository else "session_id"): "x"})


class TestPuzzleRepository:
    def test_roundtrip_preserves_unicode_and_fact_order(self, tmp_path):
        db = init_db(tmp_path)
        repo = SQLitePuzzleRepository(database_path=db)
        puzzle = make_puzzle(
            id="puzzle-🐢-1",
            title="海龟汤 · 经典 🐢",
            surface="一 个 人 走 进 餐 厅",
            solution="海难 与 汤 的 味 道",
            key_facts=("事实乙", "事实甲", "π ≈ 3.14159"),
            status=PuzzleStatus.ENABLED,
        )
        repo.save(puzzle=puzzle)
        loaded = repo.get(puzzle_id="puzzle-🐢-1")
        assert loaded == puzzle
        assert loaded.key_facts == ("事实乙", "事实甲", "π ≈ 3.14159")

    def test_save_overwrites_single_row(self, tmp_path):
        db = init_db(tmp_path)
        repo = SQLitePuzzleRepository(database_path=db)
        repo.save(puzzle=make_puzzle())
        changed = make_puzzle(
            title="改过的标题",
            surface="改过的题面",
            solution="改过的题底",
            key_facts=("新事实",),
            status=PuzzleStatus.DISABLED,
        )
        repo.save(puzzle=changed)
        assert repo.get(puzzle_id="puzzle-1") == changed
        with raw_connection(db) as connection:
            assert connection.execute("SELECT COUNT(*) FROM puzzles").fetchone()[0] == 1

    def test_get_missing_returns_none(self, tmp_path):
        db = init_db(tmp_path)
        assert SQLitePuzzleRepository(database_path=db).get(puzzle_id="missing") is None

    @pytest.mark.parametrize("value", [123, "", "   "])
    def test_get_rejects_invalid_ids(self, tmp_path, value):
        db = init_db(tmp_path)
        with pytest.raises(ValueError):
            SQLitePuzzleRepository(database_path=db).get(puzzle_id=value)

    def test_save_rejects_non_puzzle(self, tmp_path):
        db = init_db(tmp_path)
        repo = SQLitePuzzleRepository(database_path=db)
        with pytest.raises(ValueError):
            repo.save(puzzle=make_question())
        with pytest.raises(ValueError):
            repo.save(puzzle={"id": "x"})
        with raw_connection(db) as connection:
            assert connection.execute("SELECT COUNT(*) FROM puzzles").fetchone()[0] == 0

    def test_list_enabled_excludes_disabled_and_sorts_by_id(self, tmp_path):
        db = init_db(tmp_path)
        repo = SQLitePuzzleRepository(database_path=db)
        repo.save(puzzle=make_puzzle(id="b", status=PuzzleStatus.ENABLED))
        repo.save(puzzle=make_puzzle(id="c", status=PuzzleStatus.DISABLED))
        repo.save(puzzle=make_puzzle(id="a", status=PuzzleStatus.ENABLED))
        result = repo.list_enabled()
        assert type(result) is tuple
        assert [p.id for p in result] == ["a", "b"]
        assert all(p.status is PuzzleStatus.ENABLED for p in result)

    def test_list_enabled_empty_database(self, tmp_path):
        db = init_db(tmp_path)
        assert SQLitePuzzleRepository(database_path=db).list_enabled() == ()

    def test_data_survives_across_instances(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        assert SQLitePuzzleRepository(database_path=db).get(puzzle_id="puzzle-1") == make_puzzle()


class TestGameSessionRepository:
    def test_playing_roundtrip_with_questions(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        session = make_session(
            questions=(
                make_question(id="q-1"),
                make_question(id="q-2", question="第二问", verdict=Verdict.NO),
            ),
        )
        repo = SQLiteGameSessionRepository(database_path=db)
        repo.save(session=session)
        assert repo.get(session_id="session-1") == session

    def test_solved_roundtrip(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        solved_guess = make_guess(
            id="g-2", solved=True, created_at=T0 + timedelta(minutes=10)
        )
        session = make_session(
            status=GameStatus.SOLVED,
            ended_at=solved_guess.created_at,
            questions=(make_question(id="q-1"),),
            guesses=(make_guess(id="g-1"), solved_guess),
        )
        repo = SQLiteGameSessionRepository(database_path=db)
        repo.save(session=session)
        assert repo.get(session_id="session-1") == session

    def test_abandoned_roundtrip(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        session = make_session(
            status=GameStatus.ABANDONED,
            ended_at=T0 + timedelta(minutes=5),
            questions=(make_question(id="q-1"),),
            guesses=(make_guess(id="g-1"),),
        )
        repo = SQLiteGameSessionRepository(database_path=db)
        repo.save(session=session)
        assert repo.get(session_id="session-1") == session

    def test_roundtrip_preserves_utc_offset(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        question = make_question(id="q-1", created_at=datetime(2026, 1, 1, 16, 0, 0, tzinfo=TZ8))
        session = make_session(questions=(question,))
        repo = SQLiteGameSessionRepository(database_path=db)
        repo.save(session=session)
        loaded = repo.get(session_id="session-1")
        assert loaded.questions[0].created_at == question.created_at
        assert loaded.questions[0].created_at.utcoffset() == timedelta(hours=8)

    def test_question_and_guess_order_preserved(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        session = make_session(
            questions=(
                make_question(id="q-1"),
                make_question(id="q-2", created_at=T0 + timedelta(minutes=3)),
                make_question(id="q-3", created_at=T0 + timedelta(minutes=5)),
            ),
            guesses=(
                make_guess(id="g-1"),
                make_guess(id="g-2", created_at=T0 + timedelta(minutes=4)),
                make_guess(id="g-3", created_at=T0 + timedelta(minutes=6)),
            ),
        )
        repo = SQLiteGameSessionRepository(database_path=db)
        repo.save(session=session)
        loaded = repo.get(session_id="session-1")
        assert [r.id for r in loaded.questions] == ["q-1", "q-2", "q-3"]
        assert [r.id for r in loaded.guesses] == ["g-1", "g-2", "g-3"]

    def test_overwrite_removes_stale_records(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        repo = SQLiteGameSessionRepository(database_path=db)
        old = make_session(
            questions=(
                make_question(id="q-1"),
                make_question(id="q-2", created_at=T0 + timedelta(minutes=3)),
            ),
            guesses=(make_guess(id="g-1"),),
        )
        repo.save(session=old)
        new = make_session(questions=(make_question(id="q-new"),))
        repo.save(session=new)
        assert repo.get(session_id="session-1") == new
        with raw_connection(db) as connection:
            questions = connection.execute(
                "SELECT record_id FROM question_records WHERE session_id = 'session-1'"
            ).fetchall()
            guesses = connection.execute(
                "SELECT record_id FROM guess_records WHERE session_id = 'session-1'"
            ).fetchall()
        assert questions == [("q-new",)]
        assert guesses == []

    def test_get_missing_returns_none(self, tmp_path):
        db = init_db(tmp_path)
        repo = SQLiteGameSessionRepository(database_path=db)
        assert repo.get(session_id="missing") is None

    @pytest.mark.parametrize("value", [123, "", "   "])
    def test_get_rejects_invalid_ids(self, tmp_path, value):
        db = init_db(tmp_path)
        with pytest.raises(ValueError):
            SQLiteGameSessionRepository(database_path=db).get(session_id=value)

    def test_save_rejects_non_session(self, tmp_path):
        db = init_db(tmp_path)
        repo = SQLiteGameSessionRepository(database_path=db)
        with pytest.raises(ValueError):
            repo.save(session=make_puzzle())
        with pytest.raises(ValueError):
            repo.save(session={"id": "x"})

    def test_save_with_unknown_puzzle_leaves_no_partial_data(self, tmp_path):
        db = init_db(tmp_path)
        repo = SQLiteGameSessionRepository(database_path=db)
        with pytest.raises(sqlite3.Error):
            repo.save(session=make_session())
        with raw_connection(db) as connection:
            assert connection.execute("SELECT COUNT(*) FROM game_sessions").fetchone()[0] == 0
            assert connection.execute("SELECT COUNT(*) FROM question_records").fetchone()[0] == 0
            assert connection.execute("SELECT COUNT(*) FROM guess_records").fetchone()[0] == 0

    def test_save_rollback_keeps_old_aggregate(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        repo = SQLiteGameSessionRepository(database_path=db)
        old = make_session(
            status=GameStatus.ABANDONED,
            ended_at=T0 + timedelta(minutes=5),
            questions=(make_question(id="q-1"),),
            guesses=(make_guess(id="g-1"),),
        )
        repo.save(session=old)
        with raw_connection(db) as connection:
            connection.execute(
                "CREATE TRIGGER block_questions"
                " BEFORE INSERT ON question_records"
                " BEGIN SELECT RAISE(ABORT, 'forced failure'); END"
            )
        new = make_session(
            status=GameStatus.ABANDONED,
            ended_at=T0 + timedelta(minutes=6),
            questions=(
                make_question(id="q-1", question="被改写的问题"),
                make_question(id="q-2", created_at=T0 + timedelta(minutes=3)),
            ),
            guesses=(),
        )
        with pytest.raises(sqlite3.Error):
            repo.save(session=new)
        assert repo.get(session_id="session-1") == old
        with raw_connection(db) as connection:
            questions = connection.execute(
                "SELECT record_id, question FROM question_records WHERE session_id = 'session-1'"
            ).fetchall()
            guesses = connection.execute(
                "SELECT record_id FROM guess_records WHERE session_id = 'session-1'"
            ).fetchall()
        assert questions == [("q-1", "他点的是海龟汤吗？")]
        assert guesses == [("g-1",)]


class TestDataCorruption:
    def setup_puzzle_row(self, tmp_path, **column_overrides):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        with raw_connection(db) as connection:
            connection.execute("PRAGMA ignore_check_constraints = ON")
            assignments = ", ".join(f"{column} = ?" for column in column_overrides)
            connection.execute(
                f"UPDATE puzzles SET {assignments} WHERE id = 'puzzle-1'",
                tuple(column_overrides.values()),
            )
            connection.execute("PRAGMA ignore_check_constraints = OFF")
        return db

    def test_puzzle_invalid_json_fails_read(self, tmp_path):
        db = self.setup_puzzle_row(tmp_path, key_facts_json="not json")
        with pytest.raises(ValueError):
            SQLitePuzzleRepository(database_path=db).get(puzzle_id="puzzle-1")

    def test_puzzle_non_array_json_fails_read(self, tmp_path):
        db = self.setup_puzzle_row(tmp_path, key_facts_json='{"fact": 1}')
        with pytest.raises(ValueError):
            SQLitePuzzleRepository(database_path=db).get(puzzle_id="puzzle-1")

    def test_puzzle_empty_facts_fail_read(self, tmp_path):
        db = self.setup_puzzle_row(tmp_path, key_facts_json="[]")
        with pytest.raises(ValueError):
            SQLitePuzzleRepository(database_path=db).get(puzzle_id="puzzle-1")

    def test_puzzle_unknown_status_fails_read(self, tmp_path):
        db = self.setup_puzzle_row(tmp_path, status="WEIRD")
        with pytest.raises(ValueError):
            SQLitePuzzleRepository(database_path=db).get(puzzle_id="puzzle-1")

    def test_session_unknown_status_fails_read(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        SQLiteGameSessionRepository(database_path=db).save(session=make_session())
        with raw_connection(db) as connection:
            connection.execute("PRAGMA ignore_check_constraints = ON")
            connection.execute("UPDATE game_sessions SET status = 'WEIRD' WHERE id = 'session-1'")
            connection.execute("PRAGMA ignore_check_constraints = OFF")
        with pytest.raises(ValueError):
            SQLiteGameSessionRepository(database_path=db).get(session_id="session-1")

    def test_session_invalid_started_at_fails_read(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        SQLiteGameSessionRepository(database_path=db).save(session=make_session())
        with raw_connection(db) as connection:
            connection.execute(
                "UPDATE game_sessions SET started_at = 'not-a-time' WHERE id = 'session-1'"
            )
        with pytest.raises(ValueError):
            SQLiteGameSessionRepository(database_path=db).get(session_id="session-1")

    def test_session_invalid_ended_at_fails_read(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        session = make_session(
            status=GameStatus.ABANDONED,
            ended_at=T0 + timedelta(minutes=5),
            questions=(make_question(id="q-1"),),
        )
        SQLiteGameSessionRepository(database_path=db).save(session=session)
        with raw_connection(db) as connection:
            connection.execute(
                "UPDATE game_sessions SET ended_at = 'not-a-time' WHERE id = 'session-1'"
            )
        with pytest.raises(ValueError):
            SQLiteGameSessionRepository(database_path=db).get(session_id="session-1")

    def test_question_unknown_verdict_fails_read(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        SQLiteGameSessionRepository(database_path=db).save(
            session=make_session(questions=(make_question(id="q-1"),))
        )
        with raw_connection(db) as connection:
            connection.execute("PRAGMA ignore_check_constraints = ON")
            connection.execute(
                "UPDATE question_records SET verdict = 'MAYBE' WHERE session_id = 'session-1'"
            )
            connection.execute("PRAGMA ignore_check_constraints = OFF")
        with pytest.raises(ValueError):
            SQLiteGameSessionRepository(database_path=db).get(session_id="session-1")

    def test_guess_invalid_solved_fails_read(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        SQLiteGameSessionRepository(database_path=db).save(
            session=make_session(guesses=(make_guess(id="g-1"),))
        )
        with raw_connection(db) as connection:
            connection.execute("PRAGMA ignore_check_constraints = ON")
            connection.execute(
                "UPDATE guess_records SET solved = 5 WHERE session_id = 'session-1'"
            )
            connection.execute("PRAGMA ignore_check_constraints = OFF")
        with pytest.raises(ValueError):
            SQLiteGameSessionRepository(database_path=db).get(session_id="session-1")

    def test_aggregate_violation_solved_with_unsolved_last_guess_fails_read(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        SQLiteGameSessionRepository(database_path=db).save(
            session=make_session(guesses=(make_guess(id="g-1"),))
        )
        with raw_connection(db) as connection:
            connection.execute(
                "UPDATE game_sessions SET status = 'SOLVED',"
                " ended_at = '2026-01-01T08:10:00+00:00' WHERE id = 'session-1'"
            )
        with pytest.raises(ValueError):
            SQLiteGameSessionRepository(database_path=db).get(session_id="session-1")

    def test_aggregate_violation_playing_with_ended_at_fails_read(self, tmp_path):
        db = init_db(tmp_path)
        SQLitePuzzleRepository(database_path=db).save(puzzle=make_puzzle())
        SQLiteGameSessionRepository(database_path=db).save(session=make_session())
        with raw_connection(db) as connection:
            connection.execute("PRAGMA ignore_check_constraints = ON")
            connection.execute(
                "UPDATE game_sessions SET ended_at = '2026-01-01T08:10:00+00:00'"
                " WHERE id = 'session-1'"
            )
            connection.execute("PRAGMA ignore_check_constraints = OFF")
        with pytest.raises(ValueError):
            SQLiteGameSessionRepository(database_path=db).get(session_id="session-1")
