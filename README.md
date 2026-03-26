## Golf Meadows - Minutes + Website Starter

This repository now contains two practical, low-cost building blocks:

1. A **meeting minutes generator** (recording -> transcript -> structured minutes)
2. A **community website starter** with three visual options and a complaint form that can post to ADDA work-order APIs

---

## 1) Meeting Minutes Pipeline

Use this to convert meeting recordings into review-ready minutes.

### Quick run

```bash
./scripts/run_phase1.sh
```

### Non-interactive run

```bash
python3 scripts/phase1_pipeline.py \
  --input "/path/to/meeting.mp4" \
  --society "Golf Meadows" \
  --meeting-date "2026-03-24" \
  --meeting-title "Monthly Managing Committee Meeting" \
  --output-dir "./output"
```

Generated output:

- `output/*_transcript.txt`
- `output/*_minutes.md`

See `docs/PHASE1_FREE_STACK.md` for architecture and operating checklist.

---

## 2) Website with 3 style options + ADDA complaint submission

The web app is under `web/` and provides:

- **Option 1: Classic Civic**
- **Option 2: Bold Campaign**
- **Option 3: Calm Service**
- Complaint form that posts to ADDA Work Orders endpoint

### Setup
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
cp .env.example .env
```

Set values in `.env`:

- `ADDA_APT_ID` (required)
- Either `ADDA_BEARER_TOKEN` or (`ADDA_EMAIL` + `ADDA_PASSWORD`)
- `ADDA_WORK_ORDER_UPDATE_PATH` (verify exact path from your ADDA onboarding docs)

### Run website locally

```bash
uvicorn web.app:app --reload --port 8080
```

Open:

`http://127.0.0.1:8080/?theme=classic`

Try other themes:

- `?theme=bold`
- `?theme=calm`

### Notes on ADDA integration

ADDA endpoint names/payloads can vary by onboarding scope. This app keeps path and auth configurable through `.env`.
If ADDA returns schema errors, map their exact expected payload fields in `web/app.py` (`_build_work_order_payload`).

### Docker + Portainer deployment (no local dev)

For your preferred deployment style, this repo now includes:

- `Dockerfile`
- `docker-compose.yml`
- `docs/DEPLOY_PORTAINER_CLOUDFLARE.md` (step-by-step)

Quick run on server:

```bash
cp .env.example .env
# edit .env with ADDA settings
docker compose up -d --build
```

Then open:

`http://<server-ip>:8080/?theme=classic`

For domain publishing with Cloudflare Tunnel to `golfmedows.org`, follow:

`docs/DEPLOY_PORTAINER_CLOUDFLARE.md`

---

## Project structure

```text
docs/
  PHASE1_FREE_STACK.md
scripts/
  phase1_pipeline.py
  run_phase1.sh
templates/
  minutes_prompt.txt
web/
  app.py
  templates/index.html
.env.example
.gitignore
Dockerfile
docker-compose.yml
requirements.txt
```
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
