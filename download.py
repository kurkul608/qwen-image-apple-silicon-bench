"""Download the weights for every variant into models/."""
import shutil
from pathlib import Path

from huggingface_hub import hf_hub_download

from variants import VAE, VARIANTS, local_path


def main():
    sources = {VAE}
    for variant in VARIANTS.values():
        sources |= {variant["diffusion"], variant["encoder"]}
    for source in sorted(sources):
        target = Path(local_path(source))
        if target.exists():
            print(f"have {target}", flush=True)
            continue
        target.parent.mkdir(exist_ok=True)
        downloaded = hf_hub_download(*source)
        shutil.move(Path(downloaded).resolve(), target)
        print(f"got {target}", flush=True)


if __name__ == "__main__":
    main()
