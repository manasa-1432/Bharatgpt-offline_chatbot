import base64
from functools import lru_cache
from pathlib import Path

import yaml
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler

PROJECT_ROOT = Path(__file__).resolve().parent
with (PROJECT_ROOT / "config.yaml").open("r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@lru_cache(maxsize=1)
def _load_image_model(model_path: str, projector_path: str) -> Llama:
    model_file = Path(model_path)
    projector_file = Path(projector_path)
    if not model_file.is_absolute():
        model_file = PROJECT_ROOT / model_file
    if not projector_file.is_absolute():
        projector_file = PROJECT_ROOT / projector_file

    if not model_file.is_file():
        raise FileNotFoundError(f"LLaVA model not found: {model_file}")
    if not projector_file.is_file():
        raise FileNotFoundError(f"LLaVA image projector not found: {projector_file}")

    chat_handler = Llava15ChatHandler(clip_model_path=str(projector_file))
    return Llama(
        model_path=str(model_file),
        chat_handler=chat_handler,
        n_ctx=2048,
        n_gpu_layers=0,
        verbose=False,
    )


def answer_image_question(image_bytes: bytes, mime_type: str, question: str) -> str:
    if not image_bytes:
        raise ValueError("The uploaded image is empty.")
    if mime_type not in SUPPORTED_IMAGE_TYPES:
        raise ValueError("Use a JPG, PNG, or WebP image.")

    prompt = question.strip() or "Describe this image."
    image_data = base64.b64encode(image_bytes).decode("ascii")
    image_url = f"data:{mime_type};base64,{image_data}"

    model_path = config["image_model_path"]
    projector_path = config["image_projector_path"]
    model = _load_image_model(model_path, projector_path)
    try:
        result = model.create_chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_tokens=256,
            temperature=0.1,
            stream=False,
        )
    except ValueError as error:
        raise RuntimeError(
            "The local text model and image projector are incompatible. "
            "Use a matching GGUF LLaVA model and mmproj file."
        ) from error
    if not isinstance(result, dict):
        raise RuntimeError("The image model returned an unexpected response.")
    response = result["choices"][0]["message"].get("content")
    if not isinstance(response, str) or not response.strip():
        raise RuntimeError("The image model returned an empty response.")
    return response.strip()
