# AMALA CODE QUEST audit — 2026-10-19

## Environment

- Windows host with FFmpeg, FFprobe, Python runtime, and Ollama executable.
- Free space observed: about 9.9 GB on C: and 83.9 GB on D:.
- Ollama service could not be contacted during the audit; no model was downloaded.
- Piper, Kokoro, and eSpeak NG were not installed locally.
- Microsoft Zira Desktop is the installed English SAPI voice and was used for the real pilot sample.
- The existing Groq GitHub Actions generation test passed with the free tier and a non-OpenAI Qwen model.
- Existing unrelated Amala automations were not changed.

## Voice comparison

| Candidate | Test result | Resource/cost | Decision |
|---|---|---|---|
| Microsoft Zira Desktop | Real WAV generated for episode 1 | Installed, local, ₹0 | Selected for pilot |
| Piper | Executable/model unavailable | Would require an additional model download | Deferred |
| Kokoro | Unavailable and larger dependency footprint | Additional packages/models required | Deferred |
| eSpeak NG | Available only in the Linux cloud workflow | Small, local, but robotic | Cloud fallback |

The pilot does not claim Zira is superior to untested engines. Piper and Kokoro require a later controlled sample comparison.

## Architecture and safety

- Original Pixel and Byte characters are drawn procedurally with Pillow.
- Narration stays local; FFmpeg assembles H.264/AAC MP4.
- Captions are burned into every scene.
- Job state, metadata, quality results, and an episode registry are persistent JSON files.
- Episode 1 stops at `awaiting_human_review` and is not published.
- No OpenAI API or paid model is called.
- No secrets are stored in source files.

## Current integration status

- YouTube Data API is enabled in a separate Google Cloud project.
- YouTube OAuth completion is temporarily blocked by the Codex browser approval usage limit.
- Instagram and Facebook require eligible professional/Page accounts and Meta OAuth credentials; no publishing claim is made.
