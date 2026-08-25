from datetime import UTC, datetime, timedelta, tzinfo

import pytest

from turtle_soup.domain import (
    GameSession,
    GameStatus,
    GuessRecord,
    InvalidGameStateError,
    Puzzle,
    PuzzleStatus,
    QuestionRecord,
    Verdict,
)

T0 = datetime(2026, 1, 1, 8, 0, 0, tzinfo=UTC)


class _BrokenTzinfo(tzinfo):
    """tzinfo 非空但 utcoffset() 返回 None 的非法时区对象。"""

    def utcoffset(self, dt):
        return None

    def dst(self, dt):
        return None

    def tzname(self, dt):
        return None


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
        "created_at": T0,
    }
    fields.update(overrides)
    return QuestionRecord(**fields)


def make_guess(**overrides):
    fields = {
        "id": "g-1",
        "guess": "他曾在海难中靠喝汤维生，所以现在想喝那碗汤。",
        "solved": False,
        "created_at": T0,
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


class TestEnums:
    def test_puzzle_status_members_and_values(self):
        assert [(m.name, m.value) for m in PuzzleStatus] == [
            ("ENABLED", "ENABLED"),
            ("DISABLED", "DISABLED"),
        ]

    def test_game_status_members_and_values(self):
        assert [(m.name, m.value) for m in GameStatus] == [
            ("PLAYING", "PLAYING"),
            ("SOLVED", "SOLVED"),
            ("ABANDONED", "ABANDONED"),
        ]

    def test_verdict_members_and_values(self):
        assert [(m.name, m.value) for m in Verdict] == [
            ("YES", "YES"),
            ("NO", "NO"),
            ("IRRELEVANT", "IRRELEVANT"),
        ]

    def test_invalid_game_state_error_is_runtime_error(self):
        assert issubclass(InvalidGameStateError, RuntimeError)


class TestPuzzle:
    def test_creation_preserves_fields(self):
        puzzle = make_puzzle()
        assert puzzle.id == "puzzle-1"
        assert puzzle.title == "经典海龟汤"
        assert puzzle.surface == "一个人走进餐厅点了一碗海龟汤。"
        assert puzzle.solution == "他曾在海难中靠喝汤维生，汤的味道让他想起往事。"
        assert puzzle.key_facts == ("他经历过海难", "他想起往事")
        assert puzzle.status is PuzzleStatus.ENABLED

    def test_fields_are_immutable(self):
        puzzle = make_puzzle()
        with pytest.raises(AttributeError):
            puzzle.title = "新标题"
        with pytest.raises(AttributeError):
            puzzle.key_facts = ("另一个事实",)

    def test_rejects_positional_arguments(self):
        with pytest.raises(TypeError):
            Puzzle("puzzle-1", "标题", "题面", "题底", ("事实",), PuzzleStatus.ENABLED)

    @pytest.mark.parametrize("field", ["id", "title", "surface", "solution"])
    @pytest.mark.parametrize("value", ["", "   ", "\t\n"])
    def test_rejects_blank_text_fields(self, field, value):
        with pytest.raises(ValueError):
            make_puzzle(**{field: value})

    def test_rejects_non_string_text_fields(self):
        with pytest.raises(ValueError):
            make_puzzle(title=123)

    def test_rejects_empty_key_facts(self):
        with pytest.raises(ValueError):
            make_puzzle(key_facts=())

    def test_rejects_blank_key_fact_item(self):
        with pytest.raises(ValueError):
            make_puzzle(key_facts=("他经历过海难", "   "))

    def test_rejects_non_puzzle_status(self):
        with pytest.raises(ValueError):
            make_puzzle(status="ENABLED")
        with pytest.raises(ValueError):
            make_puzzle(status=GameStatus.PLAYING)

    def test_rejects_list_key_facts_without_conversion(self):
        with pytest.raises(ValueError):
            make_puzzle(key_facts=["他经历过海难", "他想起往事"])

    def test_rejects_generator_key_facts_without_conversion(self):
        with pytest.raises(ValueError):
            make_puzzle(key_facts=(item for item in ["他经历过海难"]))

    def test_rejects_tuple_subclass_key_facts(self):
        class _TupleSubclass(tuple):
            pass

        with pytest.raises(ValueError):
            make_puzzle(key_facts=_TupleSubclass(("他经历过海难",)))

    def test_rejects_non_string_key_fact_items(self):
        with pytest.raises(ValueError):
            make_puzzle(key_facts=("他经历过海难", 1))


class TestQuestionRecord:
    def test_creation_preserves_fields(self):
        record = make_question()
        assert record.id == "q-1"
        assert record.question == "他点的是海龟汤吗？"
        assert record.verdict is Verdict.YES
        assert record.created_at == T0

    def test_fields_are_immutable(self):
        record = make_question()
        with pytest.raises(AttributeError):
            record.verdict = Verdict.NO

    def test_rejects_positional_arguments(self):
        with pytest.raises(TypeError):
            QuestionRecord("q-1", "问题", Verdict.YES, T0)

    @pytest.mark.parametrize("field", ["id", "question"])
    @pytest.mark.parametrize("value", ["", "   "])
    def test_rejects_blank_id_and_question(self, field, value):
        with pytest.raises(ValueError):
            make_question(**{field: value})

    def test_rejects_verdict_string(self):
        with pytest.raises(ValueError):
            make_question(verdict="YES")

    def test_rejects_other_enum_as_verdict(self):
        with pytest.raises(ValueError):
            make_question(verdict=PuzzleStatus.ENABLED)

    def test_rejects_naive_datetime(self):
        with pytest.raises(ValueError):
            make_question(created_at=datetime(2026, 1, 1, 8, 0, 0))  # noqa: DTZ001

    def test_rejects_non_datetime(self):
        with pytest.raises(ValueError):
            make_question(created_at="2026-01-01T08:00:00+00:00")

    def test_rejects_tzinfo_with_none_utcoffset(self):
        broken = datetime(2026, 1, 1, 8, 0, 0, tzinfo=_BrokenTzinfo())
        with pytest.raises(ValueError):
            make_question(created_at=broken)


class TestGuessRecord:
    def test_creation_preserves_fields(self):
        record = make_guess()
        assert record.id == "g-1"
        assert record.guess == "他曾在海难中靠喝汤维生，所以现在想喝那碗汤。"
        assert record.solved is False
        assert record.created_at == T0

    def test_fields_are_immutable(self):
        record = make_guess()
        with pytest.raises(AttributeError):
            record.solved = True

    def test_rejects_positional_arguments(self):
        with pytest.raises(TypeError):
            GuessRecord("g-1", "猜测", True, T0)

    @pytest.mark.parametrize("field", ["id", "guess"])
    @pytest.mark.parametrize("value", ["", "   "])
    def test_rejects_blank_id_and_guess(self, field, value):
        with pytest.raises(ValueError):
            make_guess(**{field: value})

    @pytest.mark.parametrize("value", [0, 1, 2, None, "true"])
    def test_rejects_non_bool_solved(self, value):
        with pytest.raises(ValueError):
            make_guess(solved=value)

    def test_rejects_naive_datetime(self):
        with pytest.raises(ValueError):
            make_guess(created_at=datetime(2026, 1, 1, 8, 0, 0))  # noqa: DTZ001

    def test_rejects_tzinfo_with_none_utcoffset(self):
        broken = datetime(2026, 1, 1, 8, 0, 0, tzinfo=_BrokenTzinfo())
        with pytest.raises(ValueError):
            make_guess(created_at=broken)


class TestGameSessionConstruction:
    def test_start_creates_empty_playing_session(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        assert session.status is GameStatus.PLAYING
        assert session.ended_at is None
        assert session.questions == ()
        assert session.guesses == ()

    def test_start_rejects_positional_arguments(self):
        with pytest.raises(TypeError):
            GameSession.start("session-1", "puzzle-1", T0)

    def test_start_rejects_blank_ids(self):
        with pytest.raises(ValueError):
            GameSession.start(id="   ", puzzle_id="puzzle-1", started_at=T0)
        with pytest.raises(ValueError):
            GameSession.start(id="session-1", puzzle_id="", started_at=T0)

    def test_start_rejects_naive_started_at(self):
        with pytest.raises(ValueError):
            GameSession.start(
                id="session-1",
                puzzle_id="puzzle-1",
                started_at=datetime(2026, 1, 1, 8, 0, 0),  # noqa: DTZ001
            )

    def test_constructor_rejects_positional_arguments(self):
        with pytest.raises(TypeError):
            GameSession("session-1", "puzzle-1", GameStatus.PLAYING, T0, None, (), ())

    def test_constructor_requires_non_record_keywords(self):
        with pytest.raises(TypeError):
            GameSession(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        with pytest.raises(TypeError):
            GameSession(
                id="session-1",
                puzzle_id="puzzle-1",
                status=GameStatus.PLAYING,
                started_at=T0,
            )

    def test_constructor_defaults_records_to_empty_tuples(self):
        session = make_session()
        assert session.questions == ()
        assert session.guesses == ()

    def test_fields_are_immutable(self):
        session = make_session()
        with pytest.raises(AttributeError):
            session.status = GameStatus.SOLVED
        with pytest.raises(AttributeError):
            session.questions = (make_question(),)

    def test_direct_construction_playing(self):
        question = make_question()
        session = make_session(questions=(question,))
        assert session.status is GameStatus.PLAYING
        assert session.ended_at is None
        assert session.questions == (question,)

    def test_direct_construction_solved(self):
        first = make_guess(id="g-1", created_at=T0 + timedelta(minutes=1))
        solved = make_guess(
            id="g-2", solved=True, created_at=T0 + timedelta(minutes=10)
        )
        session = make_session(
            status=GameStatus.SOLVED,
            ended_at=solved.created_at,
            guesses=(first, solved),
        )
        assert session.status is GameStatus.SOLVED
        assert session.ended_at == solved.created_at
        assert session.guesses == (first, solved)

    def test_direct_construction_abandoned(self):
        question = make_question(created_at=T0 + timedelta(minutes=1))
        guess = make_guess(created_at=T0 + timedelta(minutes=2))
        ended_at = T0 + timedelta(minutes=5)
        session = make_session(
            status=GameStatus.ABANDONED,
            ended_at=ended_at,
            questions=(question,),
            guesses=(guess,),
        )
        assert session.status is GameStatus.ABANDONED
        assert session.ended_at == ended_at
        assert session.questions == (question,)
        assert session.guesses == (guess,)

    def test_rejects_string_status(self):
        with pytest.raises(ValueError):
            make_session(status="PLAYING")

    def test_rejects_other_enum_as_status(self):
        with pytest.raises(ValueError):
            make_session(status=Verdict.YES)

    def test_rejects_list_records_without_conversion(self):
        with pytest.raises(ValueError):
            make_session(questions=[make_question()])
        with pytest.raises(ValueError):
            make_session(guesses=[make_guess()])

    def test_rejects_generator_records_without_conversion(self):
        with pytest.raises(ValueError):
            make_session(questions=(item for item in [make_question()]))
        with pytest.raises(ValueError):
            make_session(guesses=(item for item in [make_guess()]))

    def test_rejects_tuple_subclass_records(self):
        class _TupleSubclass(tuple):
            pass

        with pytest.raises(ValueError):
            make_session(questions=_TupleSubclass((make_question(),)))
        with pytest.raises(ValueError):
            make_session(guesses=_TupleSubclass((make_guess(),)))

    def test_rejects_wrong_record_types(self):
        with pytest.raises(ValueError):
            make_session(questions=(make_guess(),))
        with pytest.raises(ValueError):
            make_session(guesses=(make_question(),))

    def test_rejects_duplicate_question_ids(self):
        with pytest.raises(ValueError):
            make_session(
                questions=(make_question(id="q-1"), make_question(id="q-1"))
            )

    def test_rejects_duplicate_guess_ids(self):
        with pytest.raises(ValueError):
            make_session(guesses=(make_guess(id="g-1"), make_guess(id="g-1")))

    def test_rejects_non_monotonic_question_times(self):
        earlier = make_question(id="q-1", created_at=T0 + timedelta(minutes=5))
        later = make_question(id="q-2", created_at=T0 + timedelta(minutes=1))
        with pytest.raises(ValueError):
            make_session(questions=(earlier, later))

    def test_rejects_non_monotonic_guess_times(self):
        earlier = make_guess(id="g-1", created_at=T0 + timedelta(minutes=5))
        later = make_guess(id="g-2", created_at=T0 + timedelta(minutes=1))
        with pytest.raises(ValueError):
            make_session(guesses=(earlier, later))

    def test_rejects_record_time_before_start(self):
        with pytest.raises(ValueError):
            make_session(
                questions=(make_question(created_at=T0 - timedelta(seconds=1)),)
            )
        with pytest.raises(ValueError):
            make_session(guesses=(make_guess(created_at=T0 - timedelta(seconds=1)),))

    def test_rejects_naive_started_at(self):
        with pytest.raises(ValueError):
            make_session(started_at=datetime(2026, 1, 1, 8, 0, 0))  # noqa: DTZ001

    def test_rejects_naive_ended_at(self):
        with pytest.raises(ValueError):
            make_session(
                status=GameStatus.ABANDONED, ended_at=datetime(2026, 1, 1, 8, 5, 0)  # noqa: DTZ001
            )

    def test_rejects_non_datetime_times(self):
        with pytest.raises(ValueError):
            make_session(started_at="2026-01-01T08:00:00+00:00")
        with pytest.raises(ValueError):
            make_session(
                status=GameStatus.ABANDONED, ended_at="2026-01-01T08:05:00+00:00"
            )

    def test_rejects_playing_with_ended_at(self):
        with pytest.raises(ValueError):
            make_session(ended_at=T0 + timedelta(minutes=5))

    def test_rejects_playing_with_solved_guess(self):
        solved = make_guess(id="g-1", solved=True)
        with pytest.raises(ValueError):
            make_session(guesses=(solved,))

    def test_rejects_solved_without_ended_at(self):
        solved = make_guess(id="g-1", solved=True)
        with pytest.raises(ValueError):
            make_session(status=GameStatus.SOLVED, guesses=(solved,))

    def test_rejects_solved_with_last_guess_unsolved(self):
        with pytest.raises(ValueError):
            make_session(
                status=GameStatus.SOLVED,
                ended_at=T0 + timedelta(minutes=10),
                guesses=(make_guess(id="g-1", solved=False),),
            )

    def test_rejects_solved_with_earlier_solved_guess(self):
        solved = make_guess(id="g-1", solved=True, created_at=T0 + timedelta(minutes=1))
        later = make_guess(id="g-2", solved=False, created_at=T0 + timedelta(minutes=2))
        with pytest.raises(ValueError):
            make_session(
                status=GameStatus.SOLVED,
                ended_at=later.created_at,
                guesses=(solved, later),
            )

    def test_rejects_abandoned_without_ended_at(self):
        with pytest.raises(ValueError):
            make_session(status=GameStatus.ABANDONED)

    def test_rejects_abandoned_with_solved_guess(self):
        solved = make_guess(id="g-1", solved=True)
        with pytest.raises(ValueError):
            make_session(
                status=GameStatus.ABANDONED,
                ended_at=T0 + timedelta(minutes=10),
                guesses=(solved,),
            )

    def test_rejects_ended_at_before_started_at(self):
        with pytest.raises(ValueError):
            make_session(
                status=GameStatus.ABANDONED, ended_at=T0 - timedelta(seconds=1)
            )

    def test_rejects_record_after_ended_at(self):
        with pytest.raises(ValueError):
            make_session(
                status=GameStatus.ABANDONED,
                ended_at=T0 + timedelta(minutes=5),
                questions=(make_question(created_at=T0 + timedelta(minutes=6)),),
            )
        with pytest.raises(ValueError):
            make_session(
                status=GameStatus.ABANDONED,
                ended_at=T0 + timedelta(minutes=5),
                guesses=(make_guess(created_at=T0 + timedelta(minutes=6)),),
            )


class TestGameSessionTransitions:
    def test_record_question_appends_and_keeps_original(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        record = make_question(id="q-1", created_at=T0 + timedelta(minutes=1))
        updated = session.record_question(record)
        assert updated is not session
        assert updated.questions == (record,)
        assert updated.status is GameStatus.PLAYING
        assert updated.ended_at is None
        assert session.questions == ()
        assert session.status is GameStatus.PLAYING

    def test_record_question_appends_in_order(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        first = make_question(id="q-1", created_at=T0 + timedelta(minutes=1))
        second = make_question(id="q-2", created_at=T0 + timedelta(minutes=2))
        updated = session.record_question(first).record_question(second)
        assert updated.questions == (first, second)

    def test_record_question_rejects_non_question_record(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        with pytest.raises(ValueError):
            session.record_question(make_guess())

    def test_record_question_rejects_duplicate_id(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        updated = session.record_question(
            make_question(id="q-1", created_at=T0 + timedelta(minutes=1))
        )
        with pytest.raises(ValueError):
            updated.record_question(
                make_question(id="q-1", created_at=T0 + timedelta(minutes=2))
            )

    def test_record_question_rejects_time_before_start(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        with pytest.raises(ValueError):
            session.record_question(make_question(created_at=T0 - timedelta(seconds=1)))

    def test_record_question_rejects_non_monotonic_time(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        updated = session.record_question(
            make_question(id="q-1", created_at=T0 + timedelta(minutes=5))
        )
        with pytest.raises(ValueError):
            updated.record_question(
                make_question(id="q-2", created_at=T0 + timedelta(minutes=1))
            )

    def test_unsolved_guess_keeps_playing(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        guess = make_guess(id="g-1", solved=False, created_at=T0 + timedelta(minutes=1))
        updated = session.record_guess(guess)
        assert updated.status is GameStatus.PLAYING
        assert updated.ended_at is None
        assert updated.guesses == (guess,)
        assert session.guesses == ()

    def test_solved_guess_transitions_to_solved(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        guess = make_guess(id="g-1", solved=True, created_at=T0 + timedelta(minutes=1))
        updated = session.record_guess(guess)
        assert updated.status is GameStatus.SOLVED
        assert updated.ended_at == guess.created_at
        assert updated.guesses == (guess,)

    def test_record_guess_rejects_non_guess_record(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        with pytest.raises(ValueError):
            session.record_guess(make_question())

    def test_record_guess_rejects_duplicate_id(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        updated = session.record_guess(
            make_guess(id="g-1", created_at=T0 + timedelta(minutes=1))
        )
        with pytest.raises(ValueError):
            updated.record_guess(
                make_guess(id="g-1", created_at=T0 + timedelta(minutes=2))
            )

    def test_abandon_transitions_and_preserves_records(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        with_question = session.record_question(
            make_question(id="q-1", created_at=T0 + timedelta(minutes=1))
        )
        ended_at = T0 + timedelta(minutes=5)
        abandoned = with_question.abandon(ended_at=ended_at)
        assert abandoned.status is GameStatus.ABANDONED
        assert abandoned.ended_at == ended_at
        assert abandoned.questions == with_question.questions
        assert session.status is GameStatus.PLAYING
        assert session.ended_at is None

    def test_abandon_rejects_positional_arguments(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        with pytest.raises(TypeError):
            session.abandon(T0 + timedelta(minutes=5))

    def test_abandon_rejects_ended_at_before_start(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        with pytest.raises(ValueError):
            session.abandon(ended_at=T0 - timedelta(seconds=1))

    def test_abandon_rejects_ended_at_before_records(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        with_question = session.record_question(
            make_question(id="q-1", created_at=T0 + timedelta(minutes=2))
        )
        with pytest.raises(ValueError):
            with_question.abandon(ended_at=T0 + timedelta(minutes=1))

    def test_abandon_rejects_naive_ended_at(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        with pytest.raises(ValueError):
            session.abandon(ended_at=datetime(2026, 1, 1, 8, 5, 0))  # noqa: DTZ001

    def test_solved_rejects_further_operations(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        solved = session.record_guess(
            make_guess(id="g-1", solved=True, created_at=T0 + timedelta(minutes=1))
        )
        with pytest.raises(InvalidGameStateError):
            solved.record_question(make_question(created_at=T0 + timedelta(minutes=2)))
        with pytest.raises(InvalidGameStateError):
            solved.record_guess(make_guess(created_at=T0 + timedelta(minutes=2)))
        with pytest.raises(InvalidGameStateError):
            solved.abandon(ended_at=T0 + timedelta(minutes=3))

    def test_abandoned_rejects_further_operations(self):
        session = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        abandoned = session.abandon(ended_at=T0 + timedelta(minutes=1))
        with pytest.raises(InvalidGameStateError):
            abandoned.record_question(make_question(created_at=T0 + timedelta(minutes=2)))
        with pytest.raises(InvalidGameStateError):
            abandoned.record_guess(make_guess(created_at=T0 + timedelta(minutes=2)))
        with pytest.raises(InvalidGameStateError):
            abandoned.abandon(ended_at=T0 + timedelta(minutes=3))

    def test_can_reveal_solution_only_in_terminal_states(self):
        playing = GameSession.start(id="session-1", puzzle_id="puzzle-1", started_at=T0)
        assert playing.can_reveal_solution is False
        solved = playing.record_guess(
            make_guess(id="g-1", solved=True, created_at=T0 + timedelta(minutes=1))
        )
        assert solved.can_reveal_solution is True
        abandoned = playing.abandon(ended_at=T0 + timedelta(minutes=1))
        assert abandoned.can_reveal_solution is True
