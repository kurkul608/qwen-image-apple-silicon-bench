#!/usr/bin/env bash
# Full matrix. Finished prompts are skipped, so a rerun only fills the gaps.
set -uo pipefail

run() { .venv/bin/python benchmark.py "$@"; }

run --variant turbo-q8 --run 1
run --variant turbo-q4 --run 1
run --variant base-q8 --run 1
run --variant turbo-q4 --run 2
run --variant turbo-q8 --run 2
run --variant base-f16 --run 1 --timeout 9000

# The sd.cpp docs example, kept to show why it should not be used.
run --variant base-f16-cfg6 --run 1 --prompts 3-typography
run --variant base-q8-cfg6 --run 1
