"""mobiusmatt: write a word in a hand-drawn font on a Möbius strip or a torus.

The letters are polygons on a surface's (u, v) parameter plane. On the strip
they are cut out (grid points inside a letter become NaN); on the torus
everything outside them is, so the torus is made of letters.

    >>> from mobiusmatt import cut_strip
    >>> u, (x, y, z) = cut_strip("MATT")

Drawing lives in :mod:`mobiusmatt.render`; the command line in
:mod:`mobiusmatt.cli`.
"""

from .core import (
    camera_path,
    check_word,
    cut_strip,
    inside_letter,
    letter_torus,
    mobius_strip,
    strip_layout,
    torus,
    torus_layout,
)
from .font import ALPHABET, Letter

__all__ = [
    "ALPHABET",
    "Letter",
    "camera_path",
    "check_word",
    "cut_strip",
    "inside_letter",
    "letter_torus",
    "mobius_strip",
    "strip_layout",
    "torus",
    "torus_layout",
]
