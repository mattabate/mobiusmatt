"""The hand-drawn font: polygon outlines for M, A and T.

Each letter is drawn in a box about 0.8 wide and 0.65 tall, centred on the
origin. ``A`` is the only letter with a hole. Points marked "extra" add no
corners; they sit on straight edges so the outline samples evenly when drawn.
"""

from __future__ import annotations

import math

Point = tuple[float, float]

ALPHABET = "MAT"

_BORDERS: dict[str, list[Point]] = {
    "M": [
        (-0.05, -0.20),
        (-0.17, -0.005),
        (-0.2, -0.32),
        (-0.4, -0.32),
        (-0.3, 0.31),
        (-0.1, 0.31),
        (0.0, 0.06),
        (0.1, 0.31),
        (0.3, 0.31),
        (0.4, -0.32),
        (0.2, -0.32),
        (0.17, -0.005),
        (0.05, -0.20),
    ],
    "T": [
        (-0.1, -0.33),
        (-0.1, -0.05),  # extra
        (-0.1, 0.2),
        (-0.25, 0.2),  # extra
        (-0.4, 0.2),
        (-0.4, 0.25),  # extra
        (-0.4, 0.32),
        (0, 0.32),  # extra
        (0.4, 0.32),
        (0.4, 0.25),  # extra
        (0.4, 0.2),
        (0.25, 0.2),  # extra
        (0.1, 0.2),
        (0.1, 0.05),  # extra
        (0.1, -0.33),
    ],
    "A": [
        (0.2, 0.31),
        (0.35, -0.32),
        (0.25, -0.32),  # extra
        (0.15, -0.32),
        (0.1, -0.07),
        (0.0, -0.07),  # extra
        (-0.1, -0.07),
        (-0.15, -0.32),
        (-0.25, -0.32),  # extra
        (-0.35, -0.32),
        (-0.2, 0.31),
    ],
}

_HOLES: dict[str, list[Point]] = {
    "A": [
        (-0.1, 0.06),
        (-0.05, 0.06),  # extra
        (0, 0.06),  # extra
        (0.05, 0.06),  # extra
        (0.1, 0.06),
        (0.1, 0.19),
        (0.05, 0.19),  # extra
        (0.0, 0.19),  # extra
        (-0.05, 0.19),  # extra
        (-0.1, 0.19),
    ],
}


class Letter:
    """One letter's outline, placed somewhere on the (u, v) parameter plane.

    ``border`` and ``hole`` are polygons relative to ``center``; ``stretch``
    and ``rotate`` reshape them about the origin and ``shift`` moves
    ``center``. Use :meth:`placed` for absolute coordinates.
    """

    def __init__(self, letter: str) -> None:
        if len(letter) != 1 or letter not in ALPHABET:
            raise ValueError(f"Unknown letter: {letter!r} (the font has {ALPHABET})")
        self.letter = letter
        self.center: Point = (0.0, 0.0)
        self.border: list[Point] = list(_BORDERS[letter])
        self.hole: list[Point] = list(_HOLES.get(letter, []))

    def shift(self, dx: float, dy: float) -> None:
        """Move the letter by (dx, dy)."""
        self.center = (self.center[0] + dx, self.center[1] + dy)

    def rotate(self, angle: float) -> None:
        """Rotate the outline counter-clockwise by ``angle`` radians."""
        c, s = math.cos(angle), math.sin(angle)
        self.border = [(x * c - y * s, x * s + y * c) for x, y in self.border]
        self.hole = [(x * c - y * s, x * s + y * c) for x, y in self.hole]

    def stretch(self, sx: float, sy: float) -> None:
        """Scale the outline by ``sx`` horizontally and ``sy`` vertically."""
        self.border = [(x * sx, y * sy) for x, y in self.border]
        self.hole = [(x * sx, y * sy) for x, y in self.hole]

    def placed(self) -> tuple[list[Point], list[Point]]:
        """Return ``(border, hole)`` in absolute coordinates."""
        cx, cy = self.center
        return (
            [(x + cx, y + cy) for x, y in self.border],
            [(x + cx, y + cy) for x, y in self.hole],
        )

    def __repr__(self) -> str:
        return f"Letter({self.letter!r}, center={self.center})"
