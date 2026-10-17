"""Generate the floor plan SVGs used by the "Floor plan" view of the home-main dashboard.

Usage: python3 tools/floorplan/generate.py
Writes www/floorplan/floorplan-light.svg and www/floorplan/floorplan-dark.svg.

Coordinates are pixels of the original scan (2000x1500 display size), so the
dashboard overlay positions are: left% = (x - VIEW_X) / VIEW_W * 100,
top% = (y - VIEW_Y) / VIEW_H * 100. Keep VIEW_* stable or the overlay drifts.
"""

from pathlib import Path

VIEW_X, VIEW_Y, VIEW_W, VIEW_H = 20, 30, 1980, 1470
WALL = 16
OUTER_WALL = 26

# Room polygons. kind selects the tint from the palette.
ROOMS = [
    {
        "name": "Zimmer 1",
        "kind": "office",
        "label_at": (312, 98),
        "points": [
            (290, 55),
            (600, 55),
            (600, 350),
            (705, 350),
            (705, 470),
            (290, 470),
        ],
    },
    {
        "name": "DU/WC",
        "kind": "bath",
        "label_at": (622, 98),
        "points": [(600, 55), (830, 55), (830, 350), (600, 350)],
    },
    {
        "name": "Treppe",
        "kind": "stairs",
        "label_at": (852, 98),
        "points": [
            (830, 55),
            (1050, 55),
            (1050, 350),
            (1180, 350),
            (1180, 470),
            (830, 470),
        ],
    },
    {
        "name": "Wohnen",
        "kind": "living",
        "label_at": (312, 512),
        "points": [(290, 470), (710, 470), (710, 870), (290, 870)],
    },
    {
        "name": "Essen",
        "kind": "dining",
        "label_at": (852, 732),
        "points": [
            (705, 350),
            (830, 350),
            (830, 690),
            (1340, 690),
            (1340, 860),
            (1080, 860),
            (1080, 1230),
            (710, 1230),
            (710, 470),
            (705, 470),
        ],
    },
    {
        "name": "Diele",
        "kind": "hall",
        "label_at": (852, 512),
        "points": [(830, 470), (1180, 470), (1180, 690), (830, 690)],
    },
    {
        "name": "Abst.",
        "kind": "utility",
        "label_at": (1200, 512),
        "points": [(1180, 470), (1370, 470), (1370, 690), (1180, 690)],
    },
    {
        "name": "Technik",
        "kind": "utility",
        "label_at": (1392, 498),
        "points": [(1370, 455), (1685, 455), (1685, 690), (1370, 690)],
    },
    {
        "name": "Keller 2",
        "kind": "utility",
        "label_at": (1707, 422),
        "points": [(1685, 380), (1985, 380), (1985, 690), (1685, 690)],
    },
    {
        "name": "Garage",
        "kind": "garage",
        "label_at": (1707, 98),
        "points": [(1685, 55), (1985, 55), (1985, 380), (1685, 380)],
    },
    {
        "name": "Zimmer 2",
        "kind": "office",
        "label_at": (312, 912),
        "points": [(290, 870), (710, 870), (710, 1230), (290, 1230)],
    },
    {
        "name": "Küche",
        "kind": "kitchen",
        "label_at": (1102, 902),
        "points": [(1080, 860), (1340, 860), (1340, 1230), (1080, 1230)],
    },
    {
        "name": "Bad",
        "kind": "bath",
        "label_at": (1477, 732),
        "points": [(1455, 690), (1750, 690), (1750, 1000), (1455, 1000)],
    },
    {
        "name": "Schlafen",
        "kind": "bedroom",
        "label_at": (1477, 1042),
        "points": [
            (1340, 690),
            (1455, 690),
            (1455, 1000),
            (1750, 1000),
            (1750, 1450),
            (1340, 1450),
        ],
    },
]

# Outer building outline, drawn with the thicker wall.
FOOTPRINT = [
    (290, 55),
    (1050, 55),
    (1050, 350),
    (1180, 350),
    (1180, 455),
    (1685, 455),
    (1685, 55),
    (1985, 55),
    (1985, 690),
    (1750, 690),
    (1750, 1450),
    (1340, 1450),
    (1340, 1230),
    (290, 1230),
]

# Openings in walls. gap: center line (x1, y1, x2, y2) on a horizontal or vertical wall.
# swing: None (open passage) or (hinge_x, hinge_y, sweep_end_x, sweep_end_y).
# fill: tint kind used to paint the erased wall so the opening blends into a room.
# panel: optional, draws a dashed sectional door across a full outer-wall opening.
DOORS = [
    {
        "name": "Zimmer 1",
        "gap": (705, 380, 705, 455),
        "swing": (705, 455, 630, 380),
        "fill": "office",
    },
    {
        "name": "DU/WC",
        "gap": (725, 350, 805, 350),
        "swing": (805, 350, 725, 275),
        "fill": "bath",
    },
    {
        "name": "Diele entrance",
        "gap": (985, 470, 1065, 470),
        "swing": (985, 470, 1065, 390),
        "fill": "hall",
    },
    {
        "name": "Diele to Essen",
        "gap": (995, 690, 1070, 690),
        "swing": (1070, 690, 995, 615),
        "fill": "hall",
    },
    {
        "name": "Abst.",
        "gap": (1240, 690, 1310, 690),
        "swing": (1310, 690, 1240, 615),
        "fill": "utility",
    },
    {
        "name": "Wohnen / Essen opening",
        "gap": (710, 500, 710, 680),
        "swing": None,
        "fill": "living",
    },
    {
        "name": "Zimmer 2 double door",
        "gap": (430, 870, 550, 870),
        "swing": None,
        "fill": "office",
    },
    {
        "name": "Kueche",
        "gap": (1180, 860, 1265, 860),
        "swing": (1265, 860, 1180, 945),
        "fill": "kitchen",
    },
    {
        "name": "Schlafen from Essen",
        "gap": (1340, 770, 1340, 850),
        "swing": (1340, 850, 1265, 770),
        "fill": "dining",
    },
    {
        "name": "Bad",
        "gap": (1455, 770, 1455, 850),
        "swing": (1455, 850, 1530, 770),
        "fill": "bath",
    },
    {
        "name": "Keller 2 inside",
        "gap": (1685, 600, 1685, 675),
        "swing": (1685, 675, 1760, 600),
        "fill": "utility",
    },
    {
        "name": "Keller 2 outside",
        "gap": (1880, 690, 1960, 690),
        "swing": (1960, 690, 1880, 765),
        "fill": "utility",
    },
    {
        "name": "Garage door",
        "gap": (1725, 55, 1945, 55),
        "swing": None,
        "fill": "garage",
        "panel": True,
    },
]

# Windows and glazed doors on outer walls: (x1, y1, x2, y2).
WINDOWS = [
    (290, 240, 290, 360),  # Zimmer 1
    (725, 55, 815, 55),  # DU/WC
    (70, 470, 260, 470),  # Wintergarten roof side
    (290, 590, 290, 760),  # Wohnen to Wintergarten
    (290, 1110, 290, 1200),  # Zimmer 2 side
    (320, 1230, 460, 1230),  # Zimmer 2 terrace door
    (830, 1230, 955, 1230),  # Essen terrace door
    (1175, 1230, 1265, 1230),  # Kueche terrace door
    (1515, 1450, 1645, 1450),  # Schlafen garden door
    (1750, 1070, 1750, 1190),  # Schlafen side
    (1750, 790, 1750, 880),  # Bad
]

WINTERGARDEN = [(40, 470), (290, 470), (290, 870), (40, 870)]
TERRACE = (290, 1240, 1330, 1480)
STAIRS = {"x1": 845, "x2": 1040, "y1": 180, "y2": 350, "step": 21}

PALETTES = {
    "light": {
        "background": "#f7f5f0",
        "wall": "#2f3437",
        "label": "#6b6f76",
        "door_swing": "#9aa0a6",
        "window": "#8ec5ff",
        "terrace": "#efe8dc",
        "terrace_line": "#ddd3c3",
        "wintergarden": "#e4f2dc",
        "glass": "#7fb069",
        "tints": {
            "office": "#e3ecfa",
            "bath": "#d8f0f2",
            "stairs": "#e5e5e5",
            "living": "#fbe6d4",
            "dining": "#fdf1d7",
            "hall": "#ececec",
            "utility": "#e8e4dd",
            "kitchen": "#e2f2df",
            "bedroom": "#ebe3f7",
            "garage": "#e4e6e9",
        },
    },
    "dark": {
        "background": "#16181c",
        "wall": "#c7cdd5",
        "label": "#8d96a3",
        "door_swing": "#5d6570",
        "window": "#4a90d9",
        "terrace": "#24211d",
        "terrace_line": "#332f29",
        "wintergarden": "#1d2a1b",
        "glass": "#5c8f4a",
        "tints": {
            "office": "#1f2a3a",
            "bath": "#1a3033",
            "stairs": "#25272b",
            "living": "#372a20",
            "dining": "#353020",
            "hall": "#26282c",
            "utility": "#2a2824",
            "kitchen": "#1f3022",
            "bedroom": "#2b2639",
            "garage": "#24272b",
        },
    },
}


def points_attr(points):
    return " ".join(f"{x},{y}" for x, y in points)


def door_gap_rect(x1, y1, x2, y2, depth):
    """Rect that erases a wall segment between two points on a horizontal or vertical wall."""
    if y1 == y2:
        return min(x1, x2), y1 - depth / 2, abs(x2 - x1), depth
    return x1 - depth / 2, min(y1, y2), depth, abs(y2 - y1)


def render(palette):
    p = palette
    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEW_X} {VIEW_Y} {VIEW_W} {VIEW_H}" '
        f'width="{VIEW_W}" height="{VIEW_H}" font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif">'
    )
    out.append(
        f'<rect x="{VIEW_X}" y="{VIEW_Y}" width="{VIEW_W}" height="{VIEW_H}" rx="28" fill="{p["background"]}"/>'
    )

    # Terrace tiles
    tx1, ty1, tx2, ty2 = TERRACE
    out.append(
        f'<rect x="{tx1}" y="{ty1}" width="{tx2 - tx1}" height="{ty2 - ty1}" rx="10" fill="{p["terrace"]}"/>'
    )
    tiles = []
    for x in range(tx1 + 60, tx2, 60):
        tiles.append(f"M{x},{ty1}V{ty2}")
    for y in range(ty1 + 60, ty2, 60):
        tiles.append(f"M{tx1},{y}H{tx2}")
    out.append(
        f'<path d="{"".join(tiles)}" stroke="{p["terrace_line"]}" stroke-width="2" fill="none"/>'
    )
    out.append(
        f'<text x="{(tx1 + tx2) / 2}" y="{ty2 - 40}" text-anchor="middle" font-size="26" '
        f'letter-spacing="4" fill="{p["label"]}">TERRASSE</text>'
    )

    # Wintergarden (glass walls)
    out.append(
        f'<polygon points="{points_attr(WINTERGARDEN)}" fill="{p["wintergarden"]}" '
        f'stroke="{p["glass"]}" stroke-width="6" stroke-dasharray="18 10"/>'
    )
    out.append(
        f'<text x="58" y="512" font-size="22" font-weight="600" letter-spacing="2" '
        f'fill="{p["label"]}">WINTERGARTEN</text>'
    )

    # Room fills first, then all walls, so neighbouring fills never cover a wall.
    for room in ROOMS:
        out.append(
            f'<polygon points="{points_attr(room["points"])}" fill="{p["tints"][room["kind"]]}"/>'
        )

    # Stairs
    s = STAIRS
    steps = "".join(
        f"M{s['x1']},{y}H{s['x2']}" for y in range(s["y1"], s["y2"] + 1, s["step"])
    )
    out.append(
        f'<path d="{steps}" stroke="{p["door_swing"]}" stroke-width="3" fill="none"/>'
    )
    mid = (s["x1"] + s["x2"]) / 2
    out.append(
        f'<path d="M{mid},{s["y1"] - 20}V{s["y2"]}" stroke="{p["door_swing"]}" stroke-width="3"/>'
    )

    for room in ROOMS:
        out.append(
            f'<polygon points="{points_attr(room["points"])}" fill="none" stroke="{p["wall"]}" '
            f'stroke-width="{WALL}" stroke-linejoin="miter"/>'
        )
    out.append(
        f'<polygon points="{points_attr(FOOTPRINT)}" fill="none" stroke="{p["wall"]}" '
        f'stroke-width="{OUTER_WALL}" stroke-linejoin="miter"/>'
    )

    # Doors: erase wall, then draw swing arc.
    for door in DOORS:
        x1, y1, x2, y2 = door["gap"]
        swing = door["swing"]
        rx, ry, rw, rh = door_gap_rect(
            x1, y1, x2, y2, OUTER_WALL + 4 if door.get("panel") else WALL + 2
        )
        out.append(
            f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{p["tints"][door["fill"]]}"/>'
        )
        if door.get("panel"):
            out.append(
                f'<path d="M{x1},{y1}L{x2},{y2}" stroke="{p["wall"]}" stroke-width="6" stroke-dasharray="22 10"/>'
            )
        if swing:
            hx, hy, ex, ey = swing
            # Leaf from hinge to the open position, quarter arc back to the closed position.
            if y1 == y2:
                closed_x = x1 if hx == x2 else x2
                leaf_end = (hx, ey)
                arc_end = (closed_x, hy)
            else:
                closed_y = y1 if hy == y2 else y2
                leaf_end = (ex, hy)
                arc_end = (hx, closed_y)
            radius = abs(x2 - x1) if y1 == y2 else abs(y2 - y1)
            out.append(
                f'<path d="M{hx},{hy}L{leaf_end[0]},{leaf_end[1]}A{radius},{radius} 0 0 '
                f'{door_sweep(hx, hy, leaf_end, arc_end)} {arc_end[0]},{arc_end[1]}" '
                f'fill="none" stroke="{p["door_swing"]}" stroke-width="3"/>'
            )

    # Windows: erase wall, draw glass bar.
    for x1, y1, x2, y2 in WINDOWS:
        rx, ry, rw, rh = door_gap_rect(x1, y1, x2, y2, OUTER_WALL)
        out.append(
            f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{p["background"]}"/>'
        )
        out.append(
            f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="none" '
            f'stroke="{p["wall"]}" stroke-width="3"/>'
        )
        out.append(
            f'<path d="M{x1},{y1}L{x2},{y2}" stroke="{p["window"]}" stroke-width="6"/>'
        )

    for room in ROOMS:
        lx, ly = room["label_at"]
        out.append(
            f'<text x="{lx}" y="{ly}" font-size="26" font-weight="600" letter-spacing="2" '
            f'fill="{p["label"]}">{room["name"].upper()}</text>'
        )

    out.append("</svg>")
    return "\n".join(out) + "\n"


def door_sweep(hx, hy, leaf_end, arc_end):
    """SVG arc sweep flag so the arc bulges away from the hinge."""
    ax, ay = leaf_end[0] - hx, leaf_end[1] - hy
    bx, by = arc_end[0] - hx, arc_end[1] - hy
    cross = ax * by - ay * bx
    return 1 if cross > 0 else 0


def main():
    repo_root = Path(__file__).resolve().parents[2]
    target_dir = repo_root / "www" / "floorplan"
    target_dir.mkdir(parents=True, exist_ok=True)
    for name, palette in PALETTES.items():
        path = target_dir / f"floorplan-{name}.svg"
        path.write_text(render(palette), encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
