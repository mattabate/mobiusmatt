import numpy as np
import pytest

import mobiusmatt
from mobiusmatt import (
    Letter,
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
from mobiusmatt.cli import main

# Pinned from the original main.py / torus.py (the 2024 scripts this package
# replaces), run on the same grids: the refactor is bit-identical to them.
STRIP_CUT = {("MATT", 1): 19958, ("MATT", 2): 19972, ("TAM", 1): 21196}
TORUS_KEPT = {("MATT", 1, 1): (16, 39892), ("AT", 1, 2): (8, 36535)}


# --- surfaces --------------------------------------------------------------

def test_strip_centre_line_is_the_unit_circle():
    u = np.linspace(0, 2 * np.pi, 9)
    x, y, z = mobius_strip(u, np.zeros_like(u))
    np.testing.assert_allclose(np.hypot(x, y), 1.0)
    np.testing.assert_allclose(z, 0.0, atol=1e-12)


def test_strip_has_a_half_twist():
    # Going once around the loop lands on the opposite edge.
    v = np.linspace(-0.5, 0.5, 11)
    end = mobius_strip(np.full_like(v, 2 * np.pi), v)
    start = mobius_strip(np.zeros_like(v), -v)
    for a, b in zip(end, start):
        np.testing.assert_allclose(a, b, atol=1e-12)


def test_strip_width():
    x, y, z = mobius_strip(np.array([0.0, 0.0]), np.array([-0.5, 0.5]))
    np.testing.assert_allclose(x, [0.75, 1.25])


def test_torus_known_points():
    x, y, z = torus(np.array([0.0, np.pi / 2]), np.array([0.0, np.pi / 2]), R=2, r=1)
    np.testing.assert_allclose(x, [3.0, 0.0], atol=1e-12)
    np.testing.assert_allclose(y, [0.0, 2.0], atol=1e-12)
    np.testing.assert_allclose(z, [0.0, 1.0], atol=1e-12)


# --- font and point-in-polygon ---------------------------------------------

def test_font_has_m_a_t_and_only_a_has_a_hole():
    assert mobiusmatt.ALPHABET == "MAT"
    assert Letter("A").hole and not Letter("M").hole and not Letter("T").hole
    for bad in ["B", "m", "", "MA"]:
        with pytest.raises(ValueError):
            Letter(bad)


def test_letters_do_not_share_outlines():
    a, b = Letter("A"), Letter("A")
    a.stretch(2, 2)
    assert a.border != b.border


def test_transforms():
    t = Letter("T")
    t.stretch(2, 1)
    t.rotate(np.pi / 2)
    t.shift(1, -1)
    border, _ = t.placed()
    # (-0.1, -0.33) -> stretch (-0.2, -0.33) -> rotate (0.33, -0.2) -> shift
    assert border[0] == pytest.approx((1.33, -1.2))


def test_inside_letter_respects_the_hole():
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    hole = [(1, 1), (3, 1), (3, 3), (1, 3)]
    u = np.array([[0.5, 2.0, 5.0]])
    v = np.array([[0.5, 2.0, 2.0]])
    assert inside_letter(square, hole, u, v).tolist() == [[True, False, False]]
    assert inside_letter(square, [], u, v).tolist() == [[True, True, False]]


def test_a_is_cut_but_its_counter_is_not():
    border, hole = Letter("A").placed()
    # right leg, the counter (the hole), and the gap between the legs
    u, v = np.array([[0.25, 0.0, 0.0]]), np.array([[-0.25, 0.12, -0.2]])
    assert inside_letter(border, hole, u, v).tolist() == [[True, False, False]]


# --- layouts ---------------------------------------------------------------

def test_check_word():
    assert check_word("MAT") == "MAT"
    with pytest.raises(ValueError, match="B"):
        check_word("BAT")
    with pytest.raises(ValueError):
        check_word("")


def test_strip_layout_spaces_letters_evenly_right_to_left():
    letters = strip_layout("MATT", times=2)
    assert "".join(le.letter for le in letters) == "TTAMTTAM"
    us = [le.center[0] for le in letters]
    np.testing.assert_allclose(np.diff(us), 2 * np.pi / 8)
    assert us[0] == pytest.approx(np.pi / 8 + 0.01)


def test_torus_layout_rows_shift_one_letter():
    letters = torus_layout("MAT", num_x=2, num_y=1)
    assert len(letters) == 3 * 6
    rows = ["".join(le.letter for le in letters[j * 6:(j + 1) * 6]) for j in range(3)]
    assert rows == ["MATMAT", "ATMATM", "TMATMA"]


# --- pinned answers --------------------------------------------------------

@pytest.mark.parametrize("key", STRIP_CUT)
def test_cut_strip_matches_the_original_script(key):
    u, (x, y, z) = cut_strip(*key)
    assert x.shape == u.shape == (100, 800)
    assert int(np.isnan(x).sum()) == STRIP_CUT[key]
    assert np.array_equal(np.isnan(x), np.isnan(z))


def test_cut_strip_leaves_the_edges_whole():
    _, (x, _, _) = cut_strip("MATT")
    assert not np.isnan(x[0]).any() and not np.isnan(x[-1]).any()


@pytest.mark.parametrize("key", TORUS_KEPT)
def test_letter_torus_matches_the_original_script(key):
    _, surfaces = letter_torus(*key)
    count, kept = TORUS_KEPT[key]
    assert len(surfaces) == count
    assert sum(int((~np.isnan(x)).sum()) for x, _, _ in surfaces) == kept


def test_camera_path_loops():
    path = camera_path(120)
    assert len(path) == 120
    assert path[0] == (-40.0, 30.0)
    assert max(e for e, _ in path) == 75
    assert path[30] == (75.0, -60.0)  # top of the first rock, a quarter turn in
    assert path[60] == (-40.0, -150.0)  # second rock starts half way round
    assert path[-1][1] == pytest.approx(30 - 360 * 119 / 120)


# --- command line ----------------------------------------------------------

def test_cli_strip_png(tmp_path, capsys):
    out = tmp_path / "strip.png"
    assert main(["strip", "--out", str(out)]) == 0
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert "MATT: 4 letters, 19958 of 80000 grid points cut out" in capsys.readouterr().out


def test_cli_strip_gif(tmp_path, capsys):
    out = tmp_path / "strip.gif"
    assert main(["strip", "--out", str(out), "--frames", "4", "--width", "120"]) == 0
    assert out.read_bytes()[:6] == b"GIF89a"
    assert "4 frames, 120 px" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [
    ["torus", "--word", "AT", "--num-y", "2"],
    ["layout", "--times", "2"],
    ["letter", "A"],
])
def test_cli_pngs(tmp_path, argv):
    out = tmp_path / "x.png"
    assert main(argv + ["--out", str(out)]) == 0
    assert out.stat().st_size > 1000


def test_cli_rejects_bad_input(tmp_path, capsys):
    with pytest.raises(SystemExit) as e:
        main(["strip", "--word", "BAT"])
    assert e.value.code == 2
    assert main(["strip", "--out", str(tmp_path / "x.jpg")]) == 2
    assert main(["torus", "--out", str(tmp_path / "x.gif")]) == 2
