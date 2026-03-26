## Golf Meadows - Community Portal + Minutes Starter

This repository contains two practical building blocks:

1. **Community web portal** (landing page + navigation pages + infra dashboard + issue reporting)
2. **Meeting minutes pipeline** (recording -> transcript -> structured minutes draft)

---

## 1) Community portal (multi-page website)

The FastAPI web app (`web/`) includes:

- Landing page with a hero image carousel
- Navigation pages:
  - Home
  - Downloads
  - Report an Issue
  - Feedback
  - Events
  - Infra Status (traffic-light style)
- Three visual themes:
  - `classic`
  - `bold`
  - `calm`
- Simplified issue form, routed to ADDA work-order endpoint

### Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn web.app:app --reload --port 8080
```

Open:

- `http://127.0.0.1:8080/?theme=classic`
- `http://127.0.0.1:8080/?theme=bold`
- `http://127.0.0.1:8080/?theme=calm`

### ADDA integration settings

Set in `.env`:

- `ADDA_APT_ID` (required for issue submission)
- Either:
  - `ADDA_BEARER_TOKEN`
  - or `ADDA_EMAIL` + `ADDA_PASSWORD`
- `ADDA_WORK_ORDER_UPDATE_PATH` (confirm exact route from ADDA onboarding)

If ADDA returns validation errors, adjust payload mapping in:
- `web/app.py` -> `_build_work_order_payload()`

---

## 2) Meeting minutes pipeline

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

See `docs/PHASE1_FREE_STACK.md` for architecture, assumptions, and operating checklist.

---

## Docker + Portainer deployment

For server deployment (no local dev workflow), this repo includes:

- `Dockerfile`
- `docker-compose.yml`
- `docs/DEPLOY_PORTAINER_CLOUDFLARE.md`

Quick server run:

```bash
cp .env.example .env
# edit .env with ADDA settings
docker compose up -d --build
```

Then open:

- `http://<server-ip>:8080/?theme=classic`

For Cloudflare Tunnel + domain mapping to `golfmeadows.org`, follow:
- `docs/DEPLOY_PORTAINER_CLOUDFLARE.md`

---

## Project structure

```text
docs/
  DEPLOY_PORTAINER_CLOUDFLARE.md
  PHASE1_FREE_STACK.md
scripts/
  phase1_pipeline.py
  run_phase1.sh
templates/
  minutes_prompt.txt
web/
  app.py
  static/images/
  templates/
.env.example
.gitignore
Dockerfile
docker-compose.yml
requirements.txt
```
