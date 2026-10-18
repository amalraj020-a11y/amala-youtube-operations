# Baseline audit — 2026-10-18 IST

## Observed

| Area | Finding |
|---|---|
| OpenClaw | Version `2026.7.1-2` installed. Two configured agents (`main`, `amala`). Default model is `openai/gpt-5.6-sol` with `ollama/qwen3:4b` and `ollama/gemma3:1b` fallbacks. Groq provider is absent from the inspected config. |
| Gateway | Configuration binds to `loopback` on port `18789`. `openclaw status` could not finish because sandbox permissions denied a health-state write under the protected OpenClaw directory. Runtime health is unverified. |
| Messaging | Telegram enabled with allowlist; two WhatsApp accounts enabled with allowlists. Config presence does not establish live connection or message delivery. No real contacts were messaged. |
| Local tools | Node 26.9.0, npm 11.19.1, Git 2.55.0, FFmpeg 9.0.1 and ffprobe available. Ollama executable exists, but local service/model listing was inaccessible in this sandbox. Piper and Whisper commands absent. Bundled Python 3.12.14, Pillow 12.3.0 and openpyxl 3.1.5 available for this task; the normal Windows `python` alias failed. |
| Storage | Approximately 84 GB free on D: and 11.6 GB free on C: at audit time. |
| Existing workflow | `create-youtube-video.ps1` creates a static title card, Windows System.Speech WAV and horizontal MP4; a sample output exists. `morning-routine.mjs` exists. The new project does not overwrite these. |
| Backups | Six `openclaw.json` backup variants were observed. No live OpenClaw config was modified. |
| Scheduler | No matching Windows Scheduled Task was found in the available query. Existing OpenClaw cron state was not verified. No new task was installed. |
| Google | The workbook was imported into a native Google Sheet under the explicitly selected Amala Raj account. Browser access does not grant local API credentials. |
| GitHub | GitHub CLI saved account token is invalid. The inspected existing local repositories had no configured remote. A repository was created at `amalraj020-a11y/amala-youtube-operations`, and source plus sample tests were committed through the signed-in browser. |
| Workspace | Windows ACL denied writes to `D:\Openclaw`, including after a sandbox escalation. Project files were created in the other authorized writable task directory. This is not a durable installed location for a scheduler. |

## Blockers and exact next actions

1. Give the agent or Raj's user write access to a durable project directory, preferably `D:\Openclaw`, then move and retest this project there before scheduling.
2. Verify the actual Groq account is Free, create or choose a free-tier API key, and set `GROQ_API_KEY` in the protected environment visible to the gateway. Then use the official OpenClaw Groq provider mechanism and test latency. No key was read or changed here.
3. Install Piper and a permitted voice model from an official source, or provide an approved narration WAV. The current test used a synthetic tone, not narration.
4. Configure Google Application Default Credentials with Sheets scope for the Amala Raj account; then run `sheet_sync.py` and verify a real row update. No local API authorization was available in this run.
5. Renew `gh auth` or another authorized Git credential for `amalraj020-a11y/amala-youtube-operations` for future CLI pushes. Browser authentication did not authorize Git CLI.
6. Verify YouTube Studio/channel authorization and complete human QA and owner approval before any public upload. No upload has occurred.
7. After a durable install, inspect OpenClaw cron and Windows Task Scheduler again, register one nonduplicate schedule with the intended service account, and test a scheduled run.

## Test evidence

`python -m unittest discover -s tests -v`: 3 tests passed. One tested failure, retained earlier progress, recovery and completed-stage skipping. One rendered a six-second 1080×1920 MP4 with video and audio streams using synthetic test audio. One verified that a retried event updates the same Sheet row in a fake API session. No external AI, messaging, live Google API write, YouTube upload or scheduled execution test passed; those remain untested.
