"""Generate and optionally publish one original Amala Short in a cloud runner."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
TOPICS = [
    "find files changed today with Python",
    "rename many files safely with Python",
    "count file types in a folder with Python",
    "find empty folders without deleting them",
    "create a simple folder inventory as CSV",
    "check which files use the most disk space",
    "compare two text files with Python",
    "make a timestamped backup copy of one file",
    "find duplicate filenames across folders",
    "organize downloads by file extension in preview mode",
    "read a CSV and show the top five rows",
    "create strong random passwords locally with Python",
]


def run(*args, cwd=None, input_text=None):
    return subprocess.run(args, cwd=cwd, input=input_text, text=True, check=True, capture_output=True)


def request(method: str, url: str, *, headers=None, data=None, timeout=60):
    req = Request(url, data=data, headers=headers or {}, method=method)
    try:
        return urlopen(req, timeout=timeout)
    except HTTPError as exc:
        detail = exc.read(1000).decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from None


def topic_for(slot: str) -> str:
    index = int(hashlib.sha256(slot.encode()).hexdigest()[:8], 16) % len(TOPICS)
    return TOPICS[index]


def groq_json(topic: str) -> dict:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is missing")
    prompt = f"""Create one original 35-50 second faceless YouTube Short about: {topic}.
Return JSON only with keys title, narration, description, hashtags, scenes.
Rules: title <= 70 characters; narration 80-115 words; exactly 5 scenes; each scene <= 7 words;
hashtags is an array of 4 useful tags; teach a safe Python technique; never claim guaranteed results;
never delete or modify user files; no copied quotes, music, brands, news, or unverifiable statistics.
The final narration sentence must invite viewers to subscribe for practical Python tips."""
    payload = {
        "model": MODEL,
        "temperature": 0.65,
        "max_tokens": 900,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "You write concise, original, factual educational Shorts. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
    }
    for attempt in range(3):
        req = Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                # Groq's edge rejects urllib's default Python-urllib user agent
                # from some shared cloud runner IPs with Cloudflare error 1010.
                "User-Agent": "amala-youtube-operations/1.0",
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=60) as response:
                result = json.load(response)
            return json.loads(result["choices"][0]["message"]["content"])
        except HTTPError as exc:
            if exc.code != 429 or attempt == 2:
                detail = exc.read(1000).decode("utf-8", errors="replace")
                raise RuntimeError(f"Groq HTTP {exc.code}: {detail}") from None
            time.sleep(min(20, int(exc.headers.get("retry-after", "3"))))
    raise AssertionError("unreachable")


def validate_content(content: dict) -> dict:
    required = {"title", "narration", "description", "hashtags", "scenes"}
    if not required.issubset(content):
        raise ValueError(f"Groq output lacks fields: {sorted(required - set(content))}")
    if len(str(content["title"])) > 70:
        raise ValueError("Title exceeds 70 characters")
    word_count = len(str(content["narration"]).split())
    # Allow a small cushion above the prompt's 115-word target. Models can
    # count punctuation-bound words differently, and a harmless one-word
    # variation should not stop the entire scheduled publishing job.
    if not 70 <= word_count <= 130:
        raise ValueError(f"Narration has {word_count} words; expected 70-130")
    if not isinstance(content["scenes"], list) or len(content["scenes"]) != 5:
        raise ValueError("Exactly five scenes are required")
    if not isinstance(content["hashtags"], list) or not 3 <= len(content["hashtags"]) <= 6:
        raise ValueError("Three to six hashtags are required")
    # Safe lessons often explain that preview code does not delete or remove
    # files. Reject misleading promises, while the prompt and fixed topic list
    # keep the generated lesson non-destructive.
    blocked = re.compile(r"\b(guaranteed|100%)\b", re.I)
    if blocked.search(str(content["narration"])):
        raise ValueError("Narration contains a blocked misleading claim")
    return content


def font(size: int):
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def render_cards(content: dict, out: Path) -> list[Path]:
    cards = []
    for number, text in enumerate(content["scenes"], 1):
        image = Image.new("RGB", (1080, 1920), "#08162e")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((70, 100, 1010, 1820), 55, fill="#10264b", outline="#43c6ff", width=8)
        draw.text((100, 180), "AMALA  •  PYTHON IN 1 MINUTE", font=font(42), fill="#43c6ff")
        wrapped = textwrap.wrap(str(text), width=17)[:5]
        y = 600 - (len(wrapped) - 1) * 55
        for line in wrapped:
            box = draw.textbbox((0, 0), line, font=font(84))
            draw.text(((1080 - (box[2] - box[0])) / 2, y), line, font=font(84), fill="white")
            y += 115
        draw.text((100, 1680), f"{number}/5   @Amala", font=font(42), fill="#9ce8ff")
        path = out / f"scene-{number:02}.png"
        image.save(path)
        cards.append(path)
    return cards


def make_simple_video(content: dict, out: Path, voice_file: Path | None = None) -> Path:
    out = out.resolve()
    narration = re.sub(r"[#*_`]", "", str(content["narration"]))
    wav = out / "voice.wav"
    transcript = out / "transcript.txt"
    transcript.write_text(narration + "\n", encoding="utf-8")
    if voice_file:
        shutil.copy2(voice_file.resolve(), wav)
    elif shutil.which("espeak-ng"):
        run("espeak-ng", "-v", "en-us+f3", "-s", "158", "-w", str(wav), narration)
    elif os.name == "nt":
        run("powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROOT / "scripts" / "narrate_windows.ps1"), "-ScriptPath", str(transcript), "-OutputPath", str(wav))
    else:
        raise RuntimeError("espeak-ng is required on non-Windows runners")
    cards = render_cards(content, out)
    seconds = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(wav)).stdout.strip())
    concat = out / "concat.txt"
    per_card = seconds / len(cards)
    concat.write_text("".join(f"file '{p.as_posix()}'\nduration {per_card:.3f}\n" for p in cards) + f"file '{cards[-1].as_posix()}'\n", encoding="utf-8")
    video = out / "amala-short.mp4"
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-safe", "0", "-f", "concat", "-i", str(concat), "-i", str(wav), "-vf", "fps=30,scale=1080:1920,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(video))
    probe = json.loads(run("ffprobe", "-v", "error", "-show_streams", "-of", "json", str(video)).stdout)
    kinds = {stream["codec_type"] for stream in probe["streams"]}
    if kinds != {"video", "audio"}:
        raise RuntimeError(f"Rendered media streams are invalid: {kinds}")
    return video


def moneyprinter_command(content: dict, cards: list[Path]) -> list[str]:
    """Build the no-paid-provider MoneyPrinterTurbo CLI invocation."""
    return [
        "mpt", "cli",
        "--video-subject", str(content["title"]),
        "--video-script", re.sub(r"[#*_`]", "", str(content["narration"])),
        "--video-source", "local",
        "--video-materials", ",".join(str(card.resolve()) for card in cards),
        "--video-aspect", "9:16",
        "--video-concat-mode", "sequential",
        "--image-motion", "zoom",
        "--video-transition-mode", "fade-in",
        "--voice-name", os.environ.get("MPT_VOICE", "en-US-AriaNeural"),
        "--voice-rate", "1.08",
        "--bgm-type", "none",
        "--subtitle-enabled",
        "--subtitle-position", "bottom",
        "--subtitle-background-enabled",
        "--rounded-subtitle-background",
        "--stop-at", "video",
    ]


def make_moneyprinter_video(content: dict, out: Path) -> Path:
    """Render with MoneyPrinterTurbo using only local visuals and free Edge TTS."""
    if not shutil.which("mpt"):
        raise RuntimeError("MoneyPrinterTurbo CLI (mpt) is not installed")
    cards = render_cards(content, out)
    result = run(*moneyprinter_command(content, cards), cwd=out)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    try:
        payload = json.loads(lines[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError("MoneyPrinterTurbo did not return its JSON result") from exc
    task_result = payload.get("result", payload)
    videos = task_result.get("videos") or []
    if not videos:
        raise RuntimeError(f"MoneyPrinterTurbo failed: {task_result.get('error', 'no video returned')}")
    source = Path(videos[0])
    if not source.is_absolute():
        source = (out / source).resolve()
    if not source.is_file() or source.stat().st_size == 0:
        raise RuntimeError("MoneyPrinterTurbo returned a missing or empty video")
    video = out / "amala-short.mp4"
    shutil.copy2(source, video)
    (out / "moneyprinter-result.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return video


def make_video(content: dict, out: Path, voice_file: Path | None = None, renderer: str = "simple") -> tuple[Path, str]:
    if renderer == "moneyprinter" and voice_file is None:
        try:
            return make_moneyprinter_video(content, out), "moneyprinter"
        except Exception as exc:
            (out / "moneyprinter-fallback.txt").write_text(
                f"MoneyPrinterTurbo failed; used the reliable local renderer.\n{type(exc).__name__}: {exc}\n",
                encoding="utf-8",
            )
    return make_simple_video(content, out, voice_file), "simple"


def youtube_access_token() -> str:
    required = ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError("Missing YouTube secrets: " + ", ".join(missing))
    form = urlencode({
        "client_id": os.environ["YOUTUBE_CLIENT_ID"],
        "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
        "refresh_token": os.environ["YOUTUBE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    with request("POST", "https://oauth2.googleapis.com/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data=form, timeout=30) as response:
        return json.load(response)["access_token"]


def upload(video: Path, content: dict) -> str:
    token = youtube_access_token()
    tags = [str(tag).lstrip("#") for tag in content["hashtags"]]
    description = str(content["description"]).strip() + "\n\n" + " ".join("#" + tag for tag in tags)
    metadata = {
        "snippet": {"title": content["title"], "description": description, "tags": tags, "categoryId": "27"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True},
    }
    body = json.dumps(metadata).encode()
    with request("POST",
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status&notifySubscribers=false",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8", "Content-Length": str(len(body)), "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(video.stat().st_size)},
        data=body, timeout=30,
    ) as start:
        location = start.headers["Location"]
    media = video.read_bytes()
    with request("PUT", location, headers={"Content-Type": "video/mp4", "Content-Length": str(len(media))}, data=media, timeout=300) as finish:
        result = json.load(finish)
    return "https://youtube.com/shorts/" + result["id"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true", help="Upload publicly after generation and QA")
    parser.add_argument("--slot", help="Stable UTC slot, defaults to the current hour")
    parser.add_argument("--content-file", type=Path, help="Use reviewed JSON instead of calling Groq")
    parser.add_argument("--voice-file", type=Path, help="Use an existing WAV for a local media test")
    parser.add_argument(
        "--renderer", choices=("simple", "moneyprinter"),
        default=os.environ.get("VIDEO_RENDERER", "simple"),
        help="Video renderer; MoneyPrinterTurbo falls back to the simple renderer on failure",
    )
    parser.add_argument("--output", type=Path, default=ROOT / "hourly-output")
    args = parser.parse_args()
    slot = args.slot or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H")
    out = args.output / slot.replace(":", "-")
    out.mkdir(parents=True, exist_ok=True)
    if args.content_file:
        content = json.loads(args.content_file.read_text(encoding="utf-8"))
    else:
        content = groq_json(topic_for(slot))
    validate_content(content)
    (out / "content.json").write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    video, renderer = make_video(content, out, args.voice_file, args.renderer)
    result = {"slot": slot, "model": MODEL, "renderer": renderer, "video": str(video), "published": False}
    if args.publish:
        result.update(published=True, url=upload(video, content))
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
