from __future__ import annotations

from collections import deque

import cv2
import numpy as np

from core.hands import TIPS, HandData, draw_hand_skeleton


class TrailsMode:
    name = "5 Trails"

    def __init__(self, history: int = 24) -> None:
        self.show_skeleton = True
        self.show_blobs = True
        self.trails: dict[str, deque[tuple[int, int]]] = {}
        self.history = history

    def on_key(self, key: int) -> None:
        if key in (ord("g"), ord("G")):
            self.show_skeleton = not self.show_skeleton
        elif key in (ord("v"), ord("V")):
            self.show_blobs = not self.show_blobs
        elif key in (ord("c"), ord("C")):
            self.trails.clear()

    def render(self, frame: np.ndarray, hands: list[HandData]) -> np.ndarray:
        out = frame.copy()
        overlay = np.zeros_like(out)
        active: set[str] = set()

        for hand_index, hand in enumerate(hands):
            if self.show_blobs:
                cx, cy = hand.palm_center()
                radius = int(hand.hand_size() * 0.9)
                cv2.circle(overlay, (cx, cy), radius, (35, 35, 35), -1, cv2.LINE_AA)
                cv2.circle(out, (cx, cy), radius, (220, 220, 220), 2, cv2.LINE_AA)

            for tip in TIPS:
                key = f"{hand_index}:{tip}"
                active.add(key)
                point = hand.point(tip)
                trail = self.trails.setdefault(key, deque(maxlen=self.history))
                trail.append(point)
                points = list(trail)
                for i in range(1, len(points)):
                    t = i / len(points)
                    color = (int(80 + 160 * t), int(120 + 100 * t), int(255 * t))
                    cv2.line(out, points[i - 1], points[i], color, 2 + int(2 * t), cv2.LINE_AA)
                cv2.circle(out, point, 4, (255, 255, 255), -1, cv2.LINE_AA)

        if self.show_blobs and len(hands) >= 2:
            cv2.line(out, hands[0].palm_center(), hands[1].palm_center(), (180, 180, 180), 1, cv2.LINE_AA)

        for key in list(self.trails):
            if key not in active:
                self.trails[key].clear()

        if self.show_blobs:
            out = cv2.addWeighted(out, 1.0, overlay, 0.25, 0)
        if self.show_skeleton:
            draw_hand_skeleton(out, hands)

        label = f"{self.name} | trails + blobs [V] [G] skeleton [C] clear"
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (240, 240, 240), 1, cv2.LINE_AA)
        return out
