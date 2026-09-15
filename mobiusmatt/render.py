"""Drawing: turn the geometry in :mod:`mobiusmatt.core` into figures.

Functions that write files build a bare :class:`matplotlib.figure.Figure`, so
they work headless (no display, no pyplot state). :func:`animate_strip` and
:func:`show` use pyplot and need a window.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable

import matplotlib
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from . import core
from .font import Letter

_HSV = matplotlib.colormaps["hsv"]


def _colors(u: np.ndarray) -> np.ndarray:
    # Colour by position around the loop: the hue cycles once per trip.
    return _HSV(u / (2 * np.pi))


def draw_strip(fig: Figure, word: str = "MATT", times: int = 1, title: bool = True):
    """Draw the cut strip on ``fig``; return the 3D axes."""
    u, (x, y, z) = core.cut_strip(word, times)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(x, y, z, facecolors=_colors(u), edgecolor="none", alpha=0.6)
    if title:
        ax.set_title("Möbius Matt", fontsize=40)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)
    else:
        # The strip spans ±1.25 in x/y and ±0.1 in z: fit the box to it and
        # zoom so the letters are legible at README size.
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.set_zlim(-0.6, 0.6)
        ax.set_box_aspect((1, 1, 0.45), zoom=1.5)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_axis_off()
    ax.view_init(elev=30, azim=30)
    return ax


def draw_torus(fig: Figure, word: str = "MATT", num_x: int = 1, num_y: int = 1):
    """Draw the torus of letters on ``fig``, seen from above; return the axes."""
    radius = 2.0
    u, surfaces = core.letter_torus(word, num_x, num_y, R=radius, r=1.2)
    ax = fig.add_subplot(111, projection="3d")
    colors = _colors(u)
    for x, y, z in surfaces:
        ax.plot_surface(x, y, z, facecolors=colors, edgecolor="none", alpha=1)
    ax.set_title("Möbius Matt", fontsize=40)
    ax.set_xlim(-radius * 1.2, radius * 1.2)
    ax.set_ylim(-radius * 1.2, radius * 1.2)
    ax.set_zlim(-radius, radius)
    ax.set_axis_off()
    ax.view_init(elev=90, azim=30)
    return ax


def _draw_outlines(ax, letters: Iterable[Letter]) -> None:
    for letter in letters:
        border, hole = letter.placed()
        ax.add_patch(
            PathPatch(Path(border + border[:1]), facecolor="lightblue", lw=2, alpha=0.5)
        )
        if hole:
            ax.add_patch(PathPatch(Path(hole + hole[:1]), facecolor="white", lw=2))


def draw_layout(fig: Figure, word: str = "MATT", times: int = 1):
    """The unrolled strip: letter outlines in place, plus dots marking which
    corners get glued together (red to red, blue to blue)."""
    ax = fig.add_subplot(111)
    _draw_outlines(ax, core.strip_layout(word, times))
    ax.plot(2 * np.pi, 0.5, "ro", markersize=20)
    ax.plot(0, -0.5, "ro", markersize=20)
    ax.plot(2 * np.pi, -0.5, "bo", markersize=20)
    ax.plot(0, 0.5, "bo", markersize=20)
    ax.set_xlim(0, 2 * np.pi)
    ax.set_ylim(-0.5, 0.5)
    ax.set_aspect("equal")
    ax.set_title("2D Preview of Möbius Strip Layout")
    return ax


def draw_letter(fig: Figure, letter: str):
    """One letter of the font on its own."""
    ax = fig.add_subplot(111)
    _draw_outlines(ax, [Letter(letter)])
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_aspect("equal")
    ax.set_title(f"2D Preview of Letter '{letter}'")
    return ax


def save_png(draw: Callable[[Figure], object], out: str, dpi: int = 120) -> int:
    """Call ``draw(fig)`` on a fresh 8x6 inch figure, save it; return bytes written."""
    fig = Figure(figsize=(8, 6))
    draw(fig)
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    return os.path.getsize(out)


def save_strip_gif(
    out: str,
    word: str = "MATT",
    times: int = 1,
    frames: int = 120,
    width: int = 480,
    fps: int = 12,
    progress: Callable[[int], None] | None = None,
) -> int:
    """Write the looping GIF (the README's): one camera turn, two rocks.

    Returns bytes written. ``progress(k)`` is called after each frame.
    """
    from matplotlib.animation import PillowWriter

    dpi = 100
    fig = Figure(figsize=(width / dpi, width * 0.75 / dpi), dpi=dpi)
    ax = draw_strip(fig, word, times, title=False)
    writer = PillowWriter(fps=fps)
    with writer.saving(fig, out, dpi=dpi):
        for k, (elev, azim) in enumerate(core.camera_path(frames)):
            ax.view_init(elev=elev, azim=azim)
            writer.grab_frame()
            if progress:
                progress(k)
    return os.path.getsize(out)


def animate_strip(word: str = "MATT", times: int = 1) -> None:  # pragma: no cover
    """Open a window and circle the camera around the strip, rocking up and
    down, until the window is closed or Ctrl-C (for screen recording)."""
    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = draw_strip(fig, word, times)
    path = core.camera_path(400)
    try:
        k = 0
        while plt.fignum_exists(fig.number):
            ax.view_init(*path[k % len(path)])
            plt.draw()
            plt.pause(0.1)
            k += 1
    except KeyboardInterrupt:
        pass


def show(draw: Callable[[Figure], object]) -> None:  # pragma: no cover
    """Open a window with ``draw(fig)`` in it."""
    import matplotlib.pyplot as plt

    draw(plt.figure())
    plt.show()
