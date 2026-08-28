import inspect

import pytest

from turtle_soup.domain import model_ports as ports


class TestModelPorts:
    def test_exact_exports(self):
        assert ports.__all__ == [
            "GuessJudgmentPort",
            "ModelJudgmentError",
            "QuestionJudgmentPort",
        ]

    def test_error_is_runtime_error(self):
        assert issubclass(ports.ModelJudgmentError, RuntimeError)

    def test_protocols_are_not_runtime_checkable(self):
        with pytest.raises(TypeError):
            isinstance(object(), ports.QuestionJudgmentPort)
        with pytest.raises(TypeError):
            isinstance(object(), ports.GuessJudgmentPort)

    def test_judge_question_is_async_keyword_only(self):
        func = ports.QuestionJudgmentPort.judge_question
        assert inspect.iscoroutinefunction(func)
        params = list(inspect.signature(func).parameters.values())
        assert params
        assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in params[1:])

    def test_judge_guess_is_async_keyword_only(self):
        func = ports.GuessJudgmentPort.judge_guess
        assert inspect.iscoroutinefunction(func)
        params = list(inspect.signature(func).parameters.values())
        assert params
        assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in params[1:])

    def test_domain_module_has_no_framework_dependencies(self):
        source = inspect.getsource(ports)
        for token in ("agently", "sqlite3", "fastapi", "pydantic"):
            assert token not in source
