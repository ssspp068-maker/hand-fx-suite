from __future__ import annotations

import cv2
import numpy as np

FILTER_NAMES = ("invert", "gray", "thermal", "edges", "poster", "blur")


def apply_named_filter(bgr: np.ndarray, name: str) -> np.ndarray:
    if name == "invert":
        return cv2.bitwise_not(bgr)
    if name == "gray":
        return cv2.cvtColor(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    if name == "thermal":
        return cv2.applyColorMap(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_INFERNO)
    if name == "edges":
        edges = cv2.Canny(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY), 80, 160)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    if name == "poster":
        return (np.floor(bgr.astype(np.float32) / 255.0 * 4.0) / 4.0 * 255.0).astype(np.uint8)
    if name == "blur":
        return cv2.GaussianBlur(bgr, (31, 31), 0)
    return bgr.copy()


def stylize_anime_ish(bgr: np.ndarray) -> np.ndarray:
    soft = cv2.bilateralFilter(bgr, 9, 75, 75)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(
        cv2.medianBlur(gray, 7),
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        9,
        2,
    )
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    color = cv2.stylization(soft, sigma_s=60, sigma_r=0.35) if hasattr(cv2, "stylization") else soft
    return cv2.bitwise_and(color, edges_bgr)


def blend_masked(base: np.ndarray, overlay: np.ndarray, mask: np.ndarray) -> np.ndarray:
    if mask.ndim == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    alpha = (mask.astype(np.float32) / 255.0)[..., None]
    mixed = base.astype(np.float32) * (1.0 - alpha) + overlay.astype(np.float32) * alpha
    return np.clip(mixed, 0, 255).astype(np.uint8)


def fill_poly_mask(shape_hw: tuple[int, int], pts: np.ndarray) -> np.ndarray:
    mask = np.zeros(shape_hw, dtype=np.uint8)
    if pts is None or len(pts) < 3:
        return mask
    cv2.fillPoly(mask, [pts.astype(np.int32)], 255)
    return mask


def draw_wire_cube(
    frame: np.ndarray,
    center: tuple[int, int],
    size: int,
    color: tuple[int, int, int] = (220, 220, 220),
    thickness: int = 2,
) -> None:
    cx, cy = center
    side = max(12, int(size))
    front = np.array(
        [
            [cx - side, cy - side],
            [cx + side, cy - side],
            [cx + side, cy + side],
            [cx - side, cy + side],
        ],
        dtype=np.int32,
    )
    back = front + np.array([int(side * 0.55), -int(side * 0.55)], dtype=np.int32)
    for i in range(4):
        cv2.line(frame, tuple(front[i]), tuple(front[(i + 1) % 4]), color, thickness, cv2.LINE_AA)
        cv2.line(frame, tuple(back[i]), tuple(back[(i + 1) % 4]), color, thickness, cv2.LINE_AA)
        cv2.line(frame, tuple(front[i]), tuple(back[i]), color, thickness, cv2.LINE_AA)
