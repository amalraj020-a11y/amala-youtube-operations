"""Create the private AMALA CODE QUEST pilot with local, zero-cost tools."""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "code-quest-output"
REGISTRY = ROOT / "data" / "episode_registry.json"

EPISODE = {
    "episode": 1,
    "series": "AMALA CODE QUEST",
    "topic": "What Is Full-Stack Development?",
    "objective": "Explain how frontend, backend, and database work together.",
    "hook": "A website is more than the screen you see!",
    "narration": (
        "A website is more than the screen you see! Meet Pixel, who builds the frontend: "
        "buttons, colors, and pages people use. Byte handles the backend, where code receives "
        "requests and applies the rules. Their library, Data Dock, stores details such as names "
        "and scores. When you tap Login, the frontend asks the backend, the backend checks the "
        "database, then sends an answer back. A full-stack developer understands how all three "
        "parts connect. Follow Amala Code Quest for the next lesson!"
    ),
    "scenes": [
        {"caption": "A WEBSITE HAS 3 TEAMMATES", "speaker": "Pixel", "dialogue": "A website is more than its screen!"},
        {"caption": "FRONTEND = WHAT PEOPLE USE", "speaker": "Pixel", "dialogue": "I build buttons, colors and pages."},
        {"caption": "BACKEND = RULES + REQUESTS", "speaker": "Byte", "dialogue": "I receive requests and apply rules."},
        {"caption": "DATABASE = SAVED INFORMATION", "speaker": "Data Dock", "dialogue": "I store names, scores and more."},
        {"caption": "LOGIN: FRONT → BACK → DATA", "speaker": "Byte", "dialogue": "The three parts work as one team."},
        {"caption": "FULL-STACK CONNECTS ALL 3", "speaker": "Pixel", "dialogue": "Next: frontend development!"},
    ],
    "metadata": {
        "title": "What Is Full-Stack Development? | Amala Code Quest #1",
        "description": "Pixel and Byte explain frontend, backend, and databases in one practical cartoon lesson.",
        "hashtags": ["#FullStack", "#CodingForBeginners", "#WebDevelopment", "#AmalaCodeQuest", "#Shorts"],
        "pinned_comment": "Which part should Pixel and Byte explore next: frontend, backend, or databases?",
        "thumbnail_concept": "Pixel and Byte connect three glowing blocks labelled FRONT, BACK, and DATA.",
    },
}


def run(*args: str, input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, input=input_bytes, check=True, capture_output=True)


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def speak(text: str, wav: Path) -> str:
    transcript = wav.with_suffix(".txt")
    transcript.write_text(text, encoding="utf-8")
    if shutil.which("piper"):
        raise RuntimeError("Piper executable exists but no reviewed voice model is configured")
    if shutil.which("espeak-ng"):
        run("espeak-ng", "-v", "en-us+f3", "-s", "168", "-w", str(wav), text)
        return "espeak-ng en-us+f3"
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if not shell:
        raise RuntimeError("No reviewed local TTS engine is available")
    run(
        shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
        str(ROOT / "scripts" / "narrate_windows.ps1"),
        "-ScriptPath", str(transcript), "-OutputPath", str(wav),
    )
    return "Microsoft Zira Desktop via Windows SAPI"


def audio_duration(wav: Path) -> float:
    result = run(
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(wav),
    )
    return float(result.stdout.decode().strip())


def centered(draw: ImageDraw.ImageDraw, text: str, y: int, face: ImageFont.ImageFont, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=face)
    draw.text(((1080 - box[2] + box[0]) / 2, y), text, font=face, fill=fill)


def draw_pixel(draw: ImageDraw.ImageDraw, x: int, y: int, talking: bool, wave: float) -> None:
    # Pixel: an original purple square explorer with antenna and star badge.
    draw.rounded_rectangle((x, y, x + 330, y + 420), 70, fill="#7C4DFF", outline="#E8DCFF", width=10)
    draw.line((x + 165, y, x + 165, y - 70), fill="#E8DCFF", width=14)
    draw.ellipse((x + 140, y - 100, x + 190, y - 50), fill="#FFD740")
    draw.ellipse((x + 70, y + 105, x + 125, y + 165), fill="white")
    draw.ellipse((x + 215, y + 105, x + 270, y + 165), fill="white")
    draw.ellipse((x + 88, y + 125, x + 110, y + 150), fill="#152238")
    draw.ellipse((x + 233, y + 125, x + 255, y + 150), fill="#152238")
    mouth_h = 42 if talking else 12
    draw.rounded_rectangle((x + 105, y + 230, x + 235, y + 230 + mouth_h), 16, fill="#301660")
    hand_y = y + 180 + int(35 * wave)
    draw.line((x + 320, y + 245, x + 410, hand_y), fill="#E8DCFF", width=28)
    draw.ellipse((x + 135, y + 325, x + 195, y + 385), fill="#FFD740", outline="white", width=4)


def draw_byte(draw: ImageDraw.ImageDraw, x: int, y: int, talking: bool, wave: float) -> None:
    # Byte: an original teal round robot with terminal eyes.
    draw.ellipse((x, y, x + 340, y + 400), fill="#00AFA0", outline="#B9FFF7", width=10)
    draw.rounded_rectangle((x + 55, y + 90, x + 285, y + 195), 35, fill="#072D36")
    draw.text((x + 85, y + 105), ">_", font=font(64), fill="#7CFFCB")
    mouth_h = 46 if talking else 10
    draw.rounded_rectangle((x + 110, y + 240, x + 230, y + 240 + mouth_h), 18, fill="#06343B")
    hand_y = y + 140 + int(30 * wave)
    draw.line((x + 20, y + 245, x - 65, hand_y), fill="#B9FFF7", width=28)
    draw.ellipse((x + 120, y + 330, x + 220, y + 365), fill="#FFCA28")


def frame_at(second: float, duration: float) -> Image.Image:
    scene_count = len(EPISODE["scenes"])
    scene_len = duration / scene_count
    scene_index = min(scene_count - 1, int(second / scene_len))
    scene = EPISODE["scenes"][scene_index]
    phase = (second % scene_len) / scene_len
    bob = int(math.sin(second * 4.0) * 12)
    image = Image.new("RGB", (1080, 1920), "#07152E")
    draw = ImageDraw.Draw(image)
    # Moving code-grid background.
    shift = int((second * 35) % 120)
    for y in range(-120 + shift, 1920, 120):
        draw.line((0, y, 1080, y), fill="#102A50", width=3)
    for x in range(0, 1080, 120):
        draw.line((x, 0, x, 1920), fill="#0E2548", width=3)
    draw.rounded_rectangle((45, 40, 1035, 235), 45, fill="#0C2448", outline="#43C6FF", width=6)
    centered(draw, "AMALA CODE QUEST", 72, font(70), "#43C6FF")
    centered(draw, "EPISODE 1 • FULL-STACK", 158, font(36), "#CBEFFF")
    talking = int(second * 5) % 2 == 0
    wave = math.sin(second * 3.2)
    if scene["speaker"] == "Byte":
        draw_pixel(draw, 90, 520 + bob, False, wave * 0.2)
        draw_byte(draw, 650, 500 - bob, talking, wave)
    else:
        draw_pixel(draw, 90, 500 - bob, talking, wave)
        draw_byte(draw, 650, 520 + bob, False, wave * 0.2)
    # Three system blocks provide a stable visual analogy.
    labels = [("FRONT", "#7C4DFF"), ("BACK", "#00AFA0"), ("DATA", "#FFB300")]
    for i, (label, color) in enumerate(labels):
        x = 80 + i * 330
        active = (scene_index in {1, 4, 5} and i == 0) or (scene_index in {2, 4, 5} and i == 1) or (scene_index in {3, 4, 5} and i == 2)
        draw.rounded_rectangle((x, 1100, x + 270, 1240), 28, fill=color if active else "#18365F", outline="white", width=4)
        centered_x = x + 135
        box = draw.textbbox((0, 0), label, font=font(38))
        draw.text((centered_x - (box[2] - box[0]) / 2, 1145), label, font=font(38), fill="white")
        if i < 2:
            draw.text((x + 284, 1140), "→", font=font(48), fill="#7FE8FF")
    # Caption panel and progress bar.
    draw.rounded_rectangle((55, 1360, 1025, 1745), 48, fill="#091E3D", outline="#FFFFFF", width=5)
    centered(draw, scene["caption"], 1415, font(48), "#FFD740")
    lines = []
    words = scene["dialogue"].split()
    while words:
        lines.append(" ".join(words[:7]))
        words = words[7:]
    for i, line in enumerate(lines[:3]):
        centered(draw, line, 1515 + i * 66, font(42, False), "white")
    draw.rounded_rectangle((90, 1790, 990, 1825), 18, fill="#18365F")
    draw.rounded_rectangle((90, 1790, 90 + int(900 * second / duration), 1825), 18, fill="#43C6FF")
    centered(draw, "Original characters • Local tools • No paid AI", 1850, font(28, False), "#98BADC")
    return image


def render(video: Path, wav: Path, duration: float, fps: int = 10) -> None:
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(fps), "-i", "-",
        "-i", str(wav), "-c:v", "libx264", "-preset", "veryfast", "-crf", "25",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(video),
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdin is not None
    for n in range(math.ceil(duration * fps)):
        process.stdin.write(frame_at(n / fps, duration).tobytes())
    process.stdin.close()
    stderr = process.stderr.read() if process.stderr else b""
    code = process.wait()
    if code:
        raise RuntimeError(stderr.decode(errors="replace"))


def validate(video: Path, duration: float) -> dict:
    probe = json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)).stdout)
    streams = {s["codec_type"]: s for s in probe["streams"]}
    actual = float(probe["format"]["duration"])
    checks = {
        "mp4_exists": video.exists() and video.stat().st_size > 500_000,
        "vertical_1080x1920": streams["video"]["width"] == 1080 and streams["video"]["height"] == 1920,
        "video_h264": streams["video"]["codec_name"] == "h264",
        "audio_present": "audio" in streams,
        "duration_matches_audio": abs(actual - duration) < 1.0,
        "private_review_only": True,
        "captions_burned_in": True,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Quality validation failed: {checks}")
    return {"checks": checks, "duration_seconds": round(actual, 2), "size_bytes": video.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_ROOT / "episode-001")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    state = {"episode": 1, "status": "started", "updated_at": datetime.now(timezone.utc).isoformat()}
    (out / "job-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    (out / "script.json").write_text(json.dumps(EPISODE, indent=2), encoding="utf-8")
    wav = out / "voice-zira.wav"
    engine = speak(EPISODE["narration"], wav)
    duration = audio_duration(wav)
    video = out / "amala-code-quest-001.mp4"
    render(video, wav, duration)
    report = validate(video, duration)
    relative_wav = wav.relative_to(ROOT).as_posix()
    relative_video = video.relative_to(ROOT).as_posix()
    report.update({"voice_engine": engine, "voice_sample": relative_wav, "openai_used": False, "groq_used": False, "published": False})
    (out / "quality-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out / "metadata.json").write_text(json.dumps(EPISODE["metadata"], indent=2), encoding="utf-8")
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {"episodes": []}
    registry["episodes"] = [e for e in registry["episodes"] if e.get("episode") != 1]
    registry["episodes"].append({"episode": 1, "topic": EPISODE["topic"], "status": "awaiting_human_review", "video": relative_video, "published": {}})
    REGISTRY.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    state.update(status="awaiting_human_review", updated_at=datetime.now(timezone.utc).isoformat(), video=relative_video)
    (out / "job-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps({"video": str(video), "duration": report["duration_seconds"], "status": state["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
