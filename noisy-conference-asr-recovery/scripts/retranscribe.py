#!/usr/bin/env python3
"""Second-pass ASR with VAD off and a low no-speech threshold.

Default Whisper/Grok VAD is what dropped the noisy conference speech.
Do not turn VAD back on for the recovery pass.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_PROMPT = (
    "EU trade law academic conference in Beijing. "
    "Terms: Foreign Subsidies Regulation FSR, CSDDD, CBAM, ACI, NIS2, "
    "Cyber Resilience Act, Cybersecurity Act, Brussels effect, "
    "open strategic autonomy, WTO, state aid, distortion, subsidies, China, EU."
)


def main() -> None:
    p = argparse.ArgumentParser(description="faster-whisper with VAD off.")
    p.add_argument("--input", required=True)
    p.add_argument("--language", default="en")
    p.add_argument("--model", default="small.en")
    p.add_argument("--no-speech", type=float, default=0.2)
    p.add_argument("--prompt", default=DEFAULT_PROMPT)
    p.add_argument("--json-out", default="")
    args = p.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.stderr.write("faster_whisper not installed\n")
        raise SystemExit(1)

    model = WhisperModel(args.model, device="cpu", compute_type="int8", cpu_threads=2)
    kwargs = dict(
        vad_filter=False,
        no_speech_threshold=args.no_speech,
        beam_size=5,
        initial_prompt=args.prompt,
    )
    if args.language and args.language != "auto":
        kwargs["language"] = args.language

    segments, info = model.transcribe(args.input, **kwargs)
    rows = []
    for seg in segments:
        rec = {"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text.strip()}
        rows.append(rec)
        print(f"[{rec['start']:.2f}–{rec['end']:.2f}] {rec['text']}")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"wrote {args.json_out}  n={len(rows)}")


if __name__ == "__main__":
    main()
