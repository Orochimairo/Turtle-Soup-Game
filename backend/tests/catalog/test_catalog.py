import builtins
import inspect
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from turtle_soup.catalog import (
    PuzzleCatalogError,
    import_puzzle_catalog,
    load_puzzle_catalog,
    parse_puzzle_catalog_document,
)
from turtle_soup.domain import PuzzleStatus
from turtle_soup.infrastructure import (
    SQLitePuzzleRepository,
    initialize_sqlite_database,
)

SRC_DIR = Path(__file__).resolve().parents[2] / "src"

SYNTHETIC_SECRET = "SYNTHETIC-SECRET-SOLUTION-0x9F2A"
SYNTHETIC_FACT = "SYNTHETIC-SECRET-FACT-0x3C1D"


def make_puzzle_dict(index: int, *, status: str = "ENABLED") -> dict:
    return {
        "id": f"ts-{index:04d}",
        "title": f"合成题目 {index}",
        "surface": f"这是第 {index} 道合成题目的题面。",
        "solution": f"这是第 {index} 道合成题目的完整题底，用于自动化测试。",
        "key_facts": [f"合成事实 A-{index}", f"合成事实 B-{index}"],
        "status": status,
        "provenance": {
            "source_kind": "ORIGINAL",
            "source_reference": f"synthetic-source-{index}",
            "adaptation_note": None,
        },
    }


def make_catalog_dict(count: int = 8, enabled_count: int = 8) -> dict:
    puzzles = []
    for index in range(1, count + 1):
        status = "ENABLED" if index <= enabled_count else "DISABLED"
        puzzles.append(make_puzzle_dict(index, status=status))
    return {"catalog_version": 1, "puzzles": puzzles}


def encode(document) -> bytes:
    return json.dumps(document, ensure_ascii=False).encode("utf-8") + b"\n"


def write_catalog(tmp_path: Path, document=None, *, count: int = 8, name: str = "catalog.json") -> Path:
    doc = make_catalog_dict(count=count) if document is None else document
    path = tmp_path / name
    path.write_bytes(encode(doc))
    return path


def init_db(tmp_path: Path, name: str = "db.sqlite3") -> Path:
    db = tmp_path / name
    initialize_sqlite_database(database_path=db)
    return db


def run_cli(catalog_path, database_path) -> subprocess.CompletedProcess:
    args = [sys.executable, "-m", "turtle_soup.catalog"]
    if catalog_path is not None:
        args += ["--catalog-path", str(catalog_path)]
    if database_path is not None:
        args += ["--database-path", str(database_path)]
    return subprocess.run(args, cwd=str(SRC_DIR), capture_output=True, text=True, check=False)


class TestPublicApi:
    def test_four_names_importable(self):
        for name in (
            "PuzzleCatalogError",
            "parse_puzzle_catalog_document",
            "load_puzzle_catalog",
            "import_puzzle_catalog",
        ):
            assert hasattr(sys.modules["turtle_soup.catalog"], name)

    def test_all_exact(self):
        from turtle_soup import catalog

        assert catalog.__all__ == [
            "PuzzleCatalogError",
            "import_puzzle_catalog",
            "load_puzzle_catalog",
            "parse_puzzle_catalog_document",
        ]

    def test_error_is_value_error(self):
        assert issubclass(PuzzleCatalogError, ValueError)

    def test_keyword_only_signatures(self):
        for func in (
            parse_puzzle_catalog_document,
            load_puzzle_catalog,
            import_puzzle_catalog,
        ):
            params = inspect.signature(func).parameters.values()
            assert params
            assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in params)


class TestStrictParsing:
    def test_valid_document_returns_ordered_tuple(self):
        result = parse_puzzle_catalog_document(document=encode(make_catalog_dict()))
        assert type(result) is tuple
        assert [p.id for p in result] == [f"ts-{i:04d}" for i in range(1, 9)]
        assert all(p.status is PuzzleStatus.ENABLED for p in result)
        first = result[0]
        assert first.title == "合成题目 1"
        assert first.surface == "这是第 1 道合成题目的题面。"
        assert first.solution == "这是第 1 道合成题目的完整题底，用于自动化测试。"
        assert first.key_facts == ("合成事实 A-1", "合成事实 B-1")
        assert not hasattr(first, "provenance")

    def test_valid_unicode(self):
        doc = make_catalog_dict(count=8)
        doc["puzzles"][0]["title"] = "合成题目·中文🐢"
        doc["puzzles"][0]["key_facts"] = ["事实甲 🐢", "π≈3.14"]
        result = parse_puzzle_catalog_document(document=encode(doc))
        assert result[0].title == "合成题目·中文🐢"
        assert result[0].key_facts == ("事实甲 🐢", "π≈3.14")

    def test_exactly_eight_enabled_passes(self):
        doc = make_catalog_dict(count=8, enabled_count=8)
        assert len(parse_puzzle_catalog_document(document=encode(doc))) == 8

    def test_more_than_eight_with_disabled_passes(self):
        doc = make_catalog_dict(count=9, enabled_count=8)
        result = parse_puzzle_catalog_document(document=encode(doc))
        assert len(result) == 9
        assert result[-1].status is PuzzleStatus.DISABLED

    @pytest.mark.parametrize("count", [0, 7])
    def test_less_than_eight_enabled_fails(self, count):
        doc = make_catalog_dict(count=count)
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_eight_with_disabled_fails(self):
        doc = make_catalog_dict(count=8, enabled_count=7)
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    @pytest.mark.parametrize("value", ["text", None, 1, ["x"], bytearray(b"{}"), memoryview(b"{}")])
    def test_rejects_non_bytes(self, value):
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=value)

    def test_rejects_bytes_subclass(self):
        class _BytesSub(bytes):
            pass

        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=_BytesSub(encode(make_catalog_dict())))

    def test_rejects_bom(self):
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(
                document=b"\xef\xbb\xbf" + encode(make_catalog_dict())
            )

    def test_rejects_invalid_utf8(self):
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=b"\xff\xfe\x00\xfa")

    def test_rejects_invalid_json(self):
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(
                document=b'{"catalog_version": 1, "puzzles": ['
            )

    def test_rejects_missing_final_newline(self):
        raw = json.dumps(make_catalog_dict(), ensure_ascii=False).encode("utf-8")
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=raw)

    def test_rejects_comments(self):
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(
                document=b'{"catalog_version": 1, /* note */ "puzzles": []}\n'
            )

    def test_rejects_trailing_comma(self):
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(
                document=b'{"catalog_version": 1, "puzzles": [],}\n'
            )

    def test_rejects_json_lines(self):
        document = encode(make_catalog_dict()) + encode(make_catalog_dict())
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=document)

    def test_rejects_duplicate_top_level_key(self):
        raw = '{"catalog_version": 1, "catalog_version": 1, "puzzles": []}\n'
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=raw.encode("utf-8"))

    def test_rejects_duplicate_puzzle_key(self):
        body = json.dumps(make_puzzle_dict(1), ensure_ascii=False)
        raw = (
            '{"catalog_version": 1, "puzzles": ['
            + body[:-1]
            + ', "id": "ts-0001", "id": "ts-0001"}]}\n'
        )
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=raw.encode("utf-8"))

    def test_rejects_duplicate_provenance_key(self):
        doc = make_catalog_dict(count=1)
        prov = json.dumps(doc["puzzles"][0]["provenance"], ensure_ascii=False)
        body = json.dumps(doc["puzzles"][0], ensure_ascii=False)
        raw = (
            '{"catalog_version": 1, "puzzles": ['
            + body.replace(prov, prov[:-1] + ', "source_kind": "LICENSED"}')
            + "]}\n"
        )
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=raw.encode("utf-8"))

    @pytest.mark.parametrize("version", [True, 2, "1", None, 1.5])
    def test_rejects_wrong_catalog_version(self, version):
        doc = make_catalog_dict()
        doc["catalog_version"] = version
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    @pytest.mark.parametrize("puzzles", ["x", {"a": 1}, None])
    def test_rejects_non_array_puzzles(self, puzzles):
        raw = '{"catalog_version": 1, "puzzles": ' + json.dumps(puzzles) + "}\n"
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=raw.encode("utf-8"))

    def test_rejects_missing_top_level_key(self):
        raw = '{"catalog_version": 1}\n'
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=raw.encode("utf-8"))

    def test_rejects_extra_top_level_key(self):
        raw = '{"catalog_version": 1, "puzzles": [], "extra": 1}\n'
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=raw.encode("utf-8"))

    def test_rejects_puzzle_missing_field(self):
        doc = make_catalog_dict(count=1)
        del doc["puzzles"][0]["surface"]
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_puzzle_extra_field(self):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["extra"] = "x"
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_provenance_missing_field(self):
        doc = make_catalog_dict(count=1)
        del doc["puzzles"][0]["provenance"]["source_kind"]
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_provenance_extra_field(self):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["provenance"]["extra"] = "x"
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    @pytest.mark.parametrize(
        "field,value",
        [
            ("id", 1),
            ("id", None),
            ("title", None),
            ("surface", ["x"]),
            ("solution", {"x": 1}),
            ("status", 1),
            ("key_facts", "x"),
            ("provenance", "x"),
        ],
    )
    def test_rejects_wrong_field_types(self, field, value):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0][field] = value
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    @pytest.mark.parametrize("field", ["id", "title", "surface", "solution"])
    def test_rejects_blank_text_fields(self, field):
        for value in ("", "   ", "\t\n"):
            doc = make_catalog_dict(count=1)
            doc["puzzles"][0][field] = value
            with pytest.raises(PuzzleCatalogError):
                parse_puzzle_catalog_document(document=encode(doc))

    @pytest.mark.parametrize("bad_id", ["1", "ts-1", "ts-00001", "TS-0001", "tx-0001"])
    def test_rejects_invalid_id_format(self, bad_id):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["id"] = bad_id
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_zero_id(self):
        doc = make_catalog_dict(count=8)
        doc["puzzles"][0]["id"] = "ts-0000"
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_arabic_indic_digits(self):
        doc = make_catalog_dict(count=8)
        table = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
        for index, puzzle in enumerate(doc["puzzles"]):
            puzzle["id"] = f"ts-{index + 1:04d}".translate(table)
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_fullwidth_digits(self):
        doc = make_catalog_dict(count=8)
        table = str.maketrans("0123456789", "０１２３４５６７８９")
        for index, puzzle in enumerate(doc["puzzles"]):
            puzzle["id"] = f"ts-{index + 1:04d}".translate(table)
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_accepts_id_format_boundaries(self):
        doc = make_catalog_dict(count=8)
        for index, puzzle in enumerate(doc["puzzles"]):
            puzzle["id"] = f"ts-{index + 1:04d}"
        doc["puzzles"][-1]["id"] = "ts-9999"
        result = parse_puzzle_catalog_document(document=encode(doc))
        assert result[0].id == "ts-0001"
        assert result[-1].id == "ts-9999"

    def test_rejects_duplicate_ids(self):
        doc = make_catalog_dict(count=2)
        doc["puzzles"][1]["id"] = doc["puzzles"][0]["id"]
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_non_ascending_ids(self):
        doc = make_catalog_dict(count=2)
        doc["puzzles"][0], doc["puzzles"][1] = doc["puzzles"][1], doc["puzzles"][0]
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_unknown_status(self):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["status"] = "ACTIVE"
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_non_array_key_facts(self):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["key_facts"] = {"a": 1}
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_empty_key_facts(self):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["key_facts"] = []
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    @pytest.mark.parametrize("item", [1, None, ["x"], "", "   "])
    def test_rejects_invalid_key_fact_items(self, item):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["key_facts"] = ["合法事实", item]
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_rejects_unknown_source_kind(self):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["provenance"]["source_kind"] = "MIXED"
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    @pytest.mark.parametrize("value", [1, None, "", "   "])
    def test_rejects_invalid_source_reference(self, value):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["provenance"]["source_reference"] = value
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    @pytest.mark.parametrize("value", [1, True, "", "   "])
    def test_rejects_invalid_adaptation_note(self, value):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["provenance"]["adaptation_note"] = value
        with pytest.raises(PuzzleCatalogError):
            parse_puzzle_catalog_document(document=encode(doc))

    def test_accepts_adaptation_note_string(self):
        doc = make_catalog_dict(count=8)
        doc["puzzles"][0]["provenance"]["adaptation_note"] = "合成改编说明"
        result = parse_puzzle_catalog_document(document=encode(doc))
        assert result[0].title == "合成题目 1"

    def test_failure_message_excludes_solution_and_facts(self):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["solution"] = SYNTHETIC_SECRET
        doc["puzzles"][0]["key_facts"] = [SYNTHETIC_FACT]
        doc["catalog_version"] = 2
        with pytest.raises(PuzzleCatalogError) as exc:
            parse_puzzle_catalog_document(document=encode(doc))
        assert SYNTHETIC_SECRET not in str(exc.value)
        assert SYNTHETIC_FACT not in str(exc.value)

    def test_domain_validation_failure_message_excludes_content(self):
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["solution"] = SYNTHETIC_SECRET
        doc["puzzles"][0]["key_facts"] = ["合法事实", "   "]
        with pytest.raises(PuzzleCatalogError) as exc:
            parse_puzzle_catalog_document(document=encode(doc))
        assert SYNTHETIC_SECRET not in str(exc.value)

    def test_failure_returns_no_partial_puzzles(self, tmp_path):
        doc = make_catalog_dict(count=8)
        doc["puzzles"][5]["status"] = "ACTIVE"
        db = init_db(tmp_path)
        with pytest.raises(PuzzleCatalogError):
            import_puzzle_catalog(
                catalog_path=write_catalog(tmp_path, doc),
                database_path=db,
            )
        assert SQLitePuzzleRepository(database_path=db).get(puzzle_id="ts-0001") is None


class TestLocalLoading:
    def test_loads_valid_file(self, tmp_path):
        path = write_catalog(tmp_path)
        result = load_puzzle_catalog(catalog_path=str(path))
        assert type(result) is tuple
        assert len(result) == 8

    def test_accepts_path_object(self, tmp_path):
        path = write_catalog(tmp_path)
        assert len(load_puzzle_catalog(catalog_path=path)) == 8

    def test_relative_path_uses_current_working_directory(self, tmp_path, monkeypatch):
        write_catalog(tmp_path, name="relative.json")
        monkeypatch.chdir(tmp_path)
        result = load_puzzle_catalog(catalog_path="relative.json")
        assert len(result) == 8

    def test_windows_absolute_path_is_not_uri(self, tmp_path):
        path = write_catalog(tmp_path)
        assert len(load_puzzle_catalog(catalog_path=str(path.resolve()))) == 8

    @pytest.mark.parametrize("value", [5, None, b"x.json", ["x.json"], {"p": 1}])
    def test_rejects_wrong_types(self, value):
        with pytest.raises(PuzzleCatalogError):
            load_puzzle_catalog(catalog_path=value)

    @pytest.mark.parametrize("value", ["", "   "])
    def test_rejects_blank_paths(self, value):
        with pytest.raises(PuzzleCatalogError):
            load_puzzle_catalog(catalog_path=value)

    @pytest.mark.parametrize(
        "value",
        ["http://example.com/c.json", "https://example.com/c.json", "file:///tmp/c.json", "file:c.json"],
    )
    def test_rejects_urls_and_uris(self, value):
        with pytest.raises(PuzzleCatalogError):
            load_puzzle_catalog(catalog_path=value)

    def test_rejects_missing_file(self, tmp_path):
        with pytest.raises(PuzzleCatalogError):
            load_puzzle_catalog(catalog_path=tmp_path / "missing.json")
        assert not (tmp_path / "missing.json").exists()

    def test_rejects_directory(self, tmp_path):
        with pytest.raises(PuzzleCatalogError):
            load_puzzle_catalog(catalog_path=tmp_path)

    def test_oserror_propagates(self, tmp_path, monkeypatch):
        path = write_catalog(tmp_path)
        real_open = builtins.open

        def failing_open(file, *args, **kwargs):
            if Path(file) == path:
                raise PermissionError("simulated permission error")
            return real_open(file, *args, **kwargs)

        monkeypatch.setattr(builtins, "open", failing_open)
        with pytest.raises(PermissionError):
            load_puzzle_catalog(catalog_path=str(path))


class TestSqliteImport:
    def test_import_roundtrips_all_fields(self, tmp_path):
        db = init_db(tmp_path)
        doc = make_catalog_dict(count=8)
        import_puzzle_catalog(catalog_path=write_catalog(tmp_path, doc), database_path=db)
        repo = SQLitePuzzleRepository(database_path=db)
        for index in range(1, 9):
            puzzle = repo.get(puzzle_id=f"ts-{index:04d}")
            assert puzzle is not None
            assert puzzle.title == f"合成题目 {index}"
            assert puzzle.surface == f"这是第 {index} 道合成题目的题面。"
            assert puzzle.solution == f"这是第 {index} 道合成题目的完整题底，用于自动化测试。"
            assert puzzle.key_facts == (f"合成事实 A-{index}", f"合成事实 B-{index}")
            assert puzzle.status is PuzzleStatus.ENABLED

    def test_list_enabled_matches_resource(self, tmp_path):
        db = init_db(tmp_path)
        doc = make_catalog_dict(count=9, enabled_count=8)
        import_puzzle_catalog(catalog_path=write_catalog(tmp_path, doc), database_path=db)
        result = SQLitePuzzleRepository(database_path=db).list_enabled()
        assert [p.id for p in result] == [f"ts-{i:04d}" for i in range(1, 9)]

    def test_reimport_is_idempotent(self, tmp_path):
        db = init_db(tmp_path)
        path = write_catalog(tmp_path)
        import_puzzle_catalog(catalog_path=path, database_path=db)
        import_puzzle_catalog(catalog_path=path, database_path=db)
        result = SQLitePuzzleRepository(database_path=db).list_enabled()
        assert [p.id for p in result] == [f"ts-{i:04d}" for i in range(1, 9)]

    def test_status_only_change_is_saved(self, tmp_path):
        db = init_db(tmp_path)
        first = write_catalog(tmp_path, make_catalog_dict(count=10, enabled_count=9), name="v1.json")
        import_puzzle_catalog(catalog_path=first, database_path=db)
        second = make_catalog_dict(count=10, enabled_count=9)
        second["puzzles"][0]["status"] = "DISABLED"
        import_puzzle_catalog(
            catalog_path=write_catalog(tmp_path, second, name="v2.json"),
            database_path=db,
        )
        assert (
            SQLitePuzzleRepository(database_path=db).get(puzzle_id="ts-0001").status
            is PuzzleStatus.DISABLED
        )

    @pytest.mark.parametrize("field", ["title", "surface", "solution"])
    def test_core_field_change_fails_before_write(self, tmp_path, field):
        db = init_db(tmp_path)
        original = write_catalog(tmp_path, name="v1.json")
        import_puzzle_catalog(catalog_path=original, database_path=db)
        changed = make_catalog_dict(count=8)
        changed["puzzles"][0][field] = "被修改的合成内容"
        with pytest.raises(PuzzleCatalogError):
            import_puzzle_catalog(
                catalog_path=write_catalog(tmp_path, changed, name="v2.json"),
                database_path=db,
            )
        repo = SQLitePuzzleRepository(database_path=db)
        puzzle = repo.get(puzzle_id="ts-0001")
        assert getattr(puzzle, field) != "被修改的合成内容"

    def test_key_facts_change_fails_before_write(self, tmp_path):
        db = init_db(tmp_path)
        original = write_catalog(tmp_path, name="v1.json")
        import_puzzle_catalog(catalog_path=original, database_path=db)
        changed = make_catalog_dict(count=8)
        changed["puzzles"][0]["key_facts"] = ["被修改的合成事实"]
        with pytest.raises(PuzzleCatalogError):
            import_puzzle_catalog(
                catalog_path=write_catalog(tmp_path, changed, name="v2.json"),
                database_path=db,
            )
        assert (
            SQLitePuzzleRepository(database_path=db).get(puzzle_id="ts-0001").key_facts
            == ("合成事实 A-1", "合成事实 B-1")
        )

    def test_late_conflict_prevents_earlier_new_puzzle_write(self, tmp_path):
        db = init_db(tmp_path)
        repo = SQLitePuzzleRepository(database_path=db)
        existing = make_puzzle_dict(2)
        from turtle_soup.domain import Puzzle

        repo.save(
            puzzle=Puzzle(
                id=existing["id"],
                title=existing["title"],
                surface=existing["surface"],
                solution=existing["solution"],
                key_facts=tuple(existing["key_facts"]),
                status=PuzzleStatus.ENABLED,
            )
        )
        doc = make_catalog_dict(count=8)
        doc["puzzles"][1]["title"] = "数据库里的旧标题不同"
        with pytest.raises(PuzzleCatalogError):
            import_puzzle_catalog(
                catalog_path=write_catalog(tmp_path, doc),
                database_path=db,
            )
        assert repo.get(puzzle_id="ts-0001") is None
        assert repo.get(puzzle_id="ts-0003") is None

    def test_extra_database_puzzle_is_preserved(self, tmp_path):
        db = init_db(tmp_path)
        repo = SQLitePuzzleRepository(database_path=db)
        extra = make_puzzle_dict(99)
        from turtle_soup.domain import Puzzle

        repo.save(
            puzzle=Puzzle(
                id=extra["id"],
                title=extra["title"],
                surface=extra["surface"],
                solution=extra["solution"],
                key_facts=tuple(extra["key_facts"]),
                status=PuzzleStatus.ENABLED,
            )
        )
        import_puzzle_catalog(catalog_path=write_catalog(tmp_path), database_path=db)
        loaded = repo.get(puzzle_id="ts-0099")
        assert loaded is not None
        assert loaded.title == "合成题目 99"

    def test_resource_validation_failure_is_zero_write(self, tmp_path):
        db = init_db(tmp_path)
        doc = make_catalog_dict(count=7)
        with pytest.raises(PuzzleCatalogError):
            import_puzzle_catalog(
                catalog_path=write_catalog(tmp_path, doc),
                database_path=db,
            )
        assert SQLitePuzzleRepository(database_path=db).list_enabled() == ()

    def test_uninitialized_database_fails_with_sqlite_error(self, tmp_path):
        db = tmp_path / "bare.sqlite3"
        with pytest.raises(sqlite3.Error):
            import_puzzle_catalog(
                catalog_path=write_catalog(tmp_path),
                database_path=db,
            )

    def test_missing_database_parent_fails_with_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            import_puzzle_catalog(
                catalog_path=write_catalog(tmp_path),
                database_path=tmp_path / "no-such-dir" / "db.sqlite3",
            )

    def test_not_a_sqlite_file_fails_with_sqlite_error(self, tmp_path):
        fake_db = tmp_path / "fake.db"
        fake_db.write_text("this is not a sqlite database", encoding="utf-8")
        with pytest.raises(sqlite3.Error):
            import_puzzle_catalog(
                catalog_path=write_catalog(tmp_path),
                database_path=fake_db,
            )


class TestCli:
    def test_success_prints_exact_summary(self, tmp_path):
        db = init_db(tmp_path)
        catalog = write_catalog(tmp_path)
        result = run_cli(catalog, db)
        assert result.returncode == 0
        assert result.stdout == "puzzle catalog import completed\n"
        assert SQLitePuzzleRepository(database_path=db).get(puzzle_id="ts-0001") is not None

    def test_missing_catalog_path_fails(self, tmp_path):
        db = init_db(tmp_path)
        result = run_cli(None, db)
        assert result.returncode != 0
        assert result.stdout != "puzzle catalog import completed\n"

    def test_missing_database_path_fails(self, tmp_path):
        catalog = write_catalog(tmp_path)
        result = run_cli(catalog, None)
        assert result.returncode != 0
        assert result.stdout != "puzzle catalog import completed\n"

    def test_no_arguments_fails(self, tmp_path):
        result = run_cli(None, None)
        assert result.returncode != 0
        assert result.stdout != "puzzle catalog import completed\n"

    def test_url_catalog_path_fails(self, tmp_path):
        db = init_db(tmp_path)
        result = run_cli("http://example.com/c.json", db)
        assert result.returncode != 0
        assert result.stdout != "puzzle catalog import completed\n"

    def test_missing_catalog_file_fails(self, tmp_path):
        db = init_db(tmp_path)
        result = run_cli(tmp_path / "missing.json", db)
        assert result.returncode != 0
        assert result.stdout != "puzzle catalog import completed\n"

    def test_directory_catalog_path_fails(self, tmp_path):
        db = init_db(tmp_path)
        result = run_cli(tmp_path, db)
        assert result.returncode != 0
        assert result.stdout != "puzzle catalog import completed\n"

    def test_invalid_resource_fails_without_leaking_content(self, tmp_path):
        db = init_db(tmp_path)
        doc = make_catalog_dict(count=1)
        doc["puzzles"][0]["solution"] = SYNTHETIC_SECRET
        doc["puzzles"][0]["key_facts"] = [SYNTHETIC_FACT]
        doc["catalog_version"] = 2
        path = write_catalog(tmp_path, doc)
        result = run_cli(path, db)
        assert result.returncode != 0
        assert result.stdout != "puzzle catalog import completed\n"
        assert SYNTHETIC_SECRET not in result.stdout + result.stderr
        assert SYNTHETIC_FACT not in result.stdout + result.stderr

    def test_uninitialized_database_fails(self, tmp_path):
        db = tmp_path / "bare.sqlite3"
        result = run_cli(write_catalog(tmp_path), db)
        assert result.returncode != 0
        assert result.stdout != "puzzle catalog import completed\n"

    def test_cli_does_not_initialize_database(self, tmp_path):
        db = tmp_path / "bare.sqlite3"
        run_cli(write_catalog(tmp_path), db)
        with pytest.raises(sqlite3.Error):
            SQLitePuzzleRepository(database_path=db).get(puzzle_id="ts-0001")

    def test_module_import_requires_no_private_catalog(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = subprocess.run(
            [sys.executable, "-c", "import turtle_soup.catalog"],
            cwd=str(SRC_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
