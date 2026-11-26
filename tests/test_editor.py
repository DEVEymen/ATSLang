"""The VS Code grammar must know every keyword and builtin of the language."""

import json
import re
from pathlib import Path

from atslang.builtins import BUILTINS, RANGE_NAME
from atslang.tokens import KEYWORDS
from atslang.values import TYPE_NAMES

GRAMMAR = Path(__file__).parent.parent / "editor" / "vscode" / "syntaxes" / "atslang.tmLanguage.json"


def _words(pattern: str) -> set[str]:
    group = re.search(r"\(([a-z_|]+)\)", pattern)
    return set(group.group(1).split("|")) if group else set()


def test_grammar_covers_language():
    repo = json.loads(GRAMMAR.read_text(encoding="utf-8"))["repository"]
    keywords = set()
    for pattern in repo["keyword"]["patterns"]:
        keywords |= _words(pattern["match"])
    assert keywords == set(KEYWORDS)
    assert _words(repo["builtin"]["match"]) == set(BUILTINS) | {RANGE_NAME}
    assert _words(repo["type-annotation"]["match"]) == set(TYPE_NAMES)


def test_package_files_are_valid_json():
    root = GRAMMAR.parent.parent
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    assert package["contributes"]["languages"][0]["extensions"] == [".atslang"]
    json.loads((root / "language-configuration.json").read_text(encoding="utf-8"))


def test_vsix_is_up_to_date(tmp_path):
    """editor/atslang.vsix must be rebuilt (tools/build_vsix.py) after editing editor/vscode."""
    import importlib.util

    root = GRAMMAR.parent.parent.parent.parent
    spec = importlib.util.spec_from_file_location("build_vsix", root / "tools" / "build_vsix.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fresh = module.build(tmp_path / "fresh.vsix")
    assert fresh.read_bytes() == (root / "editor" / "atslang.vsix").read_bytes()


def test_every_keyword_and_builtin_has_a_completion():
    root = GRAMMAR.parent.parent
    snippets = json.loads((root / "snippets" / "atslang.json").read_text(encoding="utf-8"))
    prefixes = {s["prefix"] for s in snippets.values()}
    assert set(KEYWORDS) <= prefixes
    assert set(BUILTINS) <= prefixes
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    assert package["contributes"]["snippets"][0]["path"] == "./snippets/atslang.json"


def test_marketplace_fields():
    root = GRAMMAR.parent.parent
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    for field in ("publisher", "license", "icon", "repository", "homepage", "bugs", "description"):
        assert package.get(field), field
    assert (root / package["icon"]).exists()
    assert (root / "LICENSE.txt").exists() and (root / "CHANGELOG.md").exists()
