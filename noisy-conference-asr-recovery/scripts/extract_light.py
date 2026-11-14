#!/usr/bin/env python3
"""Light enhance only: highpass 100 Hz + gain. Never afftdn.

Strong spectral denoise smears fricatives and is worse than leaving the noise.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description="Highpass + gain only. No afftdn.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--start", type=float, default=0.0, help="seconds")
    p.add_argument("--duration", type=float, required=True, help="seconds")
    p.add_argument("--gain", type=float, default=10.0, help="dB, default 10; use 8 if clipping")
    p.add_argument("--highpass", type=int, default=100)
    p.add_argument("--lowpass", type=int, default=7000)
    args = p.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    af = f"highpass=f={args.highpass},lowpass=f={args.lowpass},volume={args.gain}dB"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(args.start), "-t", str(args.duration),
        "-i", args.input,
        "-af", af,
        "-ar", "16000", "-ac", "1",
        "-c:a", "pcm_s16le", "-f", "wav", "-bitexact",
        args.output,
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        raise SystemExit(proc.returncode)
    print(f"wrote {args.output}  filter={af}")


if __name__ == "__main__":
    main()
