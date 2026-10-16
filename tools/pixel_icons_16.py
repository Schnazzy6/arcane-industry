"""Hand-authored 16x16 progression sprites. No resampling of the old icons."""
from __future__ import annotations

import json
import shutil
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "overrides/client/kubejs/assets/kubejs/textures/item/progression"
PREVIEW = ROOT / "custom/item-textures/pixel-icons-16-preview.png"
NAMES = sorted(p.stem for p in OUT.glob("*.png"))

DARK = "#242b35"
EDGE = "#39424d"
SHADE = "#1a2029"
IRON = ("#566775", "#8797a2", "#c5d3d6")
COPPER = ("#754435", "#b56848", "#e2a77a")
GOLD = ("#856022", "#c8973d", "#f4d677")
TEAL = ("#155a66", "#2aa4ad", "#a0e5de")
VIOLET = ("#513c72", "#8c64ad", "#cdb7ee")
RED = ("#743644", "#bd5a65", "#f4a29c")
GREEN = ("#456246", "#7bab65", "#d1e4a0")
BLUE = ("#34516f", "#668fbd", "#b9daed")


def canvas():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def diamond(d, box, colors, border=DARK):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.polygon([(cx, y0), (x1, cy), (cx, y1), (x0, cy)], fill=border)
    d.polygon([(cx, y0 + 1), (x1 - 1, cy), (cx, y1 - 1), (x0 + 1, cy)], fill=colors[0])
    d.polygon([(cx, y0 + 1), (x1 - 1, cy), (cx, cy), (x0 + 1, cy)], fill=colors[1])
    d.line([(x0 + 2, cy), (cx, y0 + 2), (cx + 2, y0 + 4)], fill=colors[2])
    d.point((cx, y0 + 1), fill="#f4f6eb")
    d.line([(cx + 1, cy + 1), (cx, y1 - 1)], fill=colors[0])


def bolt(d, x=7, y=3, color="#f5dc84"):
    d.polygon([(x + 2, y), (x - 1, y + 5), (x + 2, y + 5),
               (x, y + 10), (x + 5, y + 4), (x + 2, y + 4),
               (x + 4, y)], fill=color)


def plate(d, metal=IRON):
    d.polygon([(5, 1), (10, 1), (13, 4), (12, 12), (9, 14),
               (6, 14), (3, 12), (2, 4)], fill=DARK)
    d.polygon([(5, 2), (10, 2), (12, 4), (11, 11), (9, 13),
               (6, 13), (4, 11), (3, 4)], fill=metal[0])
    d.line([(4, 4), (6, 3), (9, 3), (11, 4)], fill=metal[2], width=1)
    d.line([(4, 5), (4, 10), (6, 12)], fill=metal[1], width=1)
    d.line([(10, 12), (11, 10), (11, 6)], fill=metal[1], width=1)
    d.line([(6, 14), (9, 14)], fill=EDGE)
    d.line([(5, 4), (5, 9)], fill=metal[1])
    d.line([(10, 5), (10, 10), (8, 12)], fill=SHADE)
    d.point((4, 3), fill=metal[2])
    d.point((11, 3), fill=metal[1])
    d.point((5, 11), fill=metal[2])


def armor_core(n):
    palettes = [
        COPPER, IRON, ("#50686b", "#80a3a0", "#d0d9c8"),
        ("#3e6570", "#68aab9", "#c8e9e5"), GOLD,
        VIOLET, BLUE, ("#504652", "#aa8aab", "#f5def7"),
    ]
    gem = [GREEN, TEAL, BLUE, VIOLET, RED, TEAL, VIOLET, GOLD][n - 1]
    im, d = canvas()
    plate(d, palettes[n - 1])
    diamond(d, (5, 5, 10, 10), gem)
    d.point((7, 6), fill=gem[2])
    d.point((5, 4), fill=palettes[n - 1][2])
    d.point((6, 11), fill=palettes[n - 1][1])
    d.point((10, 11), fill=palettes[n - 1][0])
    d.line([(6, 12), (8, 12)], fill=palettes[n - 1][2])
    if n >= 3:
        d.point((2, 2), fill=palettes[n - 1][2])
        d.point((13, 2), fill=palettes[n - 1][2])
    if n >= 6:
        d.line([(1, 6), (1, 9)], fill=palettes[n - 1][1])
        d.line([(14, 6), (14, 9)], fill=palettes[n - 1][1])
    if n == 8:
        d.point((7, 0), fill=GOLD[2])
        d.point((0, 7), fill=GOLD[2])
        d.point((15, 7), fill=GOLD[2])
    return im


def crystal_focus(metal, crystal, electrical=False):
    im, d = canvas()
    d.line([(2, 13), (5, 10), (8, 10), (11, 13)], fill=DARK, width=2)
    d.line([(3, 13), (6, 11), (10, 13)], fill=metal[1], width=1)
    d.rectangle((3, 8, 4, 12), fill=metal[0])
    d.rectangle((11, 8, 12, 12), fill=metal[0])
    diamond(d, (4, 1, 11, 9), crystal)
    d.line([(4, 7), (6, 9)], fill=metal[2])
    d.line([(10, 9), (12, 7)], fill=metal[2])
    d.point((4, 10), fill=metal[2])
    d.point((11, 10), fill=metal[0])
    d.point((7, 2), fill="#f4f6eb")
    d.line([(8, 7), (9, 6)], fill=crystal[0])
    if electrical:
        d.point((1, 5), fill=GOLD[2])
        d.point((13, 3), fill=GOLD[2])
    return im


def vial(liquid, cap=COPPER):
    im, d = canvas()
    d.rectangle((6, 1, 9, 3), fill=DARK)
    d.rectangle((7, 1, 8, 2), fill=cap[1])
    d.polygon([(5, 4), (10, 4), (12, 7), (11, 13), (9, 14),
               (6, 14), (4, 12), (3, 7)], fill=DARK)
    d.polygon([(5, 5), (10, 5), (11, 8), (10, 12), (9, 13),
               (6, 13), (5, 12), (4, 8)], fill="#b5d3d5")
    d.polygon([(4, 9), (11, 9), (10, 12), (9, 13), (6, 13),
               (5, 12)], fill=liquid[0])
    d.line([(5, 10), (8, 10)], fill=liquid[1])
    d.point((6, 6), fill="#eef7ec")
    d.point((7, 5), fill="#eef7ec")
    d.point((9, 11), fill=liquid[2])
    d.point((10, 8), fill="#e1f3eb")
    d.line([(6, 12), (8, 12)], fill=liquid[1])
    d.point((5, 11), fill=liquid[2])
    return im


def circular_seal(colors, symbol):
    im, d = canvas()
    d.ellipse((2, 2, 13, 13), fill=DARK)
    d.ellipse((3, 3, 12, 12), fill=colors[0])
    d.arc((4, 4, 11, 11), 190, 340, fill=colors[2])
    d.line([(3, 8), (5, 11), (8, 12)], fill=colors[1])
    d.point((7, 1), fill=colors[2])
    d.line([(4, 4), (5, 3), (8, 3)], fill=colors[2])
    d.line([(10, 11), (8, 12), (5, 11)], fill=SHADE)
    d.point((11, 5), fill=colors[1])
    if symbol == "leaf":
        d.line([(6, 10), (10, 5)], fill="#e2eac3")
        d.polygon([(6, 6), (10, 4), (10, 8), (7, 9)], fill=GREEN[1])
        d.point((8, 5), fill=GREEN[2])
    elif symbol == "mind":
        d.polygon([(7, 4), (10, 7), (7, 10), (4, 7)], fill=BLUE[2])
        d.line([(7, 5), (7, 9)], fill="#fff0dc")
        d.line([(5, 7), (9, 7)], fill="#fff0dc")
    elif symbol == "soul":
        d.polygon([(7, 4), (10, 7), (8, 10), (6, 10), (4, 7)], fill=VIOLET[2])
        d.point((6, 7), fill=DARK)
        d.point((8, 7), fill=DARK)
    elif symbol == "elements":
        for x, y, c in [(7, 4, RED[2]), (10, 7, BLUE[2]),
                        (7, 10, GREEN[2]), (4, 7, GOLD[2])]:
            d.rectangle((x, y, x + 1, y + 1), fill=c)
        d.point((7, 7), fill="#f1ecdd")
    elif symbol == "boss":
        d.polygon([(5, 4), (7, 6), (9, 4), (10, 8), (8, 10),
                   (6, 10), (4, 8)], fill=RED[2])
        d.point((6, 8), fill=DARK)
        d.point((8, 8), fill=DARK)
    return im


def frame(metal, inset=TEAL):
    im, d = canvas()
    d.rectangle((2, 2, 13, 13), fill=DARK)
    d.rectangle((3, 3, 12, 12), fill=metal[1])
    d.rectangle((5, 5, 10, 10), fill=DARK)
    d.rectangle((6, 6, 9, 9), fill=inset[0])
    d.point((7, 7), fill=inset[2])
    for x, y in [(3, 3), (11, 3), (3, 11), (11, 11)]:
        d.rectangle((x, y, x + 1, y + 1), fill=metal[2])
    d.line([(5, 3), (9, 3)], fill=metal[2])
    d.line([(12, 5), (12, 10)], fill=metal[0])
    d.line([(5, 12), (10, 12)], fill=SHADE)
    d.point((9, 8), fill=inset[1])
    return im


def matrix(metal, center):
    im, d = canvas()
    d.polygon([(7, 1), (13, 4), (13, 11), (8, 14),
               (2, 11), (2, 4)], fill=DARK)
    d.polygon([(7, 2), (12, 5), (12, 10), (8, 13),
               (3, 10), (3, 5)], fill=metal[0])
    d.line([(7, 2), (11, 5), (7, 7), (3, 5)], fill=metal[2])
    d.line([(7, 7), (7, 12)], fill=metal[1])
    d.line([(8, 7), (12, 5)], fill=metal[1])
    d.line([(11, 6), (11, 10), (8, 12)], fill=SHADE)
    d.point((4, 4), fill=metal[2])
    d.point((4, 9), fill=metal[1])
    diamond(d, (5, 5, 10, 10), center)
    return im


def scroll_like(base, accent, mark="star"):
    im, d = canvas()
    d.polygon([(3, 2), (11, 2), (13, 4), (12, 13), (4, 13),
               (2, 11)], fill=DARK)
    d.polygon([(4, 3), (11, 3), (12, 5), (11, 12), (5, 12),
               (3, 10)], fill=base[1])
    d.line([(4, 4), (10, 4)], fill=base[2])
    d.line([(4, 11), (11, 11)], fill=base[0])
    d.point((5, 3), fill="#f3e6bf")
    d.line([(10, 5), (10, 9)], fill=base[0])
    d.point((4, 10), fill=base[2])
    if mark == "star":
        d.line([(7, 5), (7, 10)], fill=accent[2])
        d.line([(5, 7), (10, 7)], fill=accent[2])
        d.point((7, 7), fill="#fff4db")
    elif mark == "map":
        d.line([(5, 9), (7, 6), (9, 8), (11, 5)], fill=accent[0])
        d.rectangle((8, 5, 9, 6), fill=accent[2])
    elif mark == "grid":
        for x in (5, 8, 10):
            d.line([(x, 5), (x, 10)], fill=accent[0])
        for y in (6, 9):
            d.line([(5, y), (10, y)], fill=accent[0])
        d.point((8, 6), fill=accent[2])
    return im


def drill():
    im, d = canvas()
    # Diagonal mining bit, grip and power cell; intentionally tiny like MI tools.
    d.polygon([(11, 1), (14, 1), (14, 4), (10, 8),
               (8, 6)], fill=DARK)
    d.polygon([(11, 2), (13, 2), (13, 4), (10, 7),
               (9, 6)], fill=TEAL[1])
    d.line([(11, 2), (12, 2), (10, 5)], fill=TEAL[2])
    d.polygon([(7, 5), (11, 9), (8, 12), (4, 8)], fill=DARK)
    d.polygon([(7, 6), (10, 9), (8, 11), (5, 8)], fill=IRON[1])
    d.line([(6, 7), (9, 10)], fill=IRON[2])
    d.polygon([(4, 8), (8, 12), (6, 14), (2, 10)], fill=DARK)
    d.polygon([(4, 9), (7, 12), (6, 13), (3, 10)], fill=BLUE[1])
    d.point((5, 11), fill=BLUE[2])
    d.rectangle((2, 11, 3, 14), fill=IRON[0])
    d.point((13, 2), fill="#ebfbf2")
    d.line([(9, 7), (10, 8)], fill=IRON[0])
    d.point((4, 10), fill=BLUE[2])
    d.point((2, 13), fill=IRON[2])
    return im


def provision():
    im, d = canvas()
    d.polygon([(3, 5), (11, 5), (13, 8), (11, 13),
               (4, 13), (2, 10)], fill=DARK)
    d.polygon([(4, 6), (11, 6), (12, 8), (10, 12),
               (4, 12), (3, 10)], fill="#b78b58")
    d.line([(4, 6), (10, 6)], fill="#e4c79a")
    d.line([(4, 9), (11, 9)], fill="#6e4c32")
    d.rectangle((7, 4, 8, 12), fill=COPPER[1])
    d.point((7, 3), fill=GOLD[2])
    d.polygon([(5, 6), (7, 4), (7, 8)], fill=GREEN[1])
    d.point((10, 7), fill="#f3d7aa")
    d.point((5, 11), fill="#68482c")
    d.point((10, 10), fill="#e6b97d")
    return im


def resin():
    im, d = canvas()
    d.polygon([(8, 1), (12, 7), (12, 11), (10, 14),
               (5, 14), (3, 11), (3, 7)], fill=DARK)
    d.polygon([(8, 2), (11, 7), (11, 11), (9, 13),
               (5, 13), (4, 10), (4, 7)], fill=GOLD[0])
    d.polygon([(8, 3), (10, 7), (9, 11), (6, 12),
               (5, 9)], fill=GOLD[1])
    d.line([(7, 4), (6, 8)], fill=GOLD[2])
    d.point((9, 6), fill="#fff0af")
    d.line([(10, 9), (9, 12)], fill=GOLD[0])
    d.point((5, 10), fill=GOLD[2])
    d.point((8, 5), fill="#fff0af")
    return im


def insulator():
    im, d = canvas()
    d.rectangle((3, 6, 12, 10), fill=DARK)
    d.rectangle((4, 7, 11, 9), fill=IRON[1])
    d.rectangle((6, 2, 9, 13), fill=DARK)
    d.rectangle((7, 3, 8, 12), fill=TEAL[1])
    d.rectangle((3, 5, 5, 11), fill=COPPER[0])
    d.rectangle((10, 5, 12, 11), fill=COPPER[0])
    d.line([(3, 5), (5, 5)], fill=COPPER[2])
    d.line([(10, 5), (12, 5)], fill=COPPER[2])
    d.point((7, 7), fill=TEAL[2])
    d.line([(4, 7), (4, 10)], fill=COPPER[1])
    d.line([(11, 8), (11, 10)], fill=SHADE)
    d.point((8, 4), fill="#eef9e8")
    return im


def lattice():
    im, d = canvas()
    d.polygon([(7, 1), (13, 7), (7, 14), (1, 7)], fill=DARK)
    d.polygon([(7, 2), (12, 7), (7, 13), (2, 7)], fill=VIOLET[0])
    for off in (0, 3):
        d.line([(4 + off, 5), (9 + off, 10)], fill=VIOLET[2])
        d.line([(9 - off, 4), (4 - off, 9)], fill=VIOLET[1])
    diamond(d, (5, 5, 9, 9), GOLD)
    d.point((7, 2), fill=VIOLET[2])
    d.point((11, 7), fill=VIOLET[1])
    d.point((5, 11), fill=VIOLET[2])
    return im


def stabilizer(ring=GOLD, crystal=TEAL):
    im, d = canvas()
    d.ellipse((2, 2, 13, 13), fill=DARK)
    d.arc((3, 3, 12, 12), 30, 150, fill=ring[2], width=2)
    d.arc((3, 3, 12, 12), 210, 330, fill=ring[1], width=2)
    d.line([(1, 7), (4, 7)], fill=IRON[2])
    d.line([(11, 7), (14, 7)], fill=IRON[2])
    diamond(d, (5, 4, 10, 11), crystal)
    d.point((7, 6), fill="#ffffff")
    d.point((4, 5), fill=ring[2])
    d.point((11, 10), fill=ring[0])
    d.point((10, 4), fill=ring[1])
    return im


def mount():
    im, d = canvas()
    d.polygon([(7, 2), (10, 6), (10, 11), (12, 12),
               (12, 14), (3, 14), (3, 12), (5, 11),
               (5, 6)], fill=DARK)
    d.polygon([(7, 3), (9, 6), (9, 11), (11, 12),
               (11, 13), (4, 13), (6, 11), (6, 6)], fill=COPPER[1])
    d.line([(6, 6), (7, 4)], fill=COPPER[2])
    diamond(d, (6, 5, 9, 9), TEAL)
    d.line([(4, 12), (11, 12)], fill=GOLD[2])
    d.point((5, 8), fill=COPPER[2])
    d.point((9, 10), fill=COPPER[0])
    d.point((10, 12), fill="#f4d677")
    return im


def interface():
    im, d = canvas()
    d.rectangle((2, 3, 13, 12), fill=DARK)
    d.rectangle((3, 4, 12, 11), fill=IRON[1])
    d.rectangle((4, 5, 11, 10), fill=IRON[0])
    d.rectangle((5, 5, 10, 9), fill=BLUE[0])
    d.line([(5, 5), (9, 5)], fill=BLUE[2])
    d.line([(4, 12), (11, 12)], fill=COPPER[1])
    d.rectangle((6, 7, 7, 8), fill=TEAL[2])
    d.rectangle((9, 7, 10, 8), fill=GOLD[2])
    d.point((2, 2), fill=IRON[2])
    d.point((13, 2), fill=IRON[2])
    d.line([(3, 4), (3, 9)], fill=IRON[2])
    d.line([(12, 7), (12, 11)], fill=IRON[0])
    d.point((5, 10), fill=GOLD[1])
    d.point((10, 10), fill=TEAL[1])
    return im


def soften_corners(im):
    """A few translucent edge pixels, never an image-wide blur."""
    src = im.copy()
    candidates = []
    for y in range(1, 15):
        for x in range(1, 15):
            if src.getpixel((x, y))[3]:
                continue
            cardinal = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            if any(src.getpixel(p)[3] for p in cardinal):
                continue
            diagonal = [(x - 1, y - 1), (x + 1, y - 1),
                        (x - 1, y + 1), (x + 1, y + 1)]
            solid = [p for p in diagonal if src.getpixel(p)[3] == 255]
            if len(solid) != 1:
                continue
            color = src.getpixel(solid[0])[:3]
            quadrant = (x >= 8, y >= 8)
            candidates.append((quadrant, abs(x - 7.5) + abs(y - 7.5),
                               x, y, color))
    used = set()
    for quadrant, _, x, y, color in sorted(candidates, key=lambda r: r[1]):
        if quadrant in used:
            continue
        # 25% opacity is visible on dark and light GUI backgrounds, but does
        # not create a fuzzy fringe around every pixel of the silhouette.
        im.putpixel((x, y), (*color, 64))
        used.add(quadrant)
    return im


def make(name):
    if name.startswith("armor_core_t"):
        return armor_core(int(name.removeprefix("armor_core_t")))
    if name == "electrical_focus":
        return crystal_focus(COPPER, TEAL, True)
    if name == "industrial_focus":
        return crystal_focus(IRON, BLUE, True)
    if name == "alchemical_catalyst":
        return vial(VIOLET)
    if name == "soul_stabilizer":
        return stabilizer(IRON, VIOLET)
    if name == "arcane_resin":
        return resin()
    if name == "ritual_mount":
        return mount()
    if name == "ritual_frame":
        return frame(IRON, VIOLET)
    if name == "elemental_insulator":
        return insulator()
    if name.startswith("seal_"):
        return circular_seal({"seal_life": GREEN, "seal_mind": BLUE,
                              "seal_soul": VIOLET, "seal_elements": GOLD}[name],
                             name.removeprefix("seal_"))
    if name == "boss_seal":
        return circular_seal(RED, "boss")
    if name == "convergence_core":
        return matrix(IRON, VIOLET)
    if name == "infinity_stabilizer":
        return stabilizer(GOLD, TEAL)
    if name == "engineering_matrix":
        return matrix(COPPER, TEAL)
    if name == "enchantment_lattice":
        return lattice()
    if name == "reborn_interface":
        return interface()
    if name == "mekanism_interface":
        return interface()  # historical removed item; preserve a clean fallback
    if name == "provision_bundle":
        return provision()
    if name == "expedition_emblem":
        return scroll_like(GOLD, GREEN, "map")
    if name == "relic_research":
        return scroll_like(COPPER, VIOLET, "grid")
    if name == "quantum_quarry_drill":
        return drill()
    raise ValueError(name)


def main():
    if len(NAMES) != 31:
        raise RuntimeError(f"Expected 31 icons, found {len(NAMES)}")
    OUT.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        im = soften_corners(make(name))
        if im.size != (16, 16) or not im.getbbox():
            raise RuntimeError(f"Invalid sprite: {name}")
        im.save(OUT / f"{name}.png", optimize=True)

    manifest = [
        {"item": f"kubejs:{name}", "texture": str(OUT / f"{name}.png"),
         "size": [16, 16],
         "sha256": hashlib.sha256((OUT / f"{name}.png").read_bytes()).hexdigest()}
        for name in NAMES
    ]
    (ROOT / "custom/item-textures/installed.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Enlarged nearest-neighbour review sheet; not shipped as a game texture.
    cols = 6
    tile = 96
    rows = (len(NAMES) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile, rows * (tile + 20)), "#24282e")
    d = ImageDraw.Draw(sheet)
    for i, name in enumerate(NAMES):
        x, y = (i % cols) * tile, (i // cols) * (tile + 20)
        sprite = Image.open(OUT / f"{name}.png").convert("RGBA")
        sheet.paste(sprite.resize((80, 80), Image.Resampling.NEAREST),
                    (x + 8, y + 4), sprite.resize((80, 80), Image.Resampling.NEAREST))
        d.text((x + 3, y + 85), name[:15], fill="#e1e5e1")
    sheet.save(PREVIEW)

    for dest in [
        Path.home() / "AppData/Roaming/PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft/kubejs/assets/kubejs/textures/item/progression",
        ROOT / "build/prism/Arcane Industry Prototype/minecraft/kubejs/assets/kubejs/textures/item/progression",
    ]:
        if dest.exists():
            for name in NAMES:
                shutil.copy2(OUT / f"{name}.png", dest / f"{name}.png")
    print(json.dumps({"count": len(NAMES), "size": [16, 16],
                      "preview": str(PREVIEW)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
