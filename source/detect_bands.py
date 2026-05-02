"""
For each rendered page, detect horizontal content bands (rows of fonts)
and split each band into left/right columns. Save each cell as a PNG.

Strategy:
- Convert to grayscale
- For each pixel row, mark "has content" if any pixel is significantly darker than white
- Group consecutive content rows into bands; merge bands that are close together
- For each band, split into left and right halves at column midpoint
- Trim whitespace from each cell, save as PNG
"""

from PIL import Image
from pathlib import Path
import numpy as np
import json

src_dir = Path(__file__).parent / "pages"
out_dir = Path(__file__).parent.parent / "samples"
out_dir.mkdir(exist_ok=True)

# Tunables
WHITE_THRESHOLD = 240   # pixels darker than this count as content
ROW_CONTENT_MIN = 8     # min content pixels in a row to count as "has content"
MIN_BAND_HEIGHT = 60    # min height of a font band
BAND_GAP_MERGE = 12     # merge bands separated by less than this many empty rows
PAD = 8                 # padding around each cropped cell

MAX_BAND_HEIGHT = 260  # if band exceeds this, attempt to split at internal whitespace

def detect_bands(arr):
    """arr is grayscale 2D numpy. Returns list of (y_top, y_bottom) bands."""
    h, w = arr.shape
    has_content = (arr < WHITE_THRESHOLD).sum(axis=1) > ROW_CONTENT_MIN
    bands = []
    in_band = False
    start = 0
    for y, hc in enumerate(has_content):
        if hc and not in_band:
            in_band = True; start = y
        elif not hc and in_band:
            in_band = False
            bands.append([start, y])
    if in_band:
        bands.append([start, h])
    # Merge close bands
    merged = []
    for b in bands:
        if merged and b[0] - merged[-1][1] < BAND_GAP_MERGE:
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    # Filter tiny
    merged = [b for b in merged if (b[1] - b[0]) >= MIN_BAND_HEIGHT]
    # Split tall bands by finding largest internal whitespace gap
    final = []
    for b in merged:
        final.extend(_maybe_split(b, has_content))
    return final

def _maybe_split(band, has_content, depth=0):
    y0, y1 = band
    if y1 - y0 <= MAX_BAND_HEIGHT or depth > 3:
        return [band]
    # Find longest run of empty rows in interior (excluding first/last 30%)
    margin = int((y1 - y0) * 0.25)
    interior_start = y0 + margin
    interior_end = y1 - margin
    best_run = None
    run_start = None
    for y in range(interior_start, interior_end):
        if not has_content[y]:
            if run_start is None:
                run_start = y
        else:
            if run_start is not None:
                length = y - run_start
                if best_run is None or length > best_run[2]:
                    best_run = (run_start, y, length)
                run_start = None
    if run_start is not None:
        length = interior_end - run_start
        if best_run is None or length > best_run[2]:
            best_run = (run_start, interior_end, length)
    if best_run is None or best_run[2] < 4:
        return [band]
    split_y = (best_run[0] + best_run[1]) // 2
    left = _maybe_split([y0, split_y], has_content, depth + 1)
    right = _maybe_split([split_y, y1], has_content, depth + 1)
    return left + right

def trim_cell(img):
    """Trim whitespace from a PIL image."""
    arr = np.array(img.convert("L"))
    has_content = arr < WHITE_THRESHOLD
    if not has_content.any():
        return img
    rows = np.where(has_content.any(axis=1))[0]
    cols = np.where(has_content.any(axis=0))[0]
    top, bot = rows[0], rows[-1] + 1
    left, right = cols[0], cols[-1] + 1
    top = max(0, top - PAD); bot = min(img.height, bot + PAD)
    left = max(0, left - PAD); right = min(img.width, right + PAD)
    return img.crop((left, top, right, bot))

results = []
for page_idx in range(1, 6):
    page_path = src_dir / f"page_{page_idx}.png"
    img = Image.open(page_path)
    arr = np.array(img.convert("L"))
    h, w = arr.shape
    bands = detect_bands(arr)
    print(f"Page {page_idx}: {len(bands)} bands")

    mid_x = w // 2
    for band_idx, (y0, y1) in enumerate(bands):
        for col_idx, (x0, x1) in enumerate([(0, mid_x), (mid_x, w)]):
            cell = img.crop((x0, y0, x1, y1))
            cell = trim_cell(cell)
            # skip empty cells (mostly whitespace)
            cell_arr = np.array(cell.convert("L"))
            if (cell_arr < WHITE_THRESHOLD).sum() < 200:
                continue
            slot = page_idx * 100 + band_idx * 2 + col_idx
            fname = f"slot_{page_idx}_{band_idx+1}_{['L','R'][col_idx]}.png"
            cell.save(out_dir / fname)
            results.append({
                "file": fname,
                "page": page_idx,
                "band": band_idx + 1,
                "col": ["L","R"][col_idx],
                "size": cell.size,
            })
            print(f"  {fname}: {cell.size}")

with open(out_dir / "_extraction_log.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nExtracted {len(results)} cells -> {out_dir}")
