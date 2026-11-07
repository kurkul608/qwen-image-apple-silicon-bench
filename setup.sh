#!/usr/bin/env bash
# Creates the Python environment and builds stable-diffusion.cpp with Metal.
set -euo pipefail

SD_CPP_COMMIT=5a1ba5d

[ -d .venv ] || uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
export PATH="$PWD/.venv/bin:$PATH"

if [ ! -d stable-diffusion.cpp ]; then
  git clone --recursive https://github.com/leejet/stable-diffusion.cpp
fi
git -C stable-diffusion.cpp checkout "$SD_CPP_COMMIT"
git -C stable-diffusion.cpp submodule update --init --recursive

cmake -S stable-diffusion.cpp -B stable-diffusion.cpp/build \
  -DCMAKE_BUILD_TYPE=Release -DSD_METAL=ON
cmake --build stable-diffusion.cpp/build --config Release -j8 --target sd-cli
