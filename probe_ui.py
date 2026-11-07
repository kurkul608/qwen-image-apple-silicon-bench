"""Follow-up on the 4-ui prompt: is Base's weak layout a seed accident or a lack of guidance?"""
import json

from PIL import Image, ImageDraw

from benchmark import RESULTS, TIMEOUT_SECONDS, command, parse_log, run_process, status_of
from report import font
from variants import VARIANTS

PROMPT_ID = "4-ui"
# (variant, seed, cfg). Seed 42 at CFG 1 is already in the main runs.
RUNS = [
    ("turbo-q8", 1, None), ("turbo-q8", 2, None), ("turbo-q8", 3, None),
    ("base-q8", 1, None), ("base-q8", 2, None), ("base-q8", 3, None),
    ("base-q8", 42, 2.5), ("base-q8", 42, 4.0),
]


def set_flag(args, flag, value):
    args[args.index(flag) + 1] = str(value)


def main():
    item = next(p for p in json.loads(open("prompts.json").read()) if p["id"] == PROMPT_ID)
    folder = RESULTS / "ui-probe"
    folder.mkdir(parents=True, exist_ok=True)
    summary_path = folder / "probe.json"
    records = json.loads(summary_path.read_text()) if summary_path.exists() else []
    done = {record["name"] for record in records if record["status"] == "ok"}

    for key, seed, cfg in RUNS:
        name = f"{key}-seed{seed}" + (f"-cfg{cfg}" if cfg else "")
        if name in done:
            continue
        output = folder / f"{name}.png"
        log_path = folder / f"{name}.log"
        args = command(VARIANTS[key], item, output, item["width"], item["height"])
        set_flag(args, "--seed", seed)
        if cfg:
            set_flag(args, "--cfg-scale", cfg)
        code, timed_out = run_process(args, log_path, TIMEOUT_SECONDS)
        record = {
            "name": name, "variant": key, "seed": seed,
            "cfg": cfg or 1.0, "status": status_of(code, timed_out, output),
            **parse_log(log_path.read_text(errors="replace")),
        }
        records = [r for r in records if r["name"] != name] + [record]
        summary_path.write_text(json.dumps(records, indent=2) + "\n")
        print(name, record["status"], record["total_s"], flush=True)

    grid(folder)


def grid(folder, cell=400, label=40):
    main = RESULTS / "{}" / "run-1" / f"{PROMPT_ID}.png"
    rows = [
        [(str(main).format("turbo-q8"), "Turbo Q8, seed 42")]
        + [(folder / f"turbo-q8-seed{s}.png", f"Turbo Q8, seed {s}") for s in (1, 2, 3)],
        [(str(main).format("base-q8"), "Base Q8, seed 42")]
        + [(folder / f"base-q8-seed{s}.png", f"Base Q8, seed {s}") for s in (1, 2, 3)],
        [(str(main).format("base-q8"), "Base Q8, seed 42, CFG 1")]
        + [(folder / f"base-q8-seed42-cfg{c}.png", f"Base Q8, seed 42, CFG {c:g}") for c in (2.5, 4.0)],
    ]
    canvas = Image.new("RGB", (cell * 4, (cell + label) * len(rows)), "white")
    draw = ImageDraw.Draw(canvas)
    for y, row in enumerate(rows):
        top = y * (cell + label)
        for x, (path, text) in enumerate(row):
            canvas.paste(Image.open(path).convert("RGB").resize((cell, cell)), (x * cell, top + label))
            draw.text((x * cell + 10, top + 8), text, fill="black", font=font(20))
    canvas.save("docs/ui-probe.jpg", quality=85)


if __name__ == "__main__":
    main()
