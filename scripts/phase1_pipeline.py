#!/usr/bin/env python3
"""
Phase 1 meeting-minutes pipeline for Golf Meadows.

Flow:
1) Read local meeting media file
2) Transcribe locally with faster-whisper
3) Generate structured minutes with local Ollama model
4) Write transcript + minutes outputs into output directory
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import List

DEFAULT_WHISPER_MODEL = "small"
DEFAULT_OLLAMA_MODEL = "llama3.1:8b"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate housing society meeting minutes from recording."
    )
    parser.add_argument("--input", required=True, help="Path to meeting media file")
    parser.add_argument("--society", required=True, help="Society name")
    parser.add_argument("--meeting-date", required=True, help="Meeting date (YYYY-MM-DD)")
    parser.add_argument("--meeting-title", required=True, help="Meeting title")
    parser.add_argument(
        "--output-dir", default="./output", help="Directory for transcript/minutes output"
    )
    parser.add_argument(
        "--whisper-model",
        default=DEFAULT_WHISPER_MODEL,
        help="faster-whisper model name (tiny/base/small/medium/large-v3)",
    )
    parser.add_argument(
        "--ollama-model", default=DEFAULT_OLLAMA_MODEL, help="Local Ollama model name"
    )
    parser.add_argument(
        "--prompt-template",
        default="./templates/minutes_prompt.txt",
        help="Path to minutes prompt template file",
    )
    return parser.parse_args()


def validate_input_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")


def load_prompt_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8")


def transcribe_audio(input_path: Path, model_name: str) -> str:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'faster-whisper'. Install with: pip install -r requirements.txt"
        ) from exc

    # CPU + int8 is the safest default for low-cost environments.
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(input_path), beam_size=5)

    lines: List[str] = []
    lines.append(
        f"[transcription-meta] language={info.language} probability={info.language_probability:.3f}"
    )
    for segment in segments:
        lines.append(
            f"[{segment.start:8.2f}s -> {segment.end:8.2f}s] {segment.text.strip()}"
        )
    return "\n".join(lines).strip()


def call_ollama(prompt: str, model_name: str) -> str:
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'requests'. Install with: pip install -r requirements.txt"
        ) from exc

    payload = {"model": model_name, "prompt": prompt, "stream": False}
    response = requests.post(
        DEFAULT_OLLAMA_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=1800,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def write_output_files(
    output_dir: Path,
    meeting_slug: str,
    transcript_text: str,
    minutes_markdown: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    transcript_file = output_dir / f"{meeting_slug}_transcript.txt"
    minutes_file = output_dir / f"{meeting_slug}_minutes.md"

    transcript_file.write_text(transcript_text + "\n", encoding="utf-8")
    minutes_file.write_text(minutes_markdown + "\n", encoding="utf-8")

    print(f"Transcript written: {transcript_file}")
    print(f"Minutes written: {minutes_file}")


def make_meeting_slug(meeting_date: str, meeting_title: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in meeting_title)
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return f"{meeting_date}_{cleaned[:60]}"


def build_prompt(
    template_text: str,
    society: str,
    meeting_date: str,
    meeting_title: str,
    transcript_text: str,
) -> str:
    return template_text.format(
        society=society,
        meeting_date=meeting_date,
        meeting_title=meeting_title,
        transcript=transcript_text,
    )


def validate_date(date_str: str) -> None:
    dt.datetime.strptime(date_str, "%Y-%m-%d")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    prompt_path = Path(args.prompt_template).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    try:
        validate_input_file(input_path)
        validate_date(args.meeting_date)
        template_text = load_prompt_template(prompt_path)
    except Exception as exc:
        print(f"Input validation error: {exc}", file=sys.stderr)
        return 2

    print("Step 1/3: Transcribing meeting recording...")
    try:
        transcript_text = transcribe_audio(input_path, args.whisper_model)
    except Exception as exc:
        print(f"Transcription failed: {exc}", file=sys.stderr)
        return 3

    print("Step 2/3: Generating structured meeting minutes...")
    prompt = build_prompt(
        template_text=template_text,
        society=args.society,
        meeting_date=args.meeting_date,
        meeting_title=args.meeting_title,
        transcript_text=transcript_text,
    )
    try:
        minutes_markdown = call_ollama(prompt, args.ollama_model)
    except Exception as exc:
        print(
            "Minutes generation failed. Ensure Ollama is running and model is pulled. "
            f"Details: {exc}",
            file=sys.stderr,
        )
        return 4

    print("Step 3/3: Writing outputs...")
    meeting_slug = make_meeting_slug(args.meeting_date, args.meeting_title)
    write_output_files(
        output_dir=output_dir,
        meeting_slug=meeting_slug,
        transcript_text=transcript_text,
        minutes_markdown=minutes_markdown,
    )
    print("Done. Please run secretary review checklist before sharing minutes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
