from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

import cv2

from core.camera import open_camera, read_frame
from core.hands import HandTracker
from core.person import PersonSegmenter
from modes.cubes import CubesMode
from modes.delete_me import DeleteMeMode
from modes.portal import PortalMode
from modes.style_mask import StyleMaskMode
from modes.trails import TrailsMode

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
ASSETS = ROOT / "assets"
SHOTS = ROOT / "screenshots"


HELP_LINES = [
    "1 Portal | 2 Delete Me | 3 Cubes | 4 Style Mask | 5 Trails",
    "M mirror | H help | S screenshot | Q quit",
    "Mode keys: F filter/shape | B capture bg | E enable | X hitbox | G skeleton | V blobs | C clear | R reset",
]


def draw_hud(frame, mode_name: str, fps: float, show_help: bool) -> None:
    cv2.putText(
        frame,
        f"{mode_name} | {fps:.0f} fps | keys 1-5",
        (16, frame.shape[0] - 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 0),
        3,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        f"{mode_name} | {fps:.0f} fps | keys 1-5",
        (16, frame.shape[0] - 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (230, 230, 230),
        1,
        cv2.LINE_AA,
    )
    if show_help:
        y = 70
        for line in HELP_LINES:
            cv2.putText(frame, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            y += 22


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hand FX Suite — 5 Instagram-style CV demos in one app")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (default 0)")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--mode", type=int, default=1, choices=range(1, 6), help="Start mode 1..5")
    parser.add_argument("--no-mirror", action="store_true", help="Disable selfie mirror")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hand_model = MODELS / "hand_landmarker.task"
    person_model = MODELS / "selfie_segmenter.tflite"
    if not hand_model.exists() or not person_model.exists():
        raise FileNotFoundError(
            f"Missing model files in {MODELS}. Expected hand_landmarker.task and selfie_segmenter.tflite. "
            "Run: python scripts/download_models.py"
        )

    try:
        tracker = HandTracker(hand_model)
        segmenter = PersonSegmenter(person_model)
    except AttributeError as exc:
        if "free" in str(exc).lower():
            raise SystemExit(
                "MediaPipe broken (function 'free' not found).\n"
                "Fix: delete the .venv folder, then run run.bat again.\n"
                "Need mediapipe>=0.10.31 (not 0.10.30)."
            ) from exc
        raise

    modes = {
        1: PortalMode(),
        2: DeleteMeMode(segmenter),
        3: CubesMode(),
        4: StyleMaskMode(ASSETS),
        5: TrailsMode(),
    }
    mode_id = args.mode
    mirror = not args.no_mirror
    show_help = True

    cap = open_camera(args.camera, args.width, args.height)
    window = "Hand FX Suite"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    prev = time.perf_counter()
    fps = 0.0
    SHOTS.mkdir(exist_ok=True)

    try:
        while True:
            frame = read_frame(cap)
            if frame is None:
                continue
            if mirror:
                frame = cv2.flip(frame, 1)

            hands = tracker.process(frame)
            mode = modes[mode_id]
            out = mode.render(frame, hands)

            now = time.perf_counter()
            dt = now - prev
            prev = now
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt)

            draw_hud(out, mode.name, fps, show_help)
            cv2.imshow(window, out)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
            if key in (ord("1"), ord("2"), ord("3"), ord("4"), ord("5")):
                mode_id = int(chr(key))
            elif key in (ord("m"), ord("M")):
                mirror = not mirror
            elif key in (ord("h"), ord("H")):
                show_help = not show_help
            elif key in (ord("s"), ord("S")):
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = SHOTS / f"mode{mode_id}_{stamp}.png"
                cv2.imwrite(str(path), out)
                print(f"saved {path}")
            else:
                mode.on_key(key)
    finally:
        cap.release()
        tracker.close()
        segmenter.close()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
