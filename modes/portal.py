from __future__ import annotations

import cv2
import numpy as np

from core.fx import FILTER_NAMES, apply_named_filter, blend_masked, fill_poly_mask
from core.hands import HandData, draw_hand_skeleton, portal_corners, sort_hands_left_right
from modes._helpers import any_fingers_together


class PortalMode:
    name = "1 Portal"

    def __init__(self) -> None:
        self.filter_idx = 0
        self.locked_poly: np.ndarray | None = None
        self.show_skeleton = True

    def on_key(self, key: int) -> None:
        if key in (ord("f"), ord("F")):
            self.filter_idx = (self.filter_idx + 1) % len(FILTER_NAMES)
        elif key in (ord("g"), ord("G")):
            self.show_skeleton = not self.show_skeleton
        elif key in (ord("r"), ord("R")):
            self.locked_poly = None

    def render(self, frame: np.ndarray, hands: list[HandData]) -> np.ndarray:
        out = frame.copy()
        left, right = sort_hands_left_right(hands)
        filt = FILTER_NAMES[self.filter_idx]
        locking = any_fingers_together(hands, 0.32)

        if left is not None and right is not None:
            live = portal_corners(left, right)
            if locking:
                if self.locked_poly is None:
                    self.locked_poly = live.copy()
                poly = self.locked_poly
            else:
                self.locked_poly = None
                poly = live

            filtered = apply_named_filter(frame, filt)
            mask = cv2.GaussianBlur(fill_poly_mask(frame.shape[:2], poly), (21, 21), 0)
            out = blend_masked(frame, filtered, mask)
            cv2.polylines(out, [poly.reshape(-1, 1, 2)], True, (255, 255, 255), 2, cv2.LINE_AA)

        if self.show_skeleton:
            draw_hand_skeleton(out, hands)

        state = "LOCKED" if locking and self.locked_poly is not None else "live"
        label = f"{self.name} | {filt} [F] | portal={state} fist=lock [R]reset"
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (240, 240, 240), 1, cv2.LINE_AA)
        return out
