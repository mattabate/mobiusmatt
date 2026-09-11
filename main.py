import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matt_font import Letter
import fire


# Define the parameterization of the Möbius strip
def mobius_strip(u, v):
    x = (1 + v / 2 * np.cos(u / 2)) * np.cos(u)
    y = (1 + v / 2 * np.cos(u / 2)) * np.sin(u)
    z = v / 5 * np.sin(u / 2)
    return x, y, z


def is_inside_complex_polygon(border_points, hole_points, u, v):
    """
    Check if the points (u, v) are inside a complex polygon defined by 'border_points'
    and not inside 'hole_points'.
    """
    border_path = Path(border_points)
    hole_path = Path(hole_points) if hole_points else None

    # Initially check if points are inside the border
    inside_border = border_path.contains_points(
        np.vstack((u.flatten(), v.flatten())).T
    ).reshape(u.shape)

    # Then, if there's a hole, check if points are inside it and exclude those
    if hole_path:
        inside_hole = hole_path.contains_points(
            np.vstack((u.flatten(), v.flatten())).T
        ).reshape(u.shape)
        return np.logical_and(inside_border, ~inside_hole)
    else:
        return inside_border


def plot_2d_test_layout(masks: list[Letter]):
    fig, ax = plt.subplots()

    for mask in masks:
        closed_border = mask.border + [mask.border[0]]
        centerd_border = [
            (x + mask.center[0], y + mask.center[1]) for x, y in closed_border
        ]
        border_path = Path(centerd_border)  # Close the loop
        border_patch = patches.PathPatch(
            border_path, facecolor="lightblue", lw=2, alpha=0.5
        )
        ax.add_patch(border_patch)

        # Plot the hole if it exists
        if mask.hole:
            closed_hole = mask.hole + [mask.hole[0]]
            centerd_hole = [
                (x + mask.center[0], y + mask.center[1]) for x, y in closed_hole
            ]
            hole_path = Path(centerd_hole)  # Close the loop
            hole_patch = patches.PathPatch(hole_path, facecolor="white", lw=2)
            ax.add_patch(hole_patch)

    # Add colored dots to specified corners
    ax.plot(2 * np.pi, 0.5, "ro", markersize=20)  # Red dot in the upper right corner
    ax.plot(0, -0.5, "ro", markersize=20)  # Red dot in the lower left corner
    ax.plot(2 * np.pi, -0.5, "bo", markersize=20)  # Blue dot in the lower right corner
    ax.plot(0, 0.5, "bo", markersize=20)  # Blue dot in the upper left corner

    ax.set_xlim(0, 2 * np.pi)
    ax.set_ylim(-0.5, 0.5)
    ax.set_aspect("equal")
    plt.title("2D Preview of Möbius Strip Layout")
    plt.show()


def main(word="MATT", test: bool = False, num_times=1):
    text_on_strip = word * num_times
    nonconvex_polygons = []
    for i, letter in enumerate(text_on_strip[::-1]):
        mask = Letter(letter=letter)
        mask.stretch(1, 2 * np.pi / len(text_on_strip))
        mask.rotate(-np.pi / 2)
        mask.shift(
            2 * i * np.pi / len(text_on_strip) + np.pi / len(text_on_strip) + 0.01, 0
        )
        nonconvex_polygons.append(mask)

    if test:
        plot_2d_test_layout(nonconvex_polygons)

    if not test:
        # Generate a dense meshgrid for finer detail
        u = np.linspace(0, 2 * np.pi, 800)
        v = np.linspace(-0.5, 0.5, 100)
        u, v = np.meshgrid(u, v)

        x, y, z = mobius_strip(u, v)
        for polygon_points in nonconvex_polygons:
            shifed_border = [
                (x + polygon_points.center[0], y + polygon_points.center[1])
                for x, y in polygon_points.border
            ]
            shifed_hole = [
                (x + polygon_points.center[0], y + polygon_points.center[1])
                for x, y in polygon_points.hole
            ]

            inside_mask = is_inside_complex_polygon(shifed_border, shifed_hole, u, v)
            x[inside_mask], y[inside_mask], z[inside_mask] = (
                np.nan,
                np.nan,
                np.nan,
            )

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        # ax.plot_surface(x, y, z, color="cyan", edgecolor="none", alpha=0.6)
        colors = plt.cm.hsv(u / (2 * np.pi))

        # Plot the surface with the facecolors set to the colormap
        ax.plot_surface(x, y, z, facecolors=colors, edgecolor="none", alpha=0.6)

        # Set the title and axis limits
        ax.set_title("Möbius Matt", fontsize=40)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)

        # Hide the axes for a cleaner look
        ax.set_axis_off()

        # Set initial view
        ax.view_init(elev=30, azim=30)

        # Oscillation parameters
        elev_start = -40
        elev_end = 75
        frames_per_oscillation = 80
        total_cycles = 5
        azim_change_per_frame = 360 / (frames_per_oscillation * total_cycles)
        azim_current = 30

        try:
            # Total frames for both upward and downward oscillation
            for frame in range(frames_per_oscillation * total_cycles * 2):
                if frame % (frames_per_oscillation * 2) < frames_per_oscillation:
                    # Upward oscillation in z
                    elev = np.linspace(elev_start, elev_end, frames_per_oscillation)[
                        frame % frames_per_oscillation
                    ]
                else:
                    # Downward oscillation in z
                    elev = np.linspace(elev_end, elev_start, frames_per_oscillation)[
                        frame % frames_per_oscillation
                    ]

                # Counter-clockwise rotation by decreasing the azimuth angle
                azim_current -= azim_change_per_frame
                ax.view_init(elev=elev, azim=azim_current)
                plt.draw()
                plt.pause(0.1)  # Adjust as needed for your screen recording

        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    fire.Fire(main)
