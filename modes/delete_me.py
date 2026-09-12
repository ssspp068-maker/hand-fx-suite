from __future__ import annotations

import cv2
import numpy as np

from core.hands import HandData, draw_hand_skeleton
from core.person import PersonSegmenter


class DeleteMeMode:
    name = "2 Delete Me"

    def __init__(self, segmenter: PersonSegmenter) -> None:
        self.segmenter = segmenter
        self.background: np.ndarray | None = None
        self.enabled = True
        self.show_hitbox = True
        self.show_skeleton = False
        self._capture_next = False

    def on_key(self, key: int) -> None:
        if key in (ord("b"), ord("B")):
            self._capture_next = True
        elif key in (ord("e"), ord("E")):
            self.enabled = not self.enabled
        elif key in (ord("x"), ord("X")):
            self.show_hitbox = not self.show_hitbox
        elif key in (ord("g"), ord("G")):
            self.show_skeleton = not self.show_skeleton

    def render(self, frame: np.ndarray, hands: list[HandData]) -> np.ndarray:
        out = frame.copy()
        if self._capture_next:
            self.background = frame.copy()
            self._capture_next = False

        if self.background is None:
            msg = "Step OUT of frame, press [B] to capture background"
            cv2.putText(out, msg, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(out, msg, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 1, cv2.LINE_AA)
            return out

        if self.enabled:
            bg = self.background
            if bg.shape[:2] != frame.shape[:2]:
                bg = cv2.resize(bg, (frame.shape[1], frame.shape[0]))
            person = self.segmenter.mask(frame)
            alpha = (person.astype(np.float32) / 255.0)[..., None]
            out = (frame.astype(np.float32) * (1.0 - alpha) + bg.astype(np.float32) * alpha).astype(np.uint8)
            if self.show_hitbox:
                ys, xs = np.where(person > 127)
                if len(xs):
                    cv2.rectangle(
                        out,
                        (int(xs.min()), int(ys.min())),
                        (int(xs.max()), int(ys.max())),
                        (0, 255, 0),
                        2,
                    )

        if self.show_skeleton:
            draw_hand_skeleton(out, hands)

        label = (
            f"{self.name} | {'ON' if self.enabled else 'OFF'} [E] | "
            f"hitbox={'on' if self.show_hitbox else 'off'} [X] | [B] bg"
        )
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(out, label, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1, cv2.LINE_AA)
        return out
