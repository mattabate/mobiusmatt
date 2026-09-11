# mobiusmatt

The word MATT cut out of a Möbius strip, rendered in matplotlib. March–April 2024.

![MATT cut out of a Möbius strip, turning](mobius_matt.gif)

## What it does

`main.py` parameterises a Möbius strip on a fine grid, lays the letters of the
word end to end along its length, and punches each letter out of the surface:
every grid point that falls inside a letter's outline becomes NaN, so the strip
is drawn with letter-shaped holes. The surface is coloured by position around
the loop (the HSV colormap, so the colour cycles once per trip), and the camera
then rocks up and down while circling the strip, which is what you screen-record.

The letters cut all the way through, so they read from both faces of the strip
(mirrored from the back).

`torus.py` is the same trick turned inside out on a torus: the word is tiled in
both directions around the tube, each row shifted one letter along, and this
time everything *outside* the letters is removed, so the torus is made of
letters.

`matt_font.py` is the font: hand-drawn polygon outlines for M, A and T (A has a
hole), with `shift`, `rotate` and `stretch` so a letter can be placed anywhere
on the parameter grid. Only those three letters exist, which is enough for MATT.

## Run

```
pip install -r requirements.txt
python main.py                          # MATT on the strip, animated
python main.py --num_times 2            # MATTMATT, letters half as wide
python main.py --test                   # 2D check: the unrolled strip, letters
                                        # in place, coloured dots marking which
                                        # ends get glued (red to red, blue to blue)
python torus.py --num_x 2 --num_y 1     # MATT tiled around a torus
python matt_font.py                     # preview one letter
```

`--word` accepts any word spelled from the letters M, A and T.

The GIF above is `python make_gif.py`: the same strip, one turn of the camera
with two rocks of elevation, 120 frames at 12 fps, written headless with
Pillow (`pip install pillow` on top of the requirements).

## History

The first version was committed on 12 March 2024, alongside the SIGBOVIK
2024 code; the hand-drawn font, the torus and the version of `main.py` here
arrived on 1 April 2024. From then until September 2026 it lived at
`github.com/mattabate/wordplay/tree/main/mobiusmatt`. The commit history
stays in [wordplay](https://github.com/mattabate/wordplay).

## License

MIT.
