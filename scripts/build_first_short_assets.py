"""Draw original scene art and a real, read-only sample run for the first Short."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DAY = ROOT / "youtube" / "2026-10-18"
ASSETS = DAY / "assets"
SAMPLES = DAY / "sample_files"
W, H = 1080, 1920


def font(size: int, bold: bool = False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def base(number: int, label: str):
    im = Image.new("RGB", (W, H), "#071320")
    d = ImageDraw.Draw(im)
    for y in range(H):
        color = (7 + y // 240, 19 + y // 180, 32 + y // 125)
        d.line((0, y, W, y), fill=color)
    d.rounded_rectangle((58, 76, 1022, 1844), 54, outline="#54d8c8", width=5)
    d.text((100, 110), "AMALA  /  FREE TECH HACKS", fill="#54d8c8", font=font(32, True))
    d.text((100, 1760), f"{number:02} / 04     {label}", fill="#96aabb", font=font(29))
    for x in range(4):
        d.rounded_rectangle((102 + x * 222, 1718, 298 + x * 222, 1730), 6, fill="#54d8c8" if x < number else "#365263")
    return im, d


def lines(draw, items, x, y, size, step, fill="#f5f8fc", bold=False):
    for line in items:
        draw.text((x, y), line, fill=fill, font=font(size, bold))
        y += step


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)
    for name, size in (("sample-video.dat", 3_145_728), ("sample-slides.dat", 1_572_864), ("sample-notes.dat", 524_288)):
        with (SAMPLES / name).open("wb") as output:
            output.truncate(size)
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "largest_files.py"), str(SAMPLES)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()

    im, d = base(1, "THE PROBLEM")
    lines(d, ["WHAT IS FILLING", "YOUR DRIVE?"], 104, 335, 83, 105, bold=True)
    d.rounded_rectangle((104, 680, 976, 1330), 34, fill="#122d42")
    d.text((150, 760), "Downloads", fill="#ffffff", font=font(78, True))
    d.text((150, 905), "?  ?  ?  ?  ?", fill="#ffca69", font=font(78, True))
    lines(d, ["Inspect file sizes", "No deletion. No moves."], 150, 1090, 45, 78)
    im.save(ASSETS / "scene-01.png")

    im, d = base(2, "THE SETUP")
    lines(d, ["CHOOSE A FOLDER"], 104, 340, 78, 105, bold=True)
    d.rounded_rectangle((96, 600, 984, 1380), 30, fill="#102a3c")
    lines(d, ["from pathlib import Path", "", "folder = Path(\"Downloads\")", "files = (p for p in", "  folder.iterdir()", "  if p.is_file())"], 142, 700, 40, 89, "#e4fbf8")
    d.text((120, 1500), "READ ONLY", fill="#54d8c8", font=font(64, True))
    im.save(ASSETS / "scene-02.png")

    im, d = base(3, "THE SORT")
    lines(d, ["BIGGEST FIRST"], 104, 340, 80, 105, bold=True)
    d.rounded_rectangle((96, 630, 984, 1070), 30, fill="#102a3c")
    lines(d, ["sorted(files,", "  key=lambda p:", "    p.stat().st_size,", "  reverse=True)[:5]"], 145, 706, 44, 88, "#e4fbf8")
    for i, (label, width) in enumerate((("3.0 MB", 590), ("1.5 MB", 345), ("0.5 MB", 150))):
        y = 1200 + i * 145
        d.rounded_rectangle((105, y, 105 + width, y + 72), 20, fill="#54d8c8")
        d.text((725, y + 8), label, fill="#ffffff", font=font(39, True))
    im.save(ASSETS / "scene-03.png")

    im, d = base(4, "ACTUAL DEMO")
    lines(d, ["SEE THE TOP FIVE"], 104, 340, 73, 105, bold=True)
    d.rounded_rectangle((96, 615, 984, 1390), 30, fill="#0b101b", outline="#395668", width=3)
    d.text((145, 680), "> python largest_files.py samples", fill="#54d8c8", font=font(34, True))
    output_lines = [line.strip() for line in result.splitlines()]
    lines(d, output_lines, 145, 790, 34, 90)
    d.text((106, 1500), "REVIEW BEFORE DELETING", fill="#ffca69", font=font(51, True))
    im.save(ASSETS / "scene-04.png")
    thumb = Image.new("RGB", (W, H), "#071320")
    t = ImageDraw.Draw(thumb)
    t.rounded_rectangle((45, 70, 1035, 1850), 60, outline="#54d8c8", width=8)
    t.rounded_rectangle((95, 125, 985, 245), 28, fill="#54d8c8")
    t.text((145, 158), "FREE PYTHON TIP", fill="#071320", font=font(54, True))
    lines(t, ["FIND YOUR", "5 BIGGEST", "FILES"], 100, 360, 105, 135, bold=True)
    t.rounded_rectangle((105, 850, 975, 1510), 42, fill="#13354b")
    for i, (width, label) in enumerate(((670, "3.0 MB"), (430, "1.5 MB"), (200, "0.5 MB"))):
        y = 955 + i * 168
        t.rounded_rectangle((145, y, 145 + width, y + 86), 23, fill="#54d8c8")
        t.text((165, y + 15), label, fill="#071320", font=font(50, True))
    t.text((120, 1640), "NO DELETING", fill="#ffca69", font=font(77, True))
    thumb.save(DAY / "thumbnail.png")
    (DAY / "asset-sources.md").write_text(
        "All four scenes and the thumbnail were drawn locally with Pillow. "
        "Scene four shows actual output from examples/largest_files.py run on generated sample files. "
        "No external footage, music, logos, or personal files were used.\n", encoding="utf-8"
    )
    print(result)


if __name__ == "__main__":
    main()
