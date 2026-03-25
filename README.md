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
