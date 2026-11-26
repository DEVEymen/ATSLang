"""Interface language selection and the user settings file (spec §7.4)."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

from atslang import messages

SETTINGS_FILE_NAME = "ayarlar.json"
ENV_VAR = "ATS_DIL"


def settings_dir(env: Mapping[str, str] | None = None, platform: str | None = None) -> Path:
    env = os.environ if env is None else env
    platform = sys.platform if platform is None else platform
    if platform == "win32":
        appdata = env.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return base / "atslang"
    return Path.home() / ".config" / "atslang"


def settings_path(env: Mapping[str, str] | None = None, platform: str | None = None) -> Path:
    return settings_dir(env, platform) / SETTINGS_FILE_NAME


@dataclass
class Notice:
    key: str
    params: dict[str, object] = field(default_factory=dict)


@dataclass
class LanguageChoice:
    language: str
    warnings: list[Notice] = field(default_factory=list)


def _read_settings(path: Path) -> str | None:
    """Return the saved language. Raise ValueError/OSError if the file is unusable."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("dil") not in messages.LANGUAGES:
        raise ValueError("invalid settings")
    return data["dil"]


def save_language(path: Path, language: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"dil": language}, ensure_ascii=False) + "\n", encoding="utf-8")


def ask_language(read: Callable[[str], str], write: TextIO) -> str | None:
    """Ask the bilingual first-run question. Return None on Ctrl+C / Ctrl+D."""
    while True:
        try:
            answer = read(messages.LANGUAGE_PROMPT).strip().lower()
        except (KeyboardInterrupt, EOFError):
            write.write("\n")
            return None
        if answer in ("", "tr"):
            return "tr"
        if answer == "en":
            return "en"
        write.write(messages.LANGUAGE_PROMPT_RETRY + "\n")


def resolve_language(
    cli_language: str | None,
    *,
    env: Mapping[str, str],
    path: Path,
    interactive: bool,
    read: Callable[[str], str],
    write: TextIO,
) -> LanguageChoice:
    """Order: --dil > ATS_DIL > settings file > first-run question > tr."""
    warnings: list[Notice] = []

    if cli_language is not None:
        return LanguageChoice(cli_language, warnings)

    env_value = env.get(ENV_VAR)
    if env_value is not None and env_value != "":
        normalised = env_value.strip().lower()
        if normalised in messages.LANGUAGES:
            return LanguageChoice(normalised, warnings)
        warnings.append(Notice("bad_env", {"value": env_value}))

    if path.exists():
        try:
            saved = _read_settings(path)
        except (OSError, ValueError, UnicodeDecodeError):
            warnings.append(Notice("bad_config", {"path": path}))
            return LanguageChoice(messages.DEFAULT_LANGUAGE, warnings)
        return LanguageChoice(saved, warnings)

    if interactive:
        chosen = ask_language(read, write)
        if chosen is None:
            return LanguageChoice(messages.DEFAULT_LANGUAGE, warnings)
        try:
            save_language(path, chosen)
        except OSError as exc:
            warnings.append(Notice("save_failed", {"reason": exc.strerror or exc}))
        return LanguageChoice(chosen, warnings)

    return LanguageChoice(messages.DEFAULT_LANGUAGE, warnings)
