"""Geometry: surfaces, letter layouts, and cutting letters out of a grid.

Everything here is pure (numpy in, numpy out, no drawing and no printing).
The one matplotlib import is :class:`matplotlib.path.Path`, used for its fast
vectorised point-in-polygon test.

A surface is parameterised by a grid of (u, v) points. Letters are polygons on
that same (u, v) plane, so "cutting a letter out" means setting every grid
point inside the letter to NaN; matplotlib leaves NaN cells undrawn.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from matplotlib.path import Path

from .font import ALPHABET, Letter, Point

Surface = tuple[np.ndarray, np.ndarray, np.ndarray]

#: Grid used for the strip: 800 steps around the loop, 100 across the width.
STRIP_GRID = (800, 100)
#: Grid used for the torus: 800 steps around the ring, 200 around the tube.
TORUS_GRID = (800, 200)


def check_word(word: str) -> str:
    """Return ``word`` unchanged if the font can spell it, else raise ValueError."""
    if not word:
        raise ValueError("word is empty")
    bad = sorted(set(word) - set(ALPHABET))
    if bad:
        raise ValueError(
            f"the font only has the letters {', '.join(ALPHABET)}; "
            f"{word!r} uses {', '.join(bad)}"
        )
    return word


def mobius_strip(u: np.ndarray, v: np.ndarray) -> Surface:
    """Map parameters to a Möbius strip of radius 1 and width 1.

    ``u`` runs around the loop in [0, 2π]; ``v`` runs across the strip in
    [-0.5, 0.5]. The strip makes a half twist, so the point (2π, v) is the
    point (0, -v).
    """
    x = (1 + v / 2 * np.cos(u / 2)) * np.cos(u)
    y = (1 + v / 2 * np.cos(u / 2)) * np.sin(u)
    z = v / 5 * np.sin(u / 2)
    return x, y, z


def torus(u: np.ndarray, v: np.ndarray, R: float = 1.0, r: float = 0.3) -> Surface:
    """Map parameters to a torus.

    ``u`` runs around the ring and ``v`` around the tube, both with period 2π.
    ``R`` is the distance from the centre of the torus to the centre of the
    tube, ``r`` the radius of the tube.
    """
    x = (R + r * np.cos(v)) * np.cos(u)
    y = (R + r * np.cos(v)) * np.sin(u)
    z = r * np.sin(v)
    return x, y, z


def inside_letter(
    border: Sequence[Point], hole: Sequence[Point], u: np.ndarray, v: np.ndarray
) -> np.ndarray:
    """Boolean mask, shaped like ``u``: which (u, v) points fall inside
    ``border`` and outside ``hole`` (pass an empty hole for none)."""
    points = np.column_stack((u.ravel(), v.ravel()))
    inside = Path(border).contains_points(points).reshape(u.shape)
    if len(hole):
        inside &= ~Path(hole).contains_points(points).reshape(u.shape)
    return inside


def strip_layout(word: str = "MATT", times: int = 1) -> list[Letter]:
    """Lay ``word`` repeated ``times`` times end to end along the strip.

    Each letter gets an equal share of the loop (2π / letters), is turned a
    quarter turn so it reads along the strip, and is placed right to left in
    ``u`` so that it reads left to right from outside the strip.
    """
    text = check_word(word) * times
    n = len(text)
    letters = []
    for i, ch in enumerate(text[::-1]):
        letter = Letter(ch)
        letter.stretch(1, 2 * np.pi / n)
        letter.rotate(-np.pi / 2)
        letter.shift(2 * i * np.pi / n + np.pi / n + 0.01, 0)
        letters.append(letter)
    return letters


def torus_layout(word: str = "MATT", num_x: int = 1, num_y: int = 1) -> list[Letter]:
    """Tile ``word`` over the torus's (u, v) square.

    Each row holds the word ``num_x`` times; there are ``num_y * len(word)``
    rows, and each row starts one letter later than the one above it, so the
    word also runs diagonally.
    """
    check_word(word)
    line = word * num_x
    rows = [line[i:] + line[:i] for i in range(num_y * len(word))]
    dx = 2 * np.pi / (num_x * len(word))
    dy = 2 * np.pi / (num_y * len(word))
    letters = []
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            letter = Letter(ch)
            letter.stretch(dx, dy)
            letter.shift(dx * (i + 1 / 2) + 0.01, -dy * (j + 1 / 2) + 0.01)
            letters.append(letter)
    return letters


def strip_grid(size: tuple[int, int] = STRIP_GRID) -> tuple[np.ndarray, np.ndarray]:
    """The (u, v) meshgrid for the strip: u in [0, 2π], v in [-0.5, 0.5]."""
    nu, nv = size
    return np.meshgrid(np.linspace(0, 2 * np.pi, nu), np.linspace(-0.5, 0.5, nv))


def torus_grid(size: tuple[int, int] = TORUS_GRID) -> tuple[np.ndarray, np.ndarray]:
    """The (u, v) meshgrid for the torus: u in [0, 2π], v in [-2π, 0]."""
    nu, nv = size
    return np.meshgrid(np.linspace(0, 2 * np.pi, nu), np.linspace(-2 * np.pi, 0, nv))


def cut_strip(
    word: str = "MATT", times: int = 1, grid: tuple[int, int] = STRIP_GRID
) -> tuple[np.ndarray, Surface]:
    """The Möbius strip with the letters punched out.

    Returns ``(u, (x, y, z))``; points inside a letter are NaN in x, y and z.
    ``u`` is returned for colouring by position around the loop.
    """
    u, v = strip_grid(grid)
    x, y, z = mobius_strip(u, v)
    for letter in strip_layout(word, times):
        cut = inside_letter(*letter.placed(), u, v)
        x[cut] = y[cut] = z[cut] = np.nan
    return u, (x, y, z)


def letter_torus(
    word: str = "MATT",
    num_x: int = 1,
    num_y: int = 1,
    R: float = 2.0,
    r: float = 1.2,
    grid: tuple[int, int] = TORUS_GRID,
) -> tuple[np.ndarray, list[Surface]]:
    """A torus made only of letters: one surface per letter, NaN outside it.

    Returns ``(u, surfaces)``.
    """
    u, v = torus_grid(grid)
    surfaces = []
    for letter in torus_layout(word, num_x, num_y):
        x, y, z = torus(u, v, R=R, r=r)
        outside = ~inside_letter(*letter.placed(), u, v)
        x[outside] = y[outside] = z[outside] = np.nan
        surfaces.append((x, y, z))
    return u, surfaces


def camera_path(
    frames: int, rocks: int = 2, elev: tuple[float, float] = (-40, 75), azim0: float = 30
) -> list[tuple[float, float]]:
    """``(elevation, azimuth)`` for each frame of a seamless loop.

    Azimuth turns a full 360° over the loop while elevation sweeps up and back
    down ``rocks`` times, so the frame after the last is the first again.
    """
    lo, hi = elev
    half = frames // (2 * rocks)
    path: list[float] = []
    for _ in range(rocks):
        path += list(np.linspace(lo, hi, half, endpoint=False))
        path += list(np.linspace(hi, lo, half, endpoint=False))
    path = (path + [lo] * frames)[:frames]
    return [(float(e), azim0 - 360 * k / frames) for k, e in enumerate(path)]
