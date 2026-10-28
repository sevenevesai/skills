"""Cut a generated sheet of subjects (icons, sprites, items) into one square PNG per subject.

Usage: python slice_sheet.py SHEET.png OUT_DIR --rows R --cols C [--names a,b,c] [--size 384]
                             [--margin 0.08]

The image model ignores requested cell padding (subjects fill ~90% of a cell) and does not keep
cells equal, so cuts go through the detected empty gutters, not at equal divisions: columns
are cut across the whole sheet, then each column strip is cut into rows on its own. When a
subject in one row reaches past another row's column gutter, rows are cut first instead. When
neither order has every gutter, each connected subject blob goes to the grid cell nearest its
centre of mass and is cut out by its own pixels (needs scipy).

Each cell's subject is found by alpha or, when the sheet came back fully opaque (a requested
transparent background is often ignored), by distance from the background colour sampled near
the top-left corner. The subject is trimmed, given a transparent background, padded to a square
with a uniform margin, and resized to --size. With --rows 1 --cols 1 it cuts out a single image.

Exit code 1 when a gutter is missing (subjects overlap) or a cell is empty; the report says which.
Needs numpy and Pillow; scipy only for the blob fallback.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

BG_TOLERANCE = 40  # RGB distance from the background colour that still counts as background
ALPHA_FLOOR = 24  # alpha at or below this is background; soft model edges carry faint alpha


def subject_mask(img: Image.Image, bg: np.ndarray | None) -> np.ndarray:
    arr = np.asarray(img)
    if bg is None:
        return arr[..., 3] > ALPHA_FLOOR
    dist = np.linalg.norm(arr[..., :3].astype(int) - bg, axis=-1)
    return dist > BG_TOLERANCE


def cuts(occupied: np.ndarray, n: int) -> tuple[list[int], int]:
    """Cut positions splitting a 1-D occupancy profile into n parts, plus the count of cuts
    that had no empty gutter and fell back to the equal division."""
    length = len(occupied)
    runs, start = [], None
    for i, v in enumerate(occupied):
        if not v and start is None:
            start = i
        if v and start is not None:
            if start > 0:
                runs.append((start, i))
            start = None
    positions, missing = [0], 0
    for k in range(1, n):
        ideal = length * k / n
        near = [r for r in runs if abs((r[0] + r[1]) / 2 - ideal) < length / (2 * n)]
        if near:
            best = max(near, key=lambda r: r[1] - r[0])
            positions.append((best[0] + best[1]) // 2)
        else:
            positions.append(round(ideal))
            missing += 1
    positions.append(length)
    return positions, missing


def grid_boxes(mask: np.ndarray, rows: int, cols: int) -> tuple[list[tuple[int, int, int, int]], list[str]]:
    """Cell boxes (x0, y0, x1, y1) in reading order, cut through real gutters: columns first,
    else rows first. Returns the columns-first problems when neither order has every gutter."""
    tried = []
    for cols_first in (True, False):
        outer_n, inner_n, outer_axis, what = (cols, rows, 0, "column") if cols_first else (rows, cols, 1, "row")
        other = "row" if cols_first else "column"
        problems, boxes = [], [(0, 0, 0, 0)] * (rows * cols)
        ocuts, omiss = cuts(mask.any(axis=outer_axis), outer_n)
        if omiss:
            problems.append(f"{omiss} {what} gutter(s) missing: subjects overlap across {what}s")
        for o in range(outer_n):
            strip = mask[:, ocuts[o]:ocuts[o + 1]] if cols_first else mask[ocuts[o]:ocuts[o + 1], :]
            icuts, imiss = cuts(strip.any(axis=1 - outer_axis), inner_n)
            if imiss:
                problems.append(f"{what} {o + 1}: {imiss} {other} gutter(s) missing: subjects overlap")
            for i in range(inner_n):
                a, b = (ocuts[o], ocuts[o + 1]), (icuts[i], icuts[i + 1])
                r, c = (i, o) if cols_first else (o, i)
                boxes[r * cols + c] = (a[0], b[0], a[1], b[1]) if cols_first else (b[0], a[0], b[1], a[1])
        if not problems:
            return boxes, []
        tried.append((boxes, problems))
    return tried[0]


def component_masks(mask: np.ndarray, rows: int, cols: int) -> list[np.ndarray]:
    """Per-cell subject masks from connected blobs, for sheets with no straight gutters. Blobs
    within a few pixels are merged first so a whisker or a spout stays with its subject."""
    from scipy import ndimage  # only this fallback needs it

    h, w = mask.shape
    labels, n = ndimage.label(ndimage.binary_dilation(mask, iterations=3))
    labels = np.where(mask, labels, 0)
    cells = [np.zeros_like(mask) for _ in range(rows * cols)]
    centres = ndimage.center_of_mass(mask, labels, range(1, n + 1))
    for label, (cy, cx) in enumerate(centres, 1):
        if np.isnan(cy):
            continue
        r = min(rows - 1, int(cy // (h / rows)))
        c = min(cols - 1, int(cx // (w / cols)))
        cells[r * cols + c] |= labels == label
    return cells


def slice_sheet(sheet: str | Path, out_dir: str | Path, rows: int, cols: int, names: list[str],
                size: int = 384, margin: float = 0.08) -> tuple[list[str], list[str]]:
    """Writes OUT_DIR/<name>.png per cell. Returns (report lines, problems); an empty problems
    list means every cell was cut through a real gutter and held a subject."""
    img = Image.open(sheet)
    has_alpha = img.mode in ("RGBA", "LA") or "transparency" in img.info
    img = img.convert("RGBA")
    if has_alpha and np.asarray(img)[..., 3].min() == 255:
        has_alpha = False  # an alpha channel that is fully opaque carries no cutout
    bg = None if has_alpha else np.asarray(img)[2, 2, :3].astype(int)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    w, h = img.size
    report = [f"sheet {w}x{h} alpha={'yes' if has_alpha else 'no (colour-keyed)'}"]
    sheet_mask = subject_mask(img, bg)
    boxes, problems = grid_boxes(sheet_mask, rows, cols)
    # (box, mask within the box, whether pixels outside the mask must be cleared)
    cells = [(box, sheet_mask[box[1]:box[3], box[0]:box[2]], False) for box in boxes]
    if problems:
        try:
            masks = component_masks(sheet_mask, rows, cols)
        except ImportError:
            return report, problems + ["install scipy to cut overlapping subjects by their blobs"]
        problems = []
        report[0] += " sliced by blobs"
        cells = []
        for m in masks:
            ys, xs = np.nonzero(m) if m.any() else (np.array([0]), np.array([0]))
            box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
            cells.append((box, m[box[1]:box[3], box[0]:box[2]], True))
    for i, (box, mask, isolate) in enumerate(cells):
        name = names[i] if i < len(names) else f"cell{i + 1}"
        cell = img.crop(box)
        if not mask.any():
            problems.append(f"{name}: empty cell")
            continue
        ys, xs = np.nonzero(mask)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        fill = max(x1 - x0, y1 - y0) / min(w / cols, h / rows)
        subject = cell.crop((x0, y0, x1, y1))
        if not has_alpha or isolate:
            rgba = np.asarray(subject).copy()
            keep = mask[y0:y1, x0:x1]
            rgba[..., 3] = np.where(keep, rgba[..., 3] if has_alpha else 255, 0)
            subject = Image.fromarray(rgba)
        side = round(max(subject.size) / (1 - 2 * margin))
        canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        canvas.paste(subject, ((side - subject.width) // 2, (side - subject.height) // 2))
        canvas.resize((size, size), Image.LANCZOS).save(out / f"{name}.png")
        report.append(f"  {name:<14} bbox {x1 - x0}x{y1 - y0}  fill {fill:.0%}")
    return report, problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sheet")
    ap.add_argument("out_dir")
    ap.add_argument("--rows", type=int, default=1)
    ap.add_argument("--cols", type=int, default=1)
    ap.add_argument("--names", default="", help="comma-separated output names in reading order")
    ap.add_argument("--size", type=int, default=384, help="output side in pixels (default 384)")
    ap.add_argument("--margin", type=float, default=0.08, help="clear border as a fraction of the side")
    args = ap.parse_args()
    names = [n.strip() for n in args.names.split(",")] if args.names else []
    report, problems = slice_sheet(args.sheet, args.out_dir, args.rows, args.cols, names, args.size, args.margin)
    print("\n".join(report))
    for p in problems:
        print("PROBLEM", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
