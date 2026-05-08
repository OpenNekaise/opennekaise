#!/usr/bin/env python3
"""Convert text to speech via OpenAI's /v1/audio/speech endpoint.

Reads the text from --text or stdin, sends it to the TTS API, and writes
the returned audio bytes under /workspace/group/audio/. Prints the
absolute container path on success.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

API_URL = "https://api.openai.com/v1/audio/speech"
OUT_DIR = Path("/workspace/group/audio")

VALID_VOICES = [
    "alloy", "ash", "ballad", "coral", "echo",
    "fable", "nova", "onyx", "sage", "shimmer", "verse",
]
VALID_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]


def slugify(text: str, fallback: str = "reply") -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]
    return s or fallback


def main() -> int:
    p = argparse.ArgumentParser(
        description="Convert text to speech via OpenAI TTS."
    )
    p.add_argument("--text", help="Text to speak. If omitted, read from stdin.")
    p.add_argument("--voice", default="alloy", choices=VALID_VOICES)
    p.add_argument("--format", default="mp3", choices=VALID_FORMATS, dest="fmt")
    p.add_argument(
        "--model",
        default="gpt-4o-mini-tts",
        help="TTS model (default: gpt-4o-mini-tts; alternatives: tts-1, tts-1-hd).",
    )
    p.add_argument("--name", help="Override the filename slug.")
    args = p.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.stderr.write(
            "ERROR: OPENAI_API_KEY not set. Add it to the host .env "
            "and restart the opennekaise service.\n"
        )
        return 2

    text = args.text if args.text is not None else sys.stdin.read()
    text = text.strip()
    if not text:
        sys.stderr.write("ERROR: empty text. Pass --text or pipe via stdin.\n")
        return 2

    body = {
        "model": args.model,
        "voice": args.voice,
        "input": text,
        "response_format": args.fmt,
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            audio_bytes = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:1000]
        sys.stderr.write(f"OpenAI API error {e.code}: {detail}\n")
        return 1
    except urllib.error.URLError as e:
        sys.stderr.write(f"Network error: {e}\n")
        return 1

    if not audio_bytes:
        sys.stderr.write("Empty audio response from API.\n")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = args.name or slugify(text)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = OUT_DIR / f"{stamp}-{slug}.{args.fmt}"
    out_path.write_bytes(audio_bytes)

    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
