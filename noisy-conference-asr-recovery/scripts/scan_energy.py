#!/usr/bin/env python3
"""Per-second RMS scan. High energy + empty ASR => VAD drop, not silence.

Decode to raw s16le (not WAV) so WAVE_FORMAT_EXTENSIBLE headers cannot
shift the PCM and fake a quiet floor.
"""
from __future__ import annotations

import argparse
import math
import struct
import subprocess
import sys


def decode_pcm16(src: str, start: float | None, end: float | None) -> tuple[int, bytes]:
    sr = 16000
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    if start is not None:
        cmd += ["-ss", str(start)]
    cmd += ["-i", src]
    if start is not None and end is not None:
        cmd += ["-t", str(max(0.0, end - start))]
    elif end is not None and start is None:
        cmd += ["-t", str(end)]
    cmd += ["-ar", str(sr), "-ac", "1", "-f", "s16le", "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        raise SystemExit(proc.returncode)
    return sr, proc.stdout


def rms_by_second(sr: int, pcm: bytes) -> list[float]:
    n = len(pcm) // 2
    samples = struct.unpack("<" + "h" * n, pcm[: n * 2])
    out = []
    for i in range(0, n, sr):
        chunk = samples[i : i + sr]
        if not chunk:
            break
        acc = sum(s * s for s in chunk) / len(chunk)
        out.append(math.sqrt(acc) / 32768.0)
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Scan RMS per second; flag likely speech.")
    p.add_argument("--input", required=True)
    p.add_argument("--start", type=float, default=None, help="seconds")
    p.add_argument("--end", type=float, default=None, help="seconds")
    p.add_argument("--threshold", type=float, default=0.01, help="RMS above this ≈ not silence")
    args = p.parse_args()

    sr, pcm = decode_pcm16(args.input, args.start, args.end)
    series = rms_by_second(sr, pcm)
    if not series:
        print("no samples")
        return

    offset = args.start or 0.0
    speech = 0
    for i, rms in enumerate(series):
        t = offset + i
        flag = "SPEECH?" if rms >= args.threshold else "quiet"
        if rms >= args.threshold:
            speech += 1
        print(f"{t:8.1f}s  rms={rms:.4f}  {flag}")

    mean = sum(series) / len(series)
    peak = max(series)
    print("---")
    print(
        f"seconds={len(series)} mean_rms={mean:.4f} peak_rms={peak:.4f} "
        f"above_threshold={speech}/{len(series)}"
    )
    if speech > max(3, int(len(series) * 0.1)):
        print("VERDICT: energy present — do NOT treat as silence; run light extract + VAD-off ASR.")
    else:
        print("VERDICT: near floor — maybe true silence / mic off. Still do not invent speech.")


if __name__ == "__main__":
    main()
