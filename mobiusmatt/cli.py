"""Command line: ``mobiusmatt strip | torus | layout | letter``.

With ``--out`` a command writes a file headless (PNG, or GIF for the strip);
without it, it opens a matplotlib window.
"""

from __future__ import annotations

import argparse
import functools
import sys

from . import core
from .font import ALPHABET, Letter


def _word(text: str) -> str:
    try:
        return core.check_word(text)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e)) from None


def _positive(text: str) -> int:
    n = int(text)
    if n < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {n}")
    return n


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mobiusmatt",
        description="Write a word in a hand-drawn font on a Möbius strip or a torus.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("strip", help="the word cut out of a Möbius strip")
    s.add_argument("--word", type=_word, default="MATT",
                   help=f"letters from {ALPHABET} (default MATT)")
    s.add_argument("--times", type=_positive, default=1,
                   help="repeat the word this many times around the strip")
    s.add_argument("--out", help="write a .png still or a looping .gif instead of animating")
    s.add_argument("--frames", type=_positive, default=120, help="GIF frames (default 120)")
    s.add_argument("--width", type=_positive, default=480, help="GIF width in px (default 480)")
    s.add_argument("--fps", type=_positive, default=12, help="GIF frames per second (default 12)")

    t = sub.add_parser("torus", help="a torus made of the word, tiled both ways")
    t.add_argument("--word", type=_word, default="MATT")
    t.add_argument("--num-x", type=_positive, default=1, help="words per row (default 1)")
    t.add_argument("--num-y", type=_positive, default=1,
                   help="rows, in multiples of the word's length (default 1)")
    t.add_argument("--out", help="write a .png instead of opening a window")

    lay = sub.add_parser("layout", help="2D check: the unrolled strip with letters in place")
    lay.add_argument("--word", type=_word, default="MATT")
    lay.add_argument("--times", type=_positive, default=1)
    lay.add_argument("--out", help="write a .png instead of opening a window")

    le = sub.add_parser("letter", help="preview one letter of the font")
    le.add_argument("letter", choices=list(ALPHABET))
    le.add_argument("--out", help="write a .png instead of opening a window")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    out = args.out
    if out and not out.lower().endswith((".png", ".gif")):
        print(f"mobiusmatt: --out must end in .png or .gif: {out}", file=sys.stderr)
        return 2
    if out and out.lower().endswith(".gif") and args.command != "strip":
        print("mobiusmatt: only `strip` writes a GIF", file=sys.stderr)
        return 2

    from . import render  # imports matplotlib's 3D toolkit; keep --help fast

    if args.command == "strip":
        text = args.word * args.times
        _, (x, _, _) = core.cut_strip(args.word, args.times)
        cut = int((x != x).sum())
        print(f"{text}: {len(text)} letters, {cut} of {x.size} grid points cut out")
        if out and out.lower().endswith(".gif"):
            size = render.save_strip_gif(out, args.word, args.times,
                                         args.frames, args.width, args.fps)
            print(f"wrote {out} ({args.frames} frames, {args.width} px, "
                  f"{args.fps} fps, {size} bytes)")
        elif out:
            size = render.save_png(functools.partial(render.draw_strip, word=args.word,
                                                     times=args.times), out)
            print(f"wrote {out} ({size} bytes)")
        else:  # pragma: no cover - needs a display
            render.animate_strip(args.word, args.times)
        return 0

    if args.command == "torus":
        draw = functools.partial(render.draw_torus, word=args.word,
                                 num_x=args.num_x, num_y=args.num_y)
        n = len(core.torus_layout(args.word, args.num_x, args.num_y))
        print(f"{args.word} on a torus: {n} letters")
    elif args.command == "layout":
        draw = functools.partial(render.draw_layout, word=args.word, times=args.times)
        letters = core.strip_layout(args.word, args.times)
        for letter in letters:
            print(f"{letter.letter}  u = {letter.center[0]:.3f}")
    else:
        draw = functools.partial(render.draw_letter, letter=args.letter)
        border, hole = Letter(args.letter).placed()
        print(f"{args.letter}: {len(border)} border points, {len(hole)} hole points")

    if out:
        print(f"wrote {out} ({render.save_png(draw, out)} bytes)")
    else:  # pragma: no cover - needs a display
        render.show(draw)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
