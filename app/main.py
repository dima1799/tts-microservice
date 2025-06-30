from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
import os
import json
from pathlib import Path

from .tts_engine import synthesize_text  # функция синтеза

app = FastAPI()

# Статические файлы (аудио, css, js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Шаблоны
templates = Jinja2Templates(directory="app/templates")

# Путь, куда сохраняются аудиофайлы
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Обработка текста и генерация речи
@app.post("/upload/")
async def upload_text(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
):
    file_id = str(uuid4())
    audio_path = os.path.join(AUDIO_DIR, f"{file_id}.wav")

    # Создаем файл прогресса с нулевым значением до запуска фоновой задачи
    progress_path = Path(f"app/progress_{file_id}.json")
    with progress_path.open("w", encoding="utf-8") as f:
        json.dump({"progress": 0}, f)

    background_tasks.add_task(synthesize_text, text, audio_path, file_id=file_id)

    return {
        "message": "Озвучка создана",
        "file_id": file_id,
        "download_url": f"/audio/{file_id}"
    }

# Отдача аудиофайла
@app.get("/audio/{file_id}")
async def get_audio(file_id: str):
    audio_path = os.path.join(AUDIO_DIR, f"{file_id}.wav")
    if not os.path.exists(audio_path):
        return {"error": "Файл не найден"}
    return FileResponse(audio_path, media_type="audio/wav")

# Эндпоинт для получения текущего прогресса
@app.get("/progress/{file_id}")
async def get_progress(file_id: str):
    progress_path = Path(f"app/progress_{file_id}.json")
    if progress_path.exists():
        with open(progress_path, "r", encoding="utf-8") as f:
            return JSONResponse(content=json.load(f))
    return JSONResponse(content={"progress": 0})
