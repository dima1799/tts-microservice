# TTS Microservice

Данный проект представляет собой микросервис для синтеза речи из текста. В основе используется библиотека [Coqui TTS](https://github.com/coqui-ai/TTS) и модель `xtts_v2`. Сервис предоставляет веб-интерфейс и REST API для загрузки текста и получения аудиофайлов.

## Требования

- Python 3.10 или новее
- Установленные зависимости из `requirements.txt`
- WAV файл с образцом голоса `static/speakers/speaker_example.wav`

## Установка

```bash
git clone <repo-url>
cd tts-microservice
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Поместите файл с образцом голоса по пути `static/speakers/speaker_example.wav`. Он необходим для работы модели XTTS.

## Запуск

```bash
uvicorn app.main:app --reload
```

После запуска интерфейс будет доступен по адресу `http://localhost:8000`.

## Использование

1. Откройте главную страницу сервиса в браузере.
2. Введите текст или загрузите `.txt` файл.
3. Наблюдайте за прогрессом обработки и скачайте готовый WAV файл.

## Структура проекта

```
app/            # код FastAPI и движок TTS
static/         # статические файлы: JS, CSS, аудио
requirements.txt
```

