#!/usr/bin/env python3
"""Download MediaPipe model files into ./models (run once after clone)."""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
MODELS.mkdir(exist_ok=True)

FILES = {
    "hand_landmarker.task": (
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    ),
    "selfie_segmenter.tflite": (
        "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite"
    ),
}


def main() -> int:
    for name, url in FILES.items():
        dest = MODELS / name
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"OK exists: {dest} ({dest.stat().st_size} bytes)")
            continue
        print(f"Downloading {name} ...")
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as exc:
            print(f"FAIL {name}: {exc}", file=sys.stderr)
            return 1
        print(f"OK saved: {dest} ({dest.stat().st_size} bytes)")
    print("Done. Models are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
