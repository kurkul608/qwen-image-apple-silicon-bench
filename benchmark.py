"""Run one variant over the prompts and record time, memory and stability."""
import argparse
import json
import os
import re
import signal
import subprocess
import threading
import time
from pathlib import Path

from variants import VAE, VARIANTS, local_path

HARDWARE = "m1-pro-32gb"
RESULTS = Path("results") / HARDWARE
SEED = 42
SAMPLE_SECONDS = 5
TIMEOUT_SECONDS = 90 * 60


def read(*args):
    return subprocess.run(args, capture_output=True, text=True).stdout


def swap_used_mb():
    match = re.search(r"used = ([\d.]+)M", read("sysctl", "vm.swapusage"))
    return float(match.group(1)) if match else None


def free_memory_percent():
    match = re.search(r"free percentage: (\d+)%", read("memory_pressure", "-Q"))
    return int(match.group(1)) if match else None


def thermal_pressure():
    match = re.search(r"(\d+)\s*$", read("notifyutil", "-g", "com.apple.system.thermalpressurelevel"))
    return int(match.group(1)) if match else None


class Monitor(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.stop = threading.Event()
        self.swap = []
        self.free = []
        self.thermal = []

    def run(self):
        while not self.stop.wait(SAMPLE_SECONDS):
            self.swap.append(swap_used_mb())
            self.free.append(free_memory_percent())
            self.thermal.append(thermal_pressure())


def known(values):
    return [value for value in values if value is not None]


def seconds_after(text, pattern):
    return round(sum(float(value) for value in re.findall(pattern, text)), 2) or None


def parse_log(text):
    text = text.replace("\r", "\n")
    footprint = re.search(r"(\d+)\s+peak memory footprint", text)
    steps = re.findall(r"\d+/\d+ -\s+([\d.]+)s/it", text)
    total = re.search(r"generate_image completed in ([\d.]+)s", text)
    return {
        "total_s": float(total.group(1)) if total else None,
        "encoder_s": seconds_after(text, r"get_learned_condition completed, taking ([\d.]+)s"),
        "sampling_s": seconds_after(text, r"sampling completed, taking ([\d.]+)s"),
        "vae_s": seconds_after(text, r"decode_first_stage completed, taking ([\d.]+)s"),
        "last_s_per_step": float(steps[-1]) if steps else None,
        "peak_footprint_gb": round(int(footprint.group(1)) / 1e9, 2) if footprint else None,
    }


def command(variant, item, output, width, height, steps=None):
    sampling = list(variant["sampling"])
    if steps:
        sampling[sampling.index("--steps") + 1] = str(steps)
    return [
        "/usr/bin/time", "-l",
        "stable-diffusion.cpp/build/bin/sd-cli",
        "--diffusion-model", local_path(variant["diffusion"]),
        "--llm", local_path(variant["encoder"]),
        "--vae", local_path(VAE),
        *sampling,
        "--sampling-method", "euler",
        "--width", str(width),
        "--height", str(height),
        "--seed", str(SEED),
        "--offload-to-cpu",
        # The text encoder crashes the Metal driver on M1 Pro, so it stays on CPU.
        "--backend", "te=cpu",
        "-p", item["prompt"],
        "-o", str(output),
    ]


def run_process(args, log_path, timeout):
    with log_path.open("w") as log:
        process = subprocess.Popen(
            args, stdout=log, stderr=subprocess.STDOUT, start_new_session=True
        )
        try:
            return process.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return process.returncode, True


def status_of(code, timed_out, output):
    if timed_out:
        return "timeout"
    if code == 0 and output.exists():
        return "ok"
    return "crashed"


def run_one(key, item, run, timeout):
    folder = RESULTS / key / f"run-{run}"
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / f"{item['id']}.png"
    log_path = folder / f"{item['id']}.log"
    args = command(VARIANTS[key], item, output, item["width"], item["height"])

    swap_before = swap_used_mb()
    free_before = free_memory_percent()
    monitor = Monitor()
    monitor.start()
    started = time.time()
    code, timed_out = run_process(args, log_path, timeout)
    wall = round(time.time() - started, 1)
    monitor.stop.set()
    monitor.join()

    return {
        "variant": key,
        "prompt": item["id"],
        "run": run,
        "size": f"{item['width']}x{item['height']}",
        "status": status_of(code, timed_out, output),
        "exit_code": code,
        "wall_s": wall,
        **parse_log(log_path.read_text(errors="replace")),
        "swap_before_mb": swap_before,
        "swap_peak_mb": max(known(monitor.swap), default=None),
        "free_before_percent": free_before,
        "free_min_percent": min(known(monitor.free), default=None),
        "thermal_max": max(known(monitor.thermal), default=None),
    }


def load_records():
    path = RESULTS / "metrics.json"
    return json.loads(path.read_text()) if path.exists() else []


def save_record(record):
    records = load_records()
    records.append(record)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "metrics.json").write_text(json.dumps(records, indent=2) + "\n")


def smoke(key):
    """Small render that proves a variant loads and finishes before a long run."""
    variant = VARIANTS[key]
    folder = Path("smoke")
    folder.mkdir(exist_ok=True)
    item = {"prompt": "A red ceramic cup on a wooden table"}
    output = folder / f"{key}.png"
    log_path = folder / f"{key}.log"
    code, timed_out = run_process(
        command(variant, item, output, 512, 512, steps=2), log_path, TIMEOUT_SECONDS
    )
    print(key, status_of(code, timed_out, output), parse_log(log_path.read_text(errors="replace")), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    parser.add_argument("--run", type=int, default=1)
    parser.add_argument("--prompts", nargs="*", help="prompt ids, all by default")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--timeout", type=int, default=TIMEOUT_SECONDS)
    options = parser.parse_args()

    if options.smoke:
        smoke(options.variant)
        return

    done = {
        (record["prompt"], record["run"])
        for record in load_records()
        if record["variant"] == options.variant
    }
    for item in json.loads(Path("prompts.json").read_text()):
        if options.prompts and item["id"] not in options.prompts:
            continue
        if (item["id"], options.run) in done:
            continue
        record = run_one(options.variant, item, options.run, options.timeout)
        save_record(record)
        print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
