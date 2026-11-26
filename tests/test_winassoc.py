import io

import pytest

from atslang import winassoc
from atslang.cli import main

PY = r"C:\Program Files\Python313\python.exe"


class FakeRegistry:
    def __init__(self):
        self.keys: dict[str, str | None] = {}

    def get_default(self, key):
        return self.keys.get(key)

    def set_default(self, key, value):
        self.keys[key] = value

    def delete_tree(self, key):
        for k in [k for k in self.keys if k == key or k.startswith(key + "\\")]:
            del self.keys[k]


def test_register_writes_current_user_keys():
    reg = FakeRegistry()
    winassoc.register(reg, PY)
    assert reg.keys[r"Software\Classes\.atslang"] == "ATSLang.Program"
    assert reg.keys[r"Software\Classes\ATSLang.Program\shell\open\command"] == \
        rf'"{PY}" -m atslang --bekle "%1"'


def test_unregister_removes_only_our_keys():
    reg = FakeRegistry()
    winassoc.register(reg, PY)
    reg.set_default(r"Software\Classes\.baska", "Baska.Program")
    winassoc.unregister(reg)
    assert reg.keys == {r"Software\Classes\.baska": "Baska.Program"}


def test_unregister_keeps_extension_owned_by_another_program():
    reg = FakeRegistry()
    reg.set_default(r"Software\Classes\.atslang", "Baska.Program")
    winassoc.unregister(reg)
    assert reg.keys[r"Software\Classes\.atslang"] == "Baska.Program"


def _main(*argv, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    code = main(list(argv), stdin=io.StringIO(kwargs.pop("stdin", "")), stdout=out, stderr=err,
                env={}, interactive=False, **kwargs)
    return code, out.getvalue(), err.getvalue()


@pytest.mark.parametrize("flag", ["--kur", "--register"])
def test_cli_register(tmp_path, flag):
    reg = FakeRegistry()
    code, out, _ = _main(flag, registry=reg, on_windows=True, settings=tmp_path / "s.json")
    assert code == 0
    assert "çift tıklayınca" in out
    assert r"Software\Classes\.atslang" in reg.keys


@pytest.mark.parametrize("flag", ["--kaldir", "--unregister"])
def test_cli_unregister(tmp_path, flag):
    reg = FakeRegistry()
    winassoc.register(reg, PY)
    code, out, _ = _main(flag, registry=reg, on_windows=True, settings=tmp_path / "s.json")
    assert (code, reg.keys) == (0, {})
    assert "kaldırıldı" in out


def test_cli_register_is_windows_only(tmp_path):
    code, _, err = _main("--kur", on_windows=False, settings=tmp_path / "s.json")
    assert code == 2
    assert "yalnızca Windows" in err


def test_wait_keeps_window_open(tmp_path):
    program = tmp_path / "p.atslang"
    program.write_text('yaz("a")', encoding="utf-8")
    code, out, _ = _main("--bekle", str(program), stdin="\n", settings=tmp_path / "s.json")
    assert code == 0
    assert out == "a\n\nKapatmak için Enter'a basın..."


def test_wait_also_after_errors(tmp_path):
    code, out, err = _main("--wait", "yok.atslang", settings=tmp_path / "s.json")
    assert code == 2
    assert "dosya bulunamadı" in err
    assert out.endswith("Kapatmak için Enter'a basın...")
