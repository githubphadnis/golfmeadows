## Phase 1 "Free Stack" for Golf Meadows

This document is a concrete implementation blueprint for a low-cost meeting minutes pipeline that is practical for a housing society.

## 1) Objective

Create a repeatable flow where a committee member can produce good meeting minutes from a meeting recording with minimal technical effort.

## 2) Build-vs-buy position

For Golf Meadows, this phase is intentionally:

- "do not buy expensive SaaS"
- avoid fragile browser bot automation
- use local open-source components where possible
- keep humans in the approval loop

## 3) Scope of Phase 1

### Included

- Local transcription from meeting audio/video files
- Structured minutes generation using a fixed prompt template
- Output files saved in a predictable folder
- One command wrapper for non-technical operation

### Excluded (for now)

- Autonomous Google Meet joining bot
- Real-time streaming transcript during meeting
- Multi-user web dashboard
- Full audit/compliance workflow automation

## 4) Recommended stack

### Core components

- Python pipeline script (`scripts/phase1_pipeline.py`)
- STT: `faster-whisper` (local)
- LLM summarization: local Ollama REST API
- Media support: `ffmpeg`
- Templates: `templates/minutes_prompt.txt`

### Why this stack

- No recurring API usage by default
- Works offline after setup
- Low operational fragility compared to browser bots

## 5) Hardware assumptions

Minimum workable:

- 4 CPU cores
- 8 GB RAM
- SSD storage

Recommended:

- 8+ CPU cores
- 16 GB RAM
- Optional NVIDIA GPU for faster transcription

Expected behavior:

- CPU-only transcription is slower but acceptable for monthly meetings.
- LLM summarization on small local models may be slower but consistent.

## 6) Idiot-proof operating model

1. Secretary records the meeting or downloads meeting recording.
2. Save recording to known folder (example: `~/Meetings/`).
3. Run `./scripts/run_phase1.sh`.
4. Paste recording path when asked.
5. Fill date/title prompts.
6. Wait for completion.
7. Open generated markdown in `output/`.
8. Perform human quality check using a fixed checklist.
9. Share approved minutes.

## 7) Quality checklist (must-do)

- Attendance names are accurate.
- Each decision is explicitly stated.
- Every action item has an owner and target date.
- Financial numbers match source discussion.
- Sensitive content is handled appropriately before sharing.

## 8) Risks and mitigations

### Risk: poor audio quality
Mitigation: encourage single speaker at a time and use phone near center of room.

### Risk: incorrect speaker attribution
Mitigation: keep output as "draft minutes"; secretary review mandatory.

### Risk: local model hallucinates details
Mitigation: strict prompt with "only use transcript facts" instruction and manual review.

### Risk: setup complexity
Mitigation: one-time setup by technical volunteer; committee uses only wrapper script.

## 9) Upgrade path (Phase 2 later)

- Add diarization/speaker segmentation
- Optional cloud STT fallback for difficult audio
- Add simple web UI with file upload
- Add action-item tracker integration

## 10) Free-cost reality

Software can be near-zero recurring cost.
Operational cost still exists in:

- one-time setup effort
- local compute/electricity
- human review time

This is still far cheaper and more controllable than full SaaS for many societies.
