const form = document.getElementById('tts-form');
const resultDiv = document.getElementById('result');
const progressBar = document.getElementById('progress-bar');
const textarea = document.getElementById('text');
const wordCountDiv = document.getElementById('word-count');
const fileInput = document.getElementById('file');

const countWords = text => text.trim().split(/\s+/).filter(w => w.length).length;

textarea.addEventListener('input', () => {
  wordCountDiv.textContent = `Слов: ${countWords(textarea.value)}`;
});
wordCountDiv.textContent = `Слов: ${countWords(textarea.value)}`;

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (file && file.name.endsWith('.txt')) {
    const reader = new FileReader();
    reader.onload = () => {
      textarea.value = reader.result;
      wordCountDiv.textContent = `Слов: ${countWords(textarea.value)}`;
    };
    reader.readAsText(file, 'UTF-8');
  } else {
    alert("Пожалуйста, загрузите текстовый файл (.txt)");
    fileInput.value = "";
  }
});

form.addEventListener('submit', async e => {
  e.preventDefault();
  resultDiv.innerHTML = "";
  progressBar.style.width = '0%';

  const formData = new FormData(form);

  try {
    const response = await fetch('/upload/', { method: 'POST', body: formData });
    if (!response.ok) throw new Error('Ошибка запроса');
    
    const data = await response.json();
    if (data.error) throw new Error(data.error);

    const fileId = data.file_id;

    const pollProgress = async () => {
      try {
        const res = await fetch(`/progress/${fileId}`);
        const progData = await res.json();
        const progress = progData.progress;
        progressBar.style.width = `${progress}%`;

        if (progress < 100) {
          setTimeout(pollProgress, 1000);
        } else {
          // после завершения отображаем аудио
          resultDiv.innerHTML = `
            <audio controls src="${data.download_url}"></audio><br>
            <a href="${data.download_url}" download="speech.wav">
              <button>Скачать аудиофайл</button>
            </a>
          `;
        }
      } catch (err) {
        console.error("Ошибка получения прогресса:", err);
      }
    };

    pollProgress();
  } catch (err) {
    progressBar.style.width = '0%';
    resultDiv.textContent = `Ошибка: ${err.message}`;
  }
});
