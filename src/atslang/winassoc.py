"""Windows file association for .atslang (spec §8.1).

Registers ``.atslang`` for the current user only (HKEY_CURRENT_USER), so no
administrator rights are needed. Double-clicking a file then runs
``python -m atslang --bekle "<file>"`` in a console window that stays open.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from typing import Protocol

EXTENSION = ".atslang"
PROG_ID = "ATSLang.Program"
CLASSES = r"Software\Classes"


class Registry(Protocol):
    """The tiny part of the registry we need, so tests can use a fake."""

    def get_default(self, key: str) -> str | None: ...
    def set_default(self, key: str, value: str) -> None: ...
    def delete_tree(self, key: str) -> None: ...


class WindowsRegistry:
    """HKEY_CURRENT_USER access through the standard library's winreg."""

    def __init__(self) -> None:
        import winreg  # only available on Windows

        self.winreg = winreg

    def get_default(self, key: str) -> str | None:
        try:
            with self.winreg.OpenKey(self.winreg.HKEY_CURRENT_USER, key) as handle:
                value, _ = self.winreg.QueryValueEx(handle, "")
                return value
        except OSError:
            return None

    def set_default(self, key: str, value: str) -> None:
        with self.winreg.CreateKey(self.winreg.HKEY_CURRENT_USER, key) as handle:
            self.winreg.SetValueEx(handle, "", 0, self.winreg.REG_SZ, value)

    def delete_tree(self, key: str) -> None:
        try:
            with self.winreg.OpenKey(self.winreg.HKEY_CURRENT_USER, key, 0,
                                     self.winreg.KEY_ALL_ACCESS) as handle:
                while True:
                    try:
                        child = self.winreg.EnumKey(handle, 0)
                    except OSError:
                        break
                    self.delete_tree(f"{key}\\{child}")
            self.winreg.DeleteKey(self.winreg.HKEY_CURRENT_USER, key)
        except FileNotFoundError:
            pass


def open_command(python: str) -> str:
    return f'"{python}" -m atslang --bekle "%1"'


def register(registry: Registry, python: str) -> None:
    registry.set_default(f"{CLASSES}\\{EXTENSION}", PROG_ID)
    registry.set_default(f"{CLASSES}\\{PROG_ID}", "ATSLang programı")
    registry.set_default(f"{CLASSES}\\{PROG_ID}\\shell\\open\\command", open_command(python))


def unregister(registry: Registry) -> None:
    registry.delete_tree(f"{CLASSES}\\{PROG_ID}")
    if registry.get_default(f"{CLASSES}\\{EXTENSION}") == PROG_ID:
        registry.delete_tree(f"{CLASSES}\\{EXTENSION}")


def package_is_installed(python: str) -> bool:
    """The association runs ``python -m atslang`` from any folder, so the
    package must be installed (``pip install -e .``), not only on PYTHONPATH."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    completed = subprocess.run([python, "-c", "import atslang"], env=env,
                               capture_output=True, cwd=tempfile.gettempdir())
    return completed.returncode == 0


def notify_shell() -> None:
    """Ask Explorer to refresh file associations."""
    try:
        import ctypes

        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)  # SHCNE_ASSOCCHANGED
    except Exception:
        pass


def is_windows() -> bool:
    return sys.platform == "win32"
