from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
WRIST = 0
INDEX_MCP = 5
MIDDLE_MCP = 9
RING_MCP = 13
PINKY_MCP = 17

TIPS = (THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP)

HAND_CONNECTIONS: tuple[tuple[int, int], ...] = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17),
)


@dataclass(frozen=True)
class HandData:
    landmarks_px: np.ndarray
    landmarks_norm: np.ndarray
    handedness: str
    score: float

    def point(self, idx: int) -> tuple[int, int]:
        x, y = self.landmarks_px[idx]
        return int(round(float(x))), int(round(float(y)))

    def palm_center(self) -> tuple[int, int]:
        ids = (WRIST, INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP)
        center = self.landmarks_px[list(ids)].mean(axis=0)
        return int(round(float(center[0]))), int(round(float(center[1])))

    def hand_size(self) -> float:
        return float(np.linalg.norm(self.landmarks_px[WRIST] - self.landmarks_px[MIDDLE_MCP])) + 1e-6

    def openness(self) -> float:
        center = np.asarray(self.palm_center(), dtype=np.float32)
        tips = self.landmarks_px[list(TIPS)]
        return float(np.linalg.norm(tips - center, axis=1).mean()) / self.hand_size()

    def fingers_together(self, ratio: float = 0.35) -> bool:
        center = np.asarray(self.palm_center(), dtype=np.float32)
        tips = self.landmarks_px[list(TIPS)]
        return bool(np.all(np.linalg.norm(tips - center, axis=1) < self.hand_size() * ratio))


class HandTracker:
    def __init__(self, model_path: Path, max_hands: int = 2) -> None:
        options = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._ts_ms = 0

    def close(self) -> None:
        self._landmarker.close()

    def process(self, bgr: np.ndarray) -> list[HandData]:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self._ts_ms += 33
        result = self._landmarker.detect_for_video(image, self._ts_ms)
        height, width = bgr.shape[:2]
        hands: list[HandData] = []
        for i, landmarks in enumerate(result.hand_landmarks):
            norm = np.array([[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32)
            px = np.column_stack([norm[:, 0] * width, norm[:, 1] * height]).astype(np.float32)
            if result.handedness and i < len(result.handedness):
                category = result.handedness[i][0]
                label = category.category_name
                score = float(category.score)
            else:
                label, score = "Unknown", 0.0
            hands.append(HandData(landmarks_px=px, landmarks_norm=norm, handedness=label, score=score))
        return hands


def draw_hand_skeleton(
    frame: np.ndarray,
    hands: Sequence[HandData],
    color_points: tuple[int, int, int] = (40, 40, 255),
    color_lines: tuple[int, int, int] = (80, 220, 80),
) -> None:
    for hand in hands:
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, hand.point(a), hand.point(b), color_lines, 2, cv2.LINE_AA)
        for idx in range(21):
            cv2.circle(frame, hand.point(idx), 3, color_points, -1, cv2.LINE_AA)


def sort_hands_left_right(hands: Sequence[HandData]) -> tuple[HandData | None, HandData | None]:
    if not hands:
        return None, None
    if len(hands) == 1:
        return hands[0], None
    ordered = sorted(hands, key=lambda hand: hand.palm_center()[0])
    return ordered[0], ordered[1]


def portal_corners(left: HandData, right: HandData) -> np.ndarray:
    return np.array(
        [
            left.point(THUMB_TIP),
            left.point(INDEX_TIP),
            right.point(INDEX_TIP),
            right.point(THUMB_TIP),
        ],
        dtype=np.int32,
    )
