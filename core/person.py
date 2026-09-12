from __future__ import annotations

from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision


class PersonSegmenter:
    def __init__(self, model_path: Path) -> None:
        options = vision.ImageSegmenterOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            output_category_mask=True,
        )
        self._segmenter = vision.ImageSegmenter.create_from_options(options)
        self._ts_ms = 0

    def close(self) -> None:
        self._segmenter.close()

    def mask(self, bgr: np.ndarray) -> np.ndarray:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self._ts_ms += 33
        result = self._segmenter.segment_for_video(image, self._ts_ms)
        if result.category_mask is None:
            return np.zeros(bgr.shape[:2], dtype=np.uint8)
        raw = result.category_mask.numpy_view()
        person = (raw > 0).astype(np.uint8) * 255
        return cv2.GaussianBlur(person, (7, 7), 0)
