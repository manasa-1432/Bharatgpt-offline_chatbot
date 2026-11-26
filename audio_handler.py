import torch
from transformers.pipelines import pipeline
import librosa
import io
from functools import lru_cache
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent
with (PROJECT_ROOT / "config.yaml").open("r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

def convert_bytes_to_array(audio_bytes):
    if not audio_bytes:
        raise ValueError("The audio recording is empty.")
    audio_bytes = io.BytesIO(audio_bytes)
    audio, _ = librosa.load(audio_bytes, sr=16000)
    return audio

@lru_cache(maxsize=1)
def _load_asr_pipeline(
    model_path: str,
    device: str,
):
    return pipeline(
        task="automatic-speech-recognition",
        model=model_path,
        chunk_length_s=30,
        device=device,
        model_kwargs={"local_files_only": True},
        return_timestamps=False,
    )


def transcribe_audio(audio_bytes):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    model_path = Path(config["whisper_model_path"])
    if not model_path.is_absolute():
        model_path = PROJECT_ROOT / model_path
    if not model_path.is_dir():
        raise FileNotFoundError(
            f"Whisper model not found: {model_path}. Place the complete local "
            "Whisper model in this folder."
        )

    audio_array = convert_bytes_to_array(audio_bytes)
    pipe = _load_asr_pipeline(str(model_path), device)
    result = pipe(audio_array, batch_size=1)
    if not isinstance(result, dict):
        raise RuntimeError("Whisper returned an unexpected transcription result.")
    prediction = result.get("text")
    if not isinstance(prediction, str) or not prediction.strip():
        raise ValueError("No speech was detected in the audio.")
    return prediction.strip()
