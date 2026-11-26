import io
import json
from pathlib import Path

import pytest

from atslang.config import resolve_language, settings_path


def resolve(path: Path, cli=None, env=None, interactive=False, answers=()):
    pending = list(answers)
    prompts = []

    def read(prompt):
        prompts.append(prompt)
        if not pending:
            raise EOFError
        answer = pending.pop(0)
        if isinstance(answer, BaseException):
            raise answer
        return answer

    choice = resolve_language(cli, env=env or {}, path=path, interactive=interactive,
                              read=read, write=io.StringIO())
    return choice, prompts


@pytest.fixture
def path(tmp_path):
    return tmp_path / "atslang" / "ayarlar.json"


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")


def test_default_is_turkish(path):
    assert resolve(path)[0].language == "tr"


def test_priority_cli_over_env_over_file(path):
    save(path, {"dil": "tr"})
    assert resolve(path, cli="en", env={"ATS_DIL": "tr"})[0].language == "en"
    assert resolve(path, env={"ATS_DIL": "en"})[0].language == "en"
    save(path, {"dil": "en"})
    assert resolve(path)[0].language == "en"


def test_env_is_case_insensitive(path):
    assert resolve(path, env={"ATS_DIL": " EN "})[0].language == "en"


def test_invalid_env_warns_and_falls_through(path):
    save(path, {"dil": "en"})
    choice, _ = resolve(path, env={"ATS_DIL": "de"})
    assert choice.language == "en"
    assert [w.key for w in choice.warnings] == ["bad_env"]


@pytest.mark.parametrize("content", ["{bozuk", '{"dil": "de"}', "[]"])
def test_corrupt_settings_warn_and_use_turkish(path, content):
    save(path, content)
    choice, prompts = resolve(path, interactive=True, answers=["en"])
    assert choice.language == "tr"
    assert [w.key for w in choice.warnings] == ["bad_config"]
    assert prompts == []


def test_never_prompts_without_terminal(path):
    choice, prompts = resolve(path, interactive=False, answers=["en"])
    assert (choice.language, prompts) == ("tr", [])
    assert not path.exists()


def test_first_run_prompt_saves_answer(path):
    choice, prompts = resolve(path, interactive=True, answers=["en\n"])
    assert choice.language == "en"
    assert len(prompts) == 1
    assert json.loads(path.read_text(encoding="utf-8")) == {"dil": "en"}
    # Second run: no question.
    choice, prompts = resolve(path, interactive=True, answers=["tr"])
    assert (choice.language, prompts) == ("en", [])


def test_enter_means_turkish(path):
    assert resolve(path, interactive=True, answers=["\n"])[0].language == "tr"
    assert json.loads(path.read_text(encoding="utf-8")) == {"dil": "tr"}


def test_invalid_answer_asks_again(path):
    choice, prompts = resolve(path, interactive=True, answers=["almanca", "EN"])
    assert choice.language == "en"
    assert len(prompts) == 2


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt(), EOFError()])
def test_ctrl_c_uses_turkish_and_saves_nothing(path, interrupt):
    choice, _ = resolve(path, interactive=True, answers=[interrupt])
    assert choice.language == "tr"
    assert not path.exists()


def test_cli_or_env_skips_the_prompt(path):
    assert resolve(path, cli="en", interactive=True, answers=["tr"])[1] == []
    assert resolve(path, env={"ATS_DIL": "en"}, interactive=True, answers=["tr"])[1] == []


def test_save_failure_warns(tmp_path):
    blocker = tmp_path / "dosya"
    blocker.write_text("")
    choice, _ = resolve(blocker / "ayarlar.json", interactive=True, answers=["en"])
    assert choice.language == "en"
    assert [w.key for w in choice.warnings] == ["save_failed"]


def test_settings_locations(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert settings_path({"APPDATA": "C:/Users/a/AppData/Roaming"}, "win32") == \
        Path("C:/Users/a/AppData/Roaming") / "atslang" / "ayarlar.json"
    assert settings_path({}, "linux") == tmp_path / ".config" / "atslang" / "ayarlar.json"
    assert settings_path({}, "darwin") == tmp_path / ".config" / "atslang" / "ayarlar.json"
