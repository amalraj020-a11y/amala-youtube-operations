"""Draw original duplicate-file Short scenes from a real synthetic demonstration."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from build_first_short_assets import base, font, lines

ROOT = Path(__file__).resolve().parents[1]
DAY = ROOT / "youtube" / "2026-10-19"
ASSETS = DAY / "assets"
SAMPLES = DAY / "sample_files"


def file_card(draw, y, name, color):
    draw.rounded_rectangle((125, y, 955, y + 185), 30, fill="#12364c", outline=color, width=4)
    draw.rounded_rectangle((157, y + 39, 242, y + 141), 15, fill=color)
    draw.text((284, y + 57), name, fill="#f5f8fc", font=font(47, True))


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)
    (SAMPLES / "notes-a.txt").write_text("Study plan: review Python daily.\n", encoding="utf-8")
    (SAMPLES / "notes-copy.txt").write_text("Study plan: review Python daily.\n", encoding="utf-8")
    (SAMPLES / "other.txt").write_text("Original file with different data.\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "find_duplicate_files.py"), str(SAMPLES)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if result != "MATCH: notes-a.txt = notes-copy.txt":
        raise RuntimeError(f"Unexpected sample result: {result}")

    im, d = base(1, "THE HOOK")
    lines(d, ["DUPLICATE", "FILES?"], 100, 335, 100, 130, bold=True)
    file_card(d, 790, "notes-a.txt", "#54d8c8")
    file_card(d, 1010, "notes-copy.txt", "#54d8c8")
    d.text((170, 1390), "SAME BYTES", fill="#ffca69", font=font(70, True))
    im.save(ASSETS / "scene-01.png")

    im, d = base(2, "FIRST FILTER")
    lines(d, ["COMPARE", "FILE SIZES"], 100, 335, 88, 120, bold=True)
    d.rounded_rectangle((108, 760, 972, 1350), 38, fill="#12364c")
    lines(d, ["notes-a.txt", "notes-copy.txt", "other.txt"], 160, 850, 49, 147)
    sizes = [f"{(SAMPLES / name).stat().st_size} bytes" for name in ("notes-a.txt", "notes-copy.txt", "other.txt")]
    lines(d, sizes, 674, 850, 39, 147, "#54d8c8", True)
    d.text((125, 1470), "UNIQUE SIZE? SKIP.", fill="#ffca69", font=font(57, True))
    im.save(ASSETS / "scene-02.png")

    im, d = base(3, "CONFIRM")
    lines(d, ["HASH, THEN", "COMPARE BYTES"], 100, 335, 78, 110, bold=True)
    d.rounded_rectangle((108, 760, 972, 1340), 38, fill="#12364c")
    lines(d, ["SHA-256", "same hash?", "check actual bytes", "report confirmed pair"], 160, 825, 53, 115)
    d.text((122, 1480), "READ ONLY", fill="#54d8c8", font=font(72, True))
    im.save(ASSETS / "scene-03.png")

    im, d = base(4, "REAL DEMO")
    lines(d, ["MATCH FOUND"], 100, 335, 86, 110, bold=True)
    d.rounded_rectangle((108, 710, 972, 1370), 38, fill="#0b101b", outline="#395668", width=3)
    lines(d, ["> python find_duplicate_files.py", "", "MATCH:", "notes-a.txt", "= notes-copy.txt"], 148, 792, 43, 99, "#e4fbf8")
    d.text((122, 1480), "NOTHING DELETED", fill="#ffca69", font=font(60, True))
    im.save(ASSETS / "scene-04.png")

    thumb = Image.new("RGB", (1080, 1920), "#071320")
    t = ImageDraw.Draw(thumb)
    t.rounded_rectangle((45, 70, 1035, 1850), 60, outline="#54d8c8", width=8)
    t.rounded_rectangle((95, 125, 985, 245), 28, fill="#54d8c8")
    t.text((145, 158), "FREE PYTHON TIP", fill="#071320", font=font(54, True))
    lines(t, ["FIND", "DUPLICATE", "FILES"], 95, 360, 100, 140, bold=True)
    file_card(t, 900, "notes-a.txt", "#54d8c8")
    file_card(t, 1140, "notes-copy.txt", "#54d8c8")
    t.text((125, 1630), "NO DELETING", fill="#ffca69", font=font(77, True))
    thumb.save(DAY / "thumbnail.png")
    (DAY / "asset-sources.md").write_text(
        "Scenes and thumbnail generated locally with Pillow. Scene four reports the actual output "
        "of examples/find_duplicate_files.py against generated sample files. No external media.\n",
        encoding="utf-8",
    )
    print(result)


if __name__ == "__main__":
    main()
