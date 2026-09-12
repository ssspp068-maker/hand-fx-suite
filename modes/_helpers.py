from __future__ import annotations

from core.hands import HandData


def any_fingers_together(hands: list[HandData], ratio: float = 0.35) -> bool:
    return any(hand.fingers_together(ratio) for hand in hands)
