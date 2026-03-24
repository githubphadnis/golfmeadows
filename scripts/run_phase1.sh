#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Golf Meadows Phase 1 Minutes Generator"
echo "-------------------------------------"

read -r -p "Input recording path (audio/video file): " INPUT_FILE
read -r -p "Society name [Golf Meadows]: " SOCIETY
read -r -p "Meeting date (YYYY-MM-DD): " MEETING_DATE
read -r -p "Meeting title: " MEETING_TITLE

if [[ -z "${SOCIETY}" ]]; then
  SOCIETY="Golf Meadows"
fi

if [[ -z "${INPUT_FILE}" || -z "${MEETING_DATE}" || -z "${MEETING_TITLE}" ]]; then
  echo "Error: input file, meeting date, and meeting title are required." >&2
  exit 2
fi

python3 "${ROOT_DIR}/scripts/phase1_pipeline.py" \
  --input "${INPUT_FILE}" \
  --society "${SOCIETY}" \
  --meeting-date "${MEETING_DATE}" \
  --meeting-title "${MEETING_TITLE}" \
  --output-dir "${ROOT_DIR}/output"

echo "Generated files are in: ${ROOT_DIR}/output"
