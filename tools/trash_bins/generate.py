"""Generate the bin SVGs used by the "Trash" section of the home-main dashboard (Home view).

Usage: python3 tools/trash_bins/generate.py
Writes www/trash/<slug>.svg for every entry in BINS.

Every image shares the same geometry: a white label plate with the bin name on top
and an empty lower half. The dashboard places a state-label (attribute "label" of
sensor.trash_<slug>) at LABEL_CENTER, converted to percent of VIEW_W/VIEW_H.
Keep VIEW_* and PLATE stable or the overlay drifts.
The overlay font is a fixed 14px (picture-elements has no container-relative units),
so the plate must stay wide enough for "in 10 Tagen" on the narrowest card
(~155px with grid_options columns 6): keep PLATE width >= 56% of VIEW_W.
/local/ is cached by browsers for 31 days: bump the ?v= query in the dashboard
whenever the SVGs change.
"""

from pathlib import Path

VIEW_W, VIEW_H = 200, 240
# x, y, width, height of the white label plate.
PLATE = (44, 94, 112, 92)
NAME_Y = 113
DIVIDER_Y = 122
LABEL_CENTER = (100, 154)

FONT = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif"

# kind: "bin" (wheelie bin) or "sack". emblem: icon drawn above the plate.
BINS = [
    {
        "slug": "bioabfall",
        "name": "Bioabfall",
        "kind": "bin",
        "body": "#8a5a34",
        "lid": "#5e3a1d",
        "text": "#5e3a1d",
        "emblem": "leaf",
    },
    {
        "slug": "gelber_sack",
        "name": "Gelber Sack",
        "kind": "sack",
        "body": "#f6cf2f",
        "lid": "#c99a0e",
        "text": "#8a6a00",
        "emblem": "recycle",
    },
    {
        "slug": "restmuell",
        "name": "Restmüll",
        "kind": "bin",
        "body": "#555b62",
        "lid": "#30343a",
        "text": "#25282c",
        "emblem": "trash",
    },
    {
        "slug": "gartentonne",
        "name": "Gartentonne",
        "kind": "bin",
        "body": "#3f9440",
        "lid": "#256b29",
        "text": "#22612a",
        "emblem": "flower",
    },
    {
        "slug": "blaue_tonne",
        "name": "Blaue Tonne",
        "kind": "bin",
        "body": "#2f6fc4",
        "lid": "#1c4a8c",
        "text": "#1c4a8c",
        "emblem": "paper",
    },
]


def shade(hex_color, factor):
    """Lighten (factor > 0) or darken (factor < 0) a #rrggbb color by mixing with white/black."""
    rgb = [int(hex_color[i : i + 2], 16) for i in (1, 3, 5)]
    target = 255 if factor > 0 else 0
    mixed = [round(c + (target - c) * abs(factor)) for c in rgb]
    return "#" + "".join(f"{c:02x}" for c in mixed)


def body_gradient(gradient_id, color):
    """Horizontal gradient that makes a flat shape look rounded."""
    stops = [
        (0, shade(color, -0.28)),
        (0.3, color),
        (0.55, shade(color, 0.16)),
        (0.8, color),
        (1, shade(color, -0.32)),
    ]
    stop_tags = "".join(
        f'<stop offset="{offset}" stop-color="{c}"/>' for offset, c in stops
    )
    return f'<linearGradient id="{gradient_id}" x1="0" y1="0" x2="1" y2="0">{stop_tags}</linearGradient>'


def emblem(kind, color):
    """Icon centred on (0, 0), roughly 16px wide, drawn in the bin color."""
    stroke = f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "leaf":
        return (
            f'<path d="M-6,6 C-7,-3 -1,-7 7,-7 C7,2 2,7 -6,6 Z" fill="{color}"/>'
            f'<path d="M-7,7 L2,-2" fill="none" stroke="#fff" stroke-width="1.4" stroke-linecap="round"/>'
        )
    if kind == "recycle":
        return (
            f'<path d="M-6.5,1.5 A6.5,6.5 0 0 1 4.5,-4.7" fill="none" {stroke}/>'
            f'<path d="M6.5,-1.5 A6.5,6.5 0 0 1 -4.5,4.7" fill="none" {stroke}/>'
            f'<path d="M2,-8 L6,-4 L1,-2.5 Z" fill="{color}"/>'
            f'<path d="M-2,8 L-6,4 L-1,2.5 Z" fill="{color}"/>'
        )
    if kind == "trash":
        return (
            f'<path d="M-7,-4 H7 M-2.5,-4 V-6.5 H2.5 V-4" fill="none" {stroke}/>'
            f'<path d="M-5.5,-1.5 L-4.5,7 H4.5 L5.5,-1.5" fill="none" {stroke}/>'
            f'<path d="M-1.5,1 V4.5 M1.5,1 V4.5" fill="none" stroke="{color}" stroke-width="1.4" stroke-linecap="round"/>'
        )
    if kind == "flower":
        petals = "".join(
            f'<circle cx="{x}" cy="{y}" r="3.2" fill="{color}"/>'
            for x, y in [(0, -4.6), (4.4, -1.4), (2.7, 3.7), (-2.7, 3.7), (-4.4, -1.4)]
        )
        return petals + '<circle cx="0" cy="0" r="2.4" fill="#f4c430"/>'
    if kind == "paper":
        return (
            f'<rect x="-6.5" y="-7" width="13" height="14" rx="1.5" fill="none" {stroke}/>'
            f'<path d="M-3.5,-3 H3.5 M-3.5,0 H3.5 M-3.5,3 H1" fill="none" stroke="{color}" '
            f'stroke-width="1.5" stroke-linecap="round"/>'
        )
    raise ValueError(f"unknown emblem kind: {kind}")


def wheelie_bin(b):
    body, lid = b["body"], b["lid"]
    return [
        # Wheels sit behind the body.
        '<circle cx="54" cy="212" r="14" fill="#1d1f22" stroke="#4a4f56" stroke-width="2"/>',
        '<circle cx="146" cy="212" r="14" fill="#1d1f22" stroke="#4a4f56" stroke-width="2"/>',
        '<circle cx="54" cy="212" r="5" fill="#8a9097"/>',
        '<circle cx="146" cy="212" r="5" fill="#8a9097"/>',
        # Body: slightly tapered towards the bottom.
        '<path d="M34,58 H166 L155,204 Q154,214 144,214 H56 Q46,214 45,204 Z" fill="url(#body)"/>',
        # Vertical ribs and a soft highlight give it some depth.
        (
            f'<path d="M44,70 L52,200 M156,70 L148,200" stroke="{shade(body, -0.22)}" stroke-width="3" '
            'stroke-linecap="round" opacity="0.7"/>'
        ),
        '<path d="M48,62 H66 L70,208 H58 Z" fill="#fff" opacity="0.12"/>',
        # Rim under the lid.
        f'<rect x="32" y="56" width="136" height="6" rx="2" fill="{shade(body, -0.35)}"/>',
        # Handle bar behind the lid and the lid itself.
        f'<rect x="58" y="30" width="84" height="10" rx="5" fill="{shade(lid, -0.2)}"/>',
        f'<rect x="26" y="38" width="148" height="20" rx="7" fill="{lid}"/>',
        '<rect x="30" y="40" width="140" height="5" rx="2.5" fill="#fff" opacity="0.18"/>',
    ]


def yellow_sack(b):
    body, edge = b["body"], b["lid"]
    return [
        # Bag body.
        (
            f'<path d="M80,66 C34,80 22,150 32,198 Q38,218 100,218 Q162,218 168,198 '
            f'C178,150 166,80 120,66 Z" fill="url(#body)" stroke="{edge}" stroke-width="2.5" opacity="0.96"/>'
        ),
        # Folds.
        (
            f'<path d="M62,92 C56,130 58,170 66,206 M138,92 C144,130 142,170 134,206 M100,70 V84" '
            f'fill="none" stroke="{shade(body, -0.3)}" stroke-width="2" stroke-linecap="round" opacity="0.45"/>'
        ),
        '<path d="M50,96 C42,130 42,170 52,200 L62,204 C54,170 54,130 62,98 Z" fill="#fff" opacity="0.22"/>',
        # Tied neck with two ears.
        f'<path d="M92,66 L70,30 Q84,34 98,56 Z" fill="{body}" stroke="{edge}" stroke-width="2.5" stroke-linejoin="round"/>',
        f'<path d="M108,66 L130,30 Q116,34 102,56 Z" fill="{body}" stroke="{edge}" stroke-width="2.5" stroke-linejoin="round"/>',
        f'<ellipse cx="100" cy="64" rx="12" ry="7" fill="{shade(body, -0.12)}" stroke="{edge}" stroke-width="2.5"/>',
    ]


def render(b):
    px, py, pw, ph = PLATE
    out = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" '
            f'width="{VIEW_W}" height="{VIEW_H}" font-family="{FONT}">'
        ),
        "<defs>",
        body_gradient("body", b["body"]),
        "</defs>",
        # Ground shadow.
        '<ellipse cx="100" cy="226" rx="74" ry="8" fill="#000" opacity="0.18"/>',
    ]
    if b["kind"] == "bin":
        out.extend(wheelie_bin(b))
    elif b["kind"] == "sack":
        out.extend(yellow_sack(b))
    else:
        raise ValueError(f"unknown bin kind: {b['kind']}")

    # Emblem badge between lid/neck and plate.
    out.append(
        f'<circle cx="100" cy="78" r="11" fill="#fff" opacity="0.92"/>'
        f'<g transform="translate(100 78)">{emblem(b["emblem"], b["text"])}</g>'
    )

    # Label plate: drop shadow, plate, bin name, divider. Lower half stays empty for the live text.
    out.append(
        f'<rect x="{px}" y="{py + 2}" width="{pw}" height="{ph}" rx="12" fill="#000" opacity="0.18"/>'
    )
    out.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="#fff"/>'
    )
    out.append(
        f'<text x="{px + pw / 2}" y="{NAME_Y}" text-anchor="middle" font-size="12.5" '
        f'font-weight="700" letter-spacing="0.3" fill="{b["text"]}">{b["name"]}</text>'
    )
    out.append(
        f'<path d="M{px + 14},{DIVIDER_Y}H{px + pw - 14}" stroke="{b["lid"]}" '
        f'stroke-width="2" stroke-linecap="round" opacity="0.55"/>'
    )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    out_dir = Path(__file__).resolve().parents[2] / "www" / "trash"
    out_dir.mkdir(parents=True, exist_ok=True)
    for b in BINS:
        path = out_dir / f"{b['slug']}.svg"
        path.write_text(render(b), encoding="utf-8")
        print(f"wrote {path}")
    cx, cy = LABEL_CENTER
    print(f"label overlay: left {cx / VIEW_W * 100:.1f}%, top {cy / VIEW_H * 100:.1f}%")


if __name__ == "__main__":
    main()
