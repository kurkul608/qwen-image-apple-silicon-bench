"""Model variants under test and the files each one needs."""

TURBO_REPO = "abenzerps/Qwen-Image-2.1-Turbo-Quantized"
BASE_REPO = "unsloth/Qwen-Image-2.1-GGUF"

VAE = (TURBO_REPO, "vae/qwen_image_2.1_vae_bf16.safetensors")
ENCODER_INT8 = (TURBO_REPO, "text_encoders/qwen3vl_8b_int8_convrot.safetensors")
ENCODER_BF16 = (TURBO_REPO, "text_encoders/qwen3vl_8b_bf16.safetensors")

TURBO_SAMPLING = ["--sigmas", "qwen-image-2.1-turbo", "--steps", "8", "--cfg-scale", "1.0"]
# Official defaults: 40 steps, no guidance. See QwenImage21Pipeline in diffusers.
BASE_SAMPLING = ["--steps", "40", "--cfg-scale", "1.0"]
# The sd.cpp docs example. Kept to document why it should not be used.
BASE_CFG6_SAMPLING = ["--steps", "20", "--cfg-scale", "6.0"]

VARIANTS = {
    "turbo-q4": {
        "label": "Turbo Q4_K_M",
        "diffusion": (TURBO_REPO, "qwen-image-2.1-turbo-Q4_K_M.gguf"),
        "encoder": ENCODER_INT8,
        "sampling": TURBO_SAMPLING,
    },
    "turbo-q8": {
        "label": "Turbo Q8_0",
        "diffusion": (TURBO_REPO, "qwen-image-2.1-turbo-Q8_0.gguf"),
        "encoder": ENCODER_INT8,
        "sampling": TURBO_SAMPLING,
    },
    "base-q8": {
        "label": "Base Q8_0",
        "diffusion": (BASE_REPO, "qwen-image-2.1-Q8_0.gguf"),
        "encoder": ENCODER_INT8,
        "sampling": BASE_SAMPLING,
    },
    "base-f16": {
        "label": "Original F16",
        "diffusion": (BASE_REPO, "qwen-image-2.1-F16.gguf"),
        "encoder": ENCODER_BF16,
        "sampling": BASE_SAMPLING,
    },
    "base-q8-cfg6": {
        "label": "Base Q8_0, CFG 6",
        "diffusion": (BASE_REPO, "qwen-image-2.1-Q8_0.gguf"),
        "encoder": ENCODER_INT8,
        "sampling": BASE_CFG6_SAMPLING,
    },
    "base-f16-cfg6": {
        "label": "Original F16, CFG 6",
        "diffusion": (BASE_REPO, "qwen-image-2.1-F16.gguf"),
        "encoder": ENCODER_BF16,
        "sampling": BASE_CFG6_SAMPLING,
    },
}


def local_path(source):
    return f"models/{source[1].rsplit('/', 1)[-1]}"
