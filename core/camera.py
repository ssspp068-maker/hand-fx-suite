from __future__ import annotations

import sys
from typing import Optional

import cv2


def open_camera(index: int = 0, width: int = 1280, height: int = 720) -> cv2.VideoCapture:
    """Open webcam. Prefer DirectShow on Windows."""
    backends: list[tuple[int, str]] = []
    if sys.platform.startswith("win"):
        backends.append((cv2.CAP_DSHOW, "CAP_DSHOW"))
    backends.append((cv2.CAP_ANY, "CAP_ANY"))

    last_error = ""
    for backend, name in backends:
        cap = cv2.VideoCapture(index, backend)
        if not cap.isOpened():
            last_error = f"{name} failed to open index {index}"
            cap.release()
            continue
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        ok, frame = cap.read()
        if not ok or frame is None:
            last_error = f"{name} opened but delivered no frame"
            cap.release()
            continue
        return cap

    raise RuntimeError(
        f"Cannot open camera {index}. Last error: {last_error or 'unknown'}. "
        "Close other apps using the webcam, then retry."
    )


def read_frame(cap: cv2.VideoCapture) -> Optional[object]:
    ok, frame = cap.read()
    if not ok or frame is None:
        return None
    return frame
