from TTS.api import TTS
import torch
import os
import json
import re
import numpy as np
from pathlib import Path
import soundfile as sf

REFERENCE_AUDIO = "C:/Users/dima-/ML/tts_microservice/static/speakers/speaker_Andrew.wav"

device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)

def split_text(text):
    return re.split(r'(?<=[.!?])\s+', text.strip())

def synthesize_text(text, output_path, file_id=None):
    if not os.path.exists(REFERENCE_AUDIO):
        raise FileNotFoundError(f"Файл спикера не найден: {REFERENCE_AUDIO}")

    fragments = split_text(text)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Прогресс сохраняется в файл с file_id
    progress_path = Path(f"app/progress_{file_id}.json") if file_id else Path("app/progress.json")
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump({"progress": 0}, f)

    full_audio = []
    for i, fragment in enumerate(fragments):
        audio = tts.tts(
            text=fragment,
            speaker_wav=REFERENCE_AUDIO,
            language="ru",
            split_sentences=False,
            file_path=None,
        )
        full_audio.extend(audio)
        # Обновление прогресса
        with open(progress_path, "w", encoding="utf-8") as f:
            json.dump({"progress": int((i + 1) / len(fragments) * 100)}, f)

    sf.write(output_path, np.array(full_audio), 24000)
