from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from core.fx import blend_masked, fill_poly_mask, stylize_anime_ish
from core.hands import HandData, draw_hand_skeleton, portal_corners, sort_hands_left_right


class StyleMaskMode:
    name = "4 Style Mask"

    def __init__(self, assets_dir: Path) -> None:
        self.show_skeleton = False
        self.shape_idx = 0
        self.overlay_still: np.ndarray | None = None
        for name in ("style_overlay.png", "style_overlay.jpg", "style_overlay.jpeg"):
            path = assets_dir / name
            if path.exists():
                image = cv2.imread(str(path), cv2.IMREAD_COLOR)
                if image is not None:
                    self.overlay_still = image
                    break

    def on_key(self, key: int) -> None:
        if key in (ord("f"), ord("F")):
            self.shape_idx = (self.shape_idx + 1) % 3
        elif key in (ord("g"), ord("G")):
            self.show_skeleton = not self.show_skeleton

    def _shape_points(self, hands: list[HandData], frame_shape: tuple[int, ...]) -> np.ndarray | None:
        left, right = sort_hands_left_right(hands)
        height, width = frame_shape[:2]

        if self.shape_idx == 2:
            if not hands:
                return None
            y = int(sum(hand.palm_center()[1] for hand in hands) / len(hands))
            band = max(40, int(0.12 * height))
            return np.array(
                [[0, y - band], [width - 1, y - band], [width - 1, y + band], [0, y + band]],
                dtype=np.int32,
            )

        if left is None or right is None:
            if not hands:
                return None
            hand = hands[0]
            cx, cy = hand.palm_center()
            side = int(hand.hand_size() * 1.2)
            return np.array(
                [[cx, cy - side], [cx + side, cy], [cx, cy + side], [cx - side, cy]],
                dtype=np.int32,
            )

        if self.shape_idx == 0:
            return portal_corners(left, right)

        lx, ly = left.palm_center()
        rx, ry = right.palm_center()
        mx, my = (lx + rx) // 2, (ly + ry) // 2
        dx = max(40, abs(rx - lx) // 2)
        dy = max(40, abs(ry - ly) // 2 + int(left.hand_size()))
        return np.array([[mx, my - dy], [mx + dx, my], [mx, my + dy], [mx - dx, my]], dtype=np.int32)

    def render(self, frame: np.ndarray, hands: list[HandData]) -> np.ndarray:
        out = frame.copy()
        if self.overlay_still is None:
            styled = stylize_anime_ish(frame)
            source = "live stylize"
        else:
            styled = cv2.resize(self.overlay_still, (frame.shape[1], frame.shape[0]))
            source = "assets overlay"

        points = self._shape_points(hands, frame.shape)
        shapes = ("quad", "diamond", "strip")
        if points is not None:
            mask = cv2.GaussianBlur(fill_poly_mask(frame.shape[:2], points), (15, 15), 0)
            out = blend_masked(frame, styled, mask)
            cv2.polylines(out, [points.reshape(-1, 1, 2)], True, (255, 255, 255), 2, cv2.LINE_AA)

        if self.show_skeleton:
            draw_hand_skeleton(out, hands)

        label = f"{self.name} | shape={shapes[self.shape_idx]} [F] | {source}"
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (240, 240, 240), 1, cv2.LINE_AA)
        return out
