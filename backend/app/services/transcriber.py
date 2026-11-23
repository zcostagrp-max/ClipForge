import os
from faster_whisper import WhisperModel
from dotenv import load_dotenv

load_dotenv()

MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = "int8" if DEVICE == "cpu" else "float16"

_model = None

def get_model():
    global _model
    if _model is None:
        _model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    return _model

def transcribe_audio(audio_path: str) -> list:
    """Return list of segments with word-level timestamps."""
    model = get_model()
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True,
        language="en"
    )
    
    result = []
    for segment in segments:
        words = []
        if hasattr(segment, 'words') and segment.words:
            for word in segment.words:
                words.append({
                    "word": word.word.strip(),
                    "start": word.start,
                    "end": word.end
                })
        result.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
            "words": words
        })
    return result
