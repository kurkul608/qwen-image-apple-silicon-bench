"""Build result tables, pixel comparisons and image grids from the raw runs."""
import json
from pathlib import Path
from statistics import mean

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

from variants import VARIANTS

RESULTS = Path("results/m1-pro-32gb")
DOCS = Path("docs")
SQUARE = "1024x1024"
POSTER = "1024x1536"
GRID_CELL = 420
GRID_LABEL = 44
ORDER = ["turbo-q4", "turbo-q8", "base-q8", "base-f16"]
# Runs with the sd.cpp docs settings. Shown in the timing table only.
CFG6 = ["base-q8-cfg6", "base-f16-cfg6"]


def image_path(variant, prompt, run=1):
    return RESULTS / variant / f"run-{run}" / f"{prompt}.png"


def minutes(seconds):
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def timing_rows(records):
    rows = [
        "| Model | Size | Finished | Mean time | Range | Per step | Peak memory | Peak swap | Thermal |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for key in ORDER + CFG6:
        for size in (SQUARE, POSTER):
            group = [r for r in records if r["variant"] == key and r["size"] == size]
            if not group:
                continue
            done = [r for r in group if r["status"] == "ok"]
            label = VARIANTS[key]["label"]
            if not done:
                rows.append(f"| {label} | {size} | 0/{len(group)} | - | - | - | - | - | - |")
                continue
            totals = [r["total_s"] for r in done]
            steps = [r["last_s_per_step"] for r in done]
            rows.append(
                f"| {label} | {size} | {len(done)}/{len(group)} "
                f"| {minutes(mean(totals))} | {minutes(min(totals))}-{minutes(max(totals))} "
                f"| {mean(steps):.0f} s "
                f"| {max(r['peak_footprint_gb'] for r in done):.1f} GB "
                f"| {max(r['swap_peak_mb'] for r in done) / 1024:.1f} GB "
                f"| {max(r['thermal_max'] for r in done)} |"
            )
    return rows


def stage_rows(records):
    rows = [
        "| Model | Size | Text encoder | Sampling | VAE decode |",
        "| --- | --- | --- | --- | --- |",
    ]
    for key in ORDER:
        for size in (SQUARE, POSTER):
            done = [
                r for r in records
                if r["variant"] == key and r["size"] == size and r["status"] == "ok"
            ]
            if done:
                rows.append(
                    f"| {VARIANTS[key]['label']} | {size} "
                    f"| {mean(r['encoder_s'] for r in done):.0f} s "
                    f"| {mean(r['sampling_s'] for r in done):.0f} s "
                    f"| {mean(r['vae_s'] for r in done):.0f} s |"
                )
    return rows


def load_gray(path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.uint8)


def compare(first, second):
    a, b = load_gray(first), load_gray(second)
    # Identical images give an infinite PSNR, which the table prints as "identical".
    with np.errstate(divide="ignore"):
        psnr = peak_signal_noise_ratio(a, b, data_range=255)
    return structural_similarity(a, b, data_range=255), psnr


def comparison_rows(prompts):
    rows = ["| Pair | Prompt | SSIM | PSNR |", "| --- | --- | --- | --- |"]
    pairs = [
        ("Quantization: Turbo Q4 vs Q8", ("turbo-q4", 1), ("turbo-q8", 1)),
        ("Quantization: Base Q8 vs Original F16", ("base-q8", 1), ("base-f16", 1)),
        ("Repeatability: Turbo Q8 run 1 vs 2", ("turbo-q8", 1), ("turbo-q8", 2)),
        ("Repeatability: Turbo Q4 run 1 vs 2", ("turbo-q4", 1), ("turbo-q4", 2)),
    ]
    for name, (left, left_run), (right, right_run) in pairs:
        for prompt in prompts:
            first = image_path(left, prompt, left_run)
            second = image_path(right, prompt, right_run)
            if first.exists() and second.exists():
                ssim, psnr = compare(first, second)
                psnr_text = "identical" if np.isinf(psnr) else f"{psnr:.1f} dB"
                rows.append(f"| {name} | {prompt} | {ssim:.4f} | {psnr_text} |")
    return rows


def quality_rows():
    path = RESULTS / "quality.json"
    if not path.exists():
        return []
    rows = [
        "| Model | Prompt | Text accuracy | Anatomy | Prompt match | Artifacts | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in json.loads(path.read_text()):
        rows.append(
            f"| {VARIANTS[item['variant']]['label']} | {item['prompt']} | {item['text']} "
            f"| {item['anatomy']} | {item['match']} | {item['artifacts']} | {item['notes']} |"
        )
    return rows


def font(size):
    return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)


def fitted(path, width, height):
    image = Image.open(path).convert("RGB")
    image.thumbnail((width, height))
    cell = Image.new("RGB", (width, height), "white")
    cell.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
    return cell


def grid(prompts):
    columns = [key for key in ORDER if image_path(key, prompts[0]).exists()]
    if not columns:
        return
    height = GRID_CELL * 1.5
    rows_height = [int(height) if "poster" in prompt else GRID_CELL for prompt in prompts]
    canvas = Image.new(
        "RGB",
        (GRID_CELL * len(columns), GRID_LABEL + sum(rows_height)),
        "white",
    )
    draw = ImageDraw.Draw(canvas)
    for index, key in enumerate(columns):
        draw.text((index * GRID_CELL + 12, 10), VARIANTS[key]["label"], fill="black", font=font(22))
    top = GRID_LABEL
    for prompt, row_height in zip(prompts, rows_height):
        for index, key in enumerate(columns):
            path = image_path(key, prompt)
            if path.exists():
                canvas.paste(fitted(path, GRID_CELL, row_height), (index * GRID_CELL, top))
        top += row_height
    canvas.save(DOCS / "grid.jpg", quality=88)


def crops():
    path = RESULTS / "crops.json"
    if not path.exists():
        return
    for crop in json.loads(path.read_text()):
        boxes = crop["boxes"]
        width = max(box[2] - box[0] for box in boxes.values())
        height = max(box[3] - box[1] for box in boxes.values())
        canvas = Image.new(
            "RGB", ((width + 12) * len(boxes), height + GRID_LABEL), "white"
        )
        draw = ImageDraw.Draw(canvas)
        for index, (key, box) in enumerate(boxes.items()):
            part = Image.open(image_path(key, crop["prompt"])).convert("RGB").crop(box)
            left = index * (width + 12)
            canvas.paste(part, (left, GRID_LABEL))
            draw.text((left + 8, 10), VARIANTS[key]["label"], fill="black", font=font(22))
        canvas.save(DOCS / f"crop-{crop['name']}.jpg", quality=92)


def main():
    DOCS.mkdir(exist_ok=True)
    records = json.loads((RESULTS / "metrics.json").read_text())
    prompts = [item["id"] for item in json.loads(Path("prompts.json").read_text())]
    sections = [
        ("Time, memory and stability", timing_rows(records)),
        ("Time per stage", stage_rows(records)),
        ("Pixel comparison", comparison_rows(prompts)),
        ("Quality review", quality_rows()),
    ]
    lines = []
    for title, rows in sections:
        if rows:
            lines += [f"## {title}", "", *rows, ""]
    (RESULTS / "summary.md").write_text("\n".join(lines))
    grid(prompts)
    crops()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
