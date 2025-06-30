from TTS.api import TTS
import torch
import os
import json
import re
import numpy as np
from pathlib import Path
import soundfile as sf

BASE_DIR = Path(__file__).resolve().parent.parent
REFERENCE_AUDIO = BASE_DIR / "static" / "speakers" / "speaker_Andrew.wav"

device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)

if device == "cuda":
    tts = tts.to(device, dtype=torch.float16)
else:
    tts = tts.to(device)


MAX_FRAGMENT_CHARS = 300

def split_text(text, max_chars: int = MAX_FRAGMENT_CHARS):
    """Split text into fragments not exceeding ``max_chars`` characters.

    The text is first split into sentences and then concatenated back
    together until the length limit is reached. This reduces the number
    of calls to the TTS engine which speeds up synthesis.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    fragments = []
    current = ""
    for sent in sentences:
        if not sent:
            continue

        # +1 accounts for the space that will be added
        additional = len(sent) + (1 if current else 0)

        if len(current) + additional <= max_chars:
            current = f"{current} {sent}".strip()
        else:
            if current:
                fragments.append(current)
            # If a single sentence is longer than max_chars, break it up
            if len(sent) > max_chars:
                start = 0
                while start < len(sent):
                    end = start + max_chars
                    fragments.append(sent[start:end])
                    start = end
                current = ""
            else:
                current = sent

    if current:
        fragments.append(current)

    return fragments

def synthesize_text(text, output_path, file_id=None):
    if not os.path.exists(REFERENCE_AUDIO):
        raise FileNotFoundError(f"Файл спикера не найден: {REFERENCE_AUDIO}")

    fragments = split_text(text)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Прогресс сохраняется в файл с file_id
    progress_dir = Path(__file__).resolve().parent
    progress_path = progress_dir / (f"progress_{file_id}.json" if file_id else "progress.json")
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump({"progress": 0}, f)

    full_audio = []
    for i, fragment in enumerate(fragments):
        audio = tts.tts(
            text=fragment,
            speaker_wav=str(REFERENCE_AUDIO),
            language="ru",
            split_sentences=False,
            file_path=None,
        )
        full_audio.extend(audio)

        # Прогресс чуть меньше 100%, пока файл ещё не сохранён
        progress = int((i + 1) / len(fragments) * 100)
        if progress >= 100:
            progress = 99
        with open(progress_path, "w", encoding="utf-8") as f:
            json.dump({"progress": progress}, f)

    sf.write(output_path, np.array(full_audio), 24000)

    # Теперь файл готов — обновляем прогресс до 100%
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump({"progress": 100}, f)
