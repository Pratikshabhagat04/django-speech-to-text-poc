import os
from functools import lru_cache
from faster_whisper import WhisperModel

@lru_cache(maxsize=1)
def get_model():
    model_size = os.getenv("WHISPER_MODEL", "base")
    device = os.getenv("WHISPER_DEVICE", "cpu")
    compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    return WhisperModel(model_size, device=device, compute_type=compute_type)

def transcribe_audio(audio_path):
    model = get_model()
    segments, info = model.transcribe(
        audio_path,
        beam_size=3,
        vad_filter=True,
        task="transcribe",
    )
    text = " ".join(segment.text.strip() for segment in segments).strip()
    language = info.language or "unknown"
    return text, language
