from __future__ import annotations

import math

import cv2
import numpy as np

from core.fx import draw_wire_cube
from core.hands import INDEX_TIP, THUMB_TIP, HandData, draw_hand_skeleton


class CubesMode:
    name = "3 Cubes"

    def __init__(self) -> None:
        self.show_skeleton = True
        self.spin = 0.0

    def on_key(self, key: int) -> None:
        if key in (ord("g"), ord("G")):
            self.show_skeleton = not self.show_skeleton

    def render(self, frame: np.ndarray, hands: list[HandData]) -> np.ndarray:
        out = frame.copy()
        self.spin += 0.08

        for hand in hands:
            cx, cy = hand.palm_center()
            size = int(hand.hand_size() * (0.55 + 0.35 * min(hand.openness(), 2.0)))
            ox = int(6 * math.cos(self.spin + hand.score))
            oy = int(6 * math.sin(self.spin + hand.score))
            draw_wire_cube(out, (cx + ox, cy + oy), size)

            thumb = hand.landmarks_px[THUMB_TIP]
            index = hand.landmarks_px[INDEX_TIP]
            if float(np.linalg.norm(thumb - index)) < hand.hand_size() * 0.55:
                mid = ((thumb + index) / 2.0).astype(int)
                draw_wire_cube(out, (int(mid[0]), int(mid[1])), max(10, size // 3), color=(180, 120, 255))

        if len(hands) >= 2:
            a = hands[0].palm_center()
            b = hands[1].palm_center()
            mid = ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
            span = int(0.25 * math.hypot(a[0] - b[0], a[1] - b[1]))
            draw_wire_cube(out, mid, max(14, span), color=(120, 220, 255))
            cv2.line(out, a, b, (120, 220, 255), 1, cv2.LINE_AA)

        if self.show_skeleton:
            draw_hand_skeleton(out, hands)

        label = f"{self.name} | cubes on palms / pinch / between hands [G]"
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1, cv2.LINE_AA)
        return out
