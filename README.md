## Golf Meadows Meeting Minutes - Phase 1 (Free Stack)

This repository contains a practical **"build, not buy"** starter for housing-society meeting minutes.

The focus is on being:

- **Low cost** (no mandatory per-minute SaaS costs)
- **Simple to run** (single command pipeline)
- **Reliable enough for non-technical users**
- **Human-reviewed** before circulation

---

## Why this Phase 1 approach

Instead of a fragile fully autonomous "join Google Meet as a bot" system, this phase uses:

1. A meeting recording (audio/video) as input
2. Local transcription (Whisper via `faster-whisper`)
3. Local summarization into formal minutes (Ollama LLM)
4. A fixed, committee-friendly minutes template

This avoids browser automation breakage, CAPTCHA/login issues, and high maintenance.

---

## Quick workflow

1. Record the meeting (phone, laptop, or Meet recording download)
2. Save media file to your machine
3. Run:

```bash
./scripts/run_phase1.sh
```

4. Enter file path + meeting metadata
5. Review generated minutes in `output/`
6. Secretary makes final edits before sharing

---

## Folder layout

```text
docs/
  PHASE1_FREE_STACK.md
scripts/
  phase1_pipeline.py
  run_phase1.sh
templates/
  minutes_prompt.txt
requirements.txt
```

---

## Prerequisites

- Python 3.10+
- `ffmpeg`
- Ollama running locally (`http://localhost:11434`)
- A local Ollama model (example: `llama3.1:8b`)

Install Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install an Ollama model:

```bash
ollama pull llama3.1:8b
```

---

## Run non-interactively (advanced)

```bash
python3 scripts/phase1_pipeline.py \
  --input "/path/to/meeting.mp4" \
  --society "Golf Meadows" \
  --meeting-date "2026-03-24" \
  --meeting-title "Monthly Managing Committee Meeting" \
  --output-dir "./output"
```

---

## Important note

Generated minutes are a draft. Always do a human verification pass for:

- names and attendance
- decisions and action owners
- deadlines and numbers

See `docs/PHASE1_FREE_STACK.md` for full architecture, assumptions, risks, and "idiot-proof" operating model.
