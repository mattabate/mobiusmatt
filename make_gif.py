"""Render the README's looping GIF: MATT cut out of a Möbius strip, the
camera circling once while the view rocks up and down. Headless.

    python make_gif.py [out.gif] [frames] [width_px] [fps]

Defaults: mobius_matt.gif, 120 frames, 480 px wide, 12 fps. One full turn
of azimuth with two rocks of elevation, so the last frame meets the first.
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import PillowWriter  # noqa: E402

from main import is_inside_complex_polygon, mobius_strip  # noqa: E402
from matt_font import Letter  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else "mobius_matt.gif"
frames = int(sys.argv[2]) if len(sys.argv) > 2 else 120
width = int(sys.argv[3]) if len(sys.argv) > 3 else 480
fps = int(sys.argv[4]) if len(sys.argv) > 4 else 12
word = "MATT"

# The strip with the letters punched out, exactly as main.py builds it.
masks = []
for i, letter in enumerate(word[::-1]):
    m = Letter(letter=letter)
    m.stretch(1, 2 * np.pi / len(word))
    m.rotate(-np.pi / 2)
    m.shift(2 * i * np.pi / len(word) + np.pi / len(word) + 0.01, 0)
    masks.append(m)

u = np.linspace(0, 2 * np.pi, 800)
v = np.linspace(-0.5, 0.5, 100)
u, v = np.meshgrid(u, v)
x, y, z = mobius_strip(u, v)
for m in masks:
    border = [(px + m.center[0], py + m.center[1]) for px, py in m.border]
    hole = [(px + m.center[0], py + m.center[1]) for px, py in m.hole]
    inside = is_inside_complex_polygon(border, hole, u, v)
    x[inside], y[inside], z[inside] = np.nan, np.nan, np.nan

dpi = 100
fig = plt.figure(figsize=(width / dpi, width * 0.75 / dpi), dpi=dpi)
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(x, y, z, facecolors=plt.cm.hsv(u / (2 * np.pi)), edgecolor="none", alpha=0.6)
ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-1.3, 1.3)
ax.set_zlim(-0.6, 0.6)
ax.set_box_aspect((1, 1, 0.45), zoom=1.5)
ax.set_axis_off()
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

# Camera: elevation rocks between -40 and 75 like main.py's animation, twice
# per turn; azimuth turns through 360 over the loop.
elev_lo, elev_hi, rocks = -40, 75, 2
half = frames // (2 * rocks)
elev_path = []
for _ in range(rocks):
    elev_path += list(np.linspace(elev_lo, elev_hi, half, endpoint=False))
    elev_path += list(np.linspace(elev_hi, elev_lo, half, endpoint=False))
elev_path = (elev_path + [elev_lo] * frames)[:frames]

writer = PillowWriter(fps=fps)
with writer.saving(fig, out, dpi=dpi):
    for k in range(frames):
        ax.view_init(elev=elev_path[k], azim=30 - 360 * k / frames)
        writer.grab_frame()
print("wrote", out, os.path.getsize(out), "bytes")
