"""Draws the README images in docs/gorseller from real ATSLang output.

    python tools/make_readme_assets.py

Needs Pillow (pip install pillow); the interpreter itself does not.
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from atslang.builtins import BUILTINS  # noqa: E402
from atslang.cli import main  # noqa: E402
from atslang.repl import Repl  # noqa: E402
from atslang.values import TYPE_NAMES  # noqa: E402

OUT = ROOT / "docs" / "gorseller"
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "C:/Windows/Fonts/consola.ttf",
]
FONT_SIZE = 18
LINE_H = 26
CHAR_W = 11
PAD = 24
TITLE_H = 38

# VS Code "Dark+" colours, the same scopes as editor/vscode
BG = (30, 30, 30)
TITLE_BG = (45, 45, 48)
DEFAULT = (212, 212, 212)
NAME = (156, 220, 254)
CONTROL = (197, 134, 192)
STORAGE = (86, 156, 214)
STRING = (206, 145, 120)
NUMBER = (181, 206, 168)
COMMENT = (106, 153, 85)
FUNCTION = (220, 220, 170)
TYPE = (78, 201, 176)
PROMPT = (78, 201, 176)
ERROR = (244, 71, 71)
HINT = (229, 192, 123)
DIM = (128, 128, 128)

CONTROL_WORDS = {"eger", "degilse", "iken", "her", "tekrarla", "dur", "devam", "dondur"}
STORAGE_WORDS = {"var", "sabit", "fonksiyon", "dogru", "yanlis", "ve", "veya", "degil"}
FUNCTIONS = set(BUILTINS) | {"aralik"}
TOKEN = re.compile(r'(#.*$)|("(?:\\.|[^"\\])*"?)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)|(\s+)|(.)')


def font() -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if Path(path).exists():
            return ImageFont.truetype(path, FONT_SIZE)
    raise SystemExit("no monospace font found")


FONT = font()


def highlight(line: str) -> list[tuple[str, tuple[int, int, int]]]:
    parts = []
    previous_word = ""
    for m in TOKEN.finditer(line):
        text = m.group(0)
        if m.group(1):
            colour = COMMENT
        elif m.group(2):
            colour = STRING
        elif m.group(3):
            colour = NUMBER
        elif m.group(4):
            rest = line[m.end():].lstrip()
            if text in CONTROL_WORDS:
                colour = CONTROL
            elif text in STORAGE_WORDS:
                colour = STORAGE
            elif text in TYPE_NAMES and previous_word == ":":
                colour = TYPE
            elif rest.startswith("(") or previous_word == "fonksiyon":
                colour = FUNCTION
            else:
                colour = NAME
            previous_word = text
        else:
            colour = DEFAULT
            if text.strip():
                previous_word = text
        parts.append((text, colour))
    return parts


def window(width_chars: int, height_lines: int, title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    w = PAD * 2 + width_chars * CHAR_W
    h = TITLE_H + PAD * 2 + height_lines * LINE_H
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, TITLE_H], fill=TITLE_BG)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([16 + i * 22, 13, 28 + i * 22, 25], fill=c)
    tw = d.textlength(title, font=FONT)
    d.text(((w - tw) / 2, 9), title, font=FONT, fill=DIM)
    return img, d


def draw_parts(d: ImageDraw.ImageDraw, row: int, parts) -> None:
    x = PAD
    y = TITLE_H + PAD + row * LINE_H
    for text, colour in parts:
        d.text((x, y), text, font=FONT, fill=colour)
        x += d.textlength(text, font=FONT)


# -- code image -----------------------------------------------------------
CODE = '''# Sayı tahmin oyunu
fonksiyon ipucu(tahmin: tam, hedef: tam): metin {
    eger tahmin < hedef { dondur "Daha büyük!" }
    eger tahmin > hedef { dondur "Daha küçük!" }
    dondur "Bildin!"
}

var hedef = rastgele(1, 100)
var deneme = 0
iken dogru {
    var tahmin = tam(oku("Tahminin: "))
    deneme = deneme + 1
    yaz(ipucu(tahmin, hedef))
    eger tahmin == hedef { dur }
}
yaz(metin(deneme) + " denemede bildin.")'''


def code_image() -> Path:
    lines = CODE.split("\n")
    img, d = window(max(len(l) for l in lines) + 2, len(lines), "sayi_tahmin.atslang")
    for row, line in enumerate(lines):
        draw_parts(d, row, highlight(line))
    path = OUT / "kod.png"
    img.save(path, optimize=True)
    return path


# -- error image ----------------------------------------------------------
def error_parts(line: str):
    if line.startswith("hata["):
        return [(line, ERROR)]
    if line.lstrip().startswith("= öneri"):
        return [(line, HINT)]
    if "^" in line and "|" in line:
        bar = line.index("|") + 1
        return [(line[:bar], DIM), (line[bar:], ERROR)]
    if line.lstrip().startswith("-->") or line.strip() == "|":
        return [(line, DIM)]
    if "|" in line:
        bar = line.index("|") + 1
        return [(line[:bar], DIM)] + highlight(line[bar:])
    return [(line, DEFAULT)]


def error_image() -> Path:
    program = 'var ad = "Ayşe"\nvar yas = 20\nyaz("Merhaba " + ad + ", yaşın " + yas)\n'
    path = OUT / "_hata.atslang"
    path.write_text(program, encoding="utf-8")
    err = io.StringIO()
    main([str(path), "--dil", "tr"], stdin=io.StringIO(), stdout=io.StringIO(), stderr=err,
         env={}, settings=OUT / "_ayar.json", interactive=False)
    path.unlink()
    text = err.getvalue().replace(str(path), "program.atslang").rstrip("\n")
    lines = ["$ ats program.atslang"] + text.split("\n")
    img, d = window(max(len(l) for l in lines) + 2, len(lines), "Terminal")
    draw_parts(d, 0, [("$ ", PROMPT), ("ats program.atslang", DEFAULT)])
    for row, line in enumerate(lines[1:], 1):
        draw_parts(d, row, error_parts(line))
    out = OUT / "hata.png"
    img.save(out, optimize=True)
    return out


# -- animated REPL --------------------------------------------------------
SESSION = [
    'var ad = "Eymen"',
    'yaz("Merhaba " + ad + "!")',
    "5 * 8 + 2",
    "fonksiyon kare(n) { dondur n * n }",
    "kare(12)",
    'var meyveler = ["elma", "armut"]',
    'ekle(meyveler, "kiraz")',
    "meyveler",
    'buyuk("istanbul")',
    "her i aralik(1, 3) { yaz(i * 10) }",
]


def run_session() -> list[tuple[str, list[str]]]:
    """Run SESSION in a real REPL and collect each input's output lines."""
    results = []
    for count in range(1, len(SESSION) + 1):
        lines = iter(SESSION[:count])
        out = io.StringIO()

        def read(prompt, lines=lines):
            try:
                return next(lines)
            except StopIteration:
                raise EOFError from None

        Repl(read, out, io.StringIO(), "tr").run()
        results.append(out.getvalue())
    outputs = []
    banner_lines = 2
    seen = 0
    for i, text in enumerate(results):
        body = text.split("\n")[banner_lines:]
        body = [l for l in body if l != ""]
        new = body[seen:]
        seen = len(body)
        outputs.append((SESSION[i], new))
    return outputs


def repl_gif() -> Path:
    transcript = run_session()
    width = 52
    rows_visible = 18
    frames: list[Image.Image] = []
    durations: list[int] = []
    screen: list[list] = [
        [("ATSLang 0.7 etkileşimli mod", PROMPT)],
        [("Çıkmak için: cikis", DIM)],
    ]

    def snapshot(duration: int, typing: list | None = None) -> None:
        lines = screen + ([typing] if typing is not None else [])
        lines = lines[-rows_visible:]
        img, d = window(width, rows_visible, "ats")
        for row, parts in enumerate(lines):
            draw_parts(d, row, parts)
        frames.append(img.convert("P", palette=Image.ADAPTIVE, colors=64))
        durations.append(duration)

    snapshot(900)
    for command, output in transcript:
        step = max(1, len(command) // 14)
        for end in range(0, len(command) + 1, step):
            snapshot(45, [("ats> ", PROMPT)] + highlight(command[:end]) + [("▌", DEFAULT)])
        screen.append([("ats> ", PROMPT)] + highlight(command))
        snapshot(250)
        for line in output:
            if line.startswith('"') or line.startswith("[") or line[:1].isdigit():
                screen.append(highlight(line))
            else:
                screen.append([(line, DEFAULT)])
        snapshot(1100)
    snapshot(2500, [("ats> ", PROMPT), ("▌", DEFAULT)])

    path = OUT / "demo.gif"
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0,
                   optimize=True, disposal=1)
    return path


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for made in (code_image(), error_image(), repl_gif()):
        print(made, made.stat().st_size // 1024, "KB")
