# Amala YouTube operations

This is a local, approval-gated extension for Amala. It does not alter the existing OpenClaw gateway, messaging sessions, Ollama models, or other workflows.

## Current state

- The imported operations workbook is a live Google Sheet in the Amala Raj account: https://docs.google.com/spreadsheets/d/1X0Zkn0JHzXhLUq7aCFdsAopoOephhvAdCT2Y1SgCb3w/edit
- The original five tabs were preserved. `Operations Events` adds the requested event fields. Spreadsheet locale is India and time zone is India Standard Time.
- Local stages are implemented and tested with safe sample data. No real video has been approved or uploaded.
- Google Sheets automatic synchronization is implemented but **not connected**: application default credentials with Sheets scope are not available here.
- Groq is **not connected**: no `GROQ_API_KEY` was available. The code does not make a model request without it.
- Piper is **not available on PATH**. The voice stage accepts an existing WAV file or configured Piper binary and model.
- A [private GitHub repository](https://github.com/amalraj020-a11y/amala-youtube-operations) was created. Code push and scheduled daily execution are still pending. See [audit and blockers](docs/AUDIT.md).

## Run locally

Use Python 3.12+, FFmpeg, and ffprobe. Install packages from `requirements.txt` in a virtual environment. Set environment variables from `.env.example` through a protected user or service environment; do not commit a filled `.env`.

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python amala_youtube.py status 2026-10-18
python amala_youtube.py stage 2026-10-18 research --research-file C:\path\to\topic-research.md
python amala_youtube.py stage 2026-10-18 script --script-file C:\path\to\script.md --storyboard-file C:\path\to\storyboard.csv
python amala_youtube.py stage 2026-10-18 voice --voice-file C:\path\to\approved-voice.wav
python amala_youtube.py stage 2026-10-18 graphics
python amala_youtube.py stage 2026-10-18 assemble
python amala_youtube.py stage 2026-10-18 qa
python amala_youtube.py stage 2026-10-18 metadata --title "Accurate title for review"
```

Stages require the prior stage. `progress.json` stores status, timestamps and retry counts; completed stages are skipped on rerun. `--force` explicitly reruns one stage. Every transition is appended to `data/sheet-queue.jsonl`, which remains durable if Sheets is unavailable. Do not delete this queue until its contents have been backed up.

`qa` checks media streams, dimensions and duration. It records human checks as pending. The generated SRT has one coarse cue and needs timing review. A successful technical test does **not** produce `final.mp4` or authorize upload. `metadata` prepares a review package only. There is no public upload command.

## Google Sheets synchronization

`sheet_sync.py` upserts the latest event for each `date:stage` key into `Operations Events`. It reads the existing keys before writing and updates a row on retries, avoiding duplicate event rows. Local events stay in the queue for audit and recovery. It uses Google Application Default Credentials with the Sheets scope; no token is stored in this project.

```powershell
$env:GOOGLE_SHEET_ID='1X0Zkn0JHzXhLUq7aCFdsAopoOephhvAdCT2Y1SgCb3w'
python sheet_sync.py
```

To enable unattended sync, Raj must authorize a suitable Google OAuth client for the Amala account with the Sheets scope, store the resulting credentials outside Git, and confirm `python sheet_sync.py` succeeds. An ordinary browser sign-in does not authorize this local program. Do not paste passwords or tokens into chat.

## Approval and upload

Open `draft.mp4`, `captions.srt`, `asset-sources.md`, `qa-checklist.md`, and `upload-metadata.md`. Correct factual, visual, audio, rights or privacy issues first. Raj's explicit approval is required before any public release. Use YouTube Studio or an authorized YouTube Data API client after authorization; record the real video ID and upload time only after confirmation. The current code intentionally has no automated upload action.

Google's current [YouTube Data API quota reference](https://developers.google.com/youtube/data/determine_quota_cost) lists a separate default bucket of 100 `videos.insert` calls per day; [upload authorization](https://developers.google.com/youtube/documentation/authentication) requires OAuth access to the channel. The actual project quota and account access have not been verified here.

## Recovery

Read `python amala_youtube.py status YYYY-MM-DD`, resolve the failed stage's note, then rerun that stage. Completed earlier outputs are preserved. Groq 429 responses have at most two retries with bounded delay. Do not keep retrying an exhausted free quota; resume later or supply an approved local script.

## Cost policy

No payment method, paid plan, trial, credits, or hosted resource was activated by this project. Local electricity and internet costs still exist. Verify the actual Groq account is on its Free plan and its current limits before setting `GROQ_API_KEY`. See the [official Groq Free limits](https://console.groq.com/docs/rate-limits), [OpenClaw Groq setup](https://docs.openclaw.ai/providers/groq), and [Sheets API limits](https://developers.google.com/workspace/sheets/api/limits).
