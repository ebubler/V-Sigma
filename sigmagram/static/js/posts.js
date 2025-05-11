// Функции для показа/скрытия формы добавления поста
function showAddPost() {
    document.querySelector('.add-post').style.display = 'block';
}

function hideAddPost() {
    document.querySelector('.add-post').style.display = 'none';
}

// Обработчик загрузки медиафайлов
document.getElementById('media-upload').addEventListener('change', function (event) {
    const files = event.target.files;
    const carouselInner = document.getElementById('carouselInner');

    // Если карусель пустая, удаляем placeholder "Нет медиа"
    if (carouselInner.children.length === 1 && carouselInner.querySelector('.carousel-item p')) {
        carouselInner.innerHTML = '';
    }

    Array.from(files).forEach((file) => {
        // Проверка типа файла
        if (!file.type.match('image.*') && !file.type.match('video.*')) {
            alert('Пожалуйста, загружайте только изображения или видео!');
            return;
        }

        // Проверка размера файла (например, не более 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('Файл слишком большой! Максимальный размер - 10MB.');
            return;
        }

        const reader = new FileReader();

        reader.onload = function (e) {
            const mediaSrc = e.target.result;

            const carouselItem = document.createElement('div');
            carouselItem.classList.add('carousel-item');

            let mediaElement;
            if (file.type.startsWith('image')) {
                mediaElement = document.createElement('img');
                mediaElement.src = mediaSrc;
                mediaElement.alt = `Image ${carouselInner.children.length + 1}`;
                mediaElement.classList.add('media-preview');
            } else if (file.type.startsWith('video')) {
                mediaElement = document.createElement('video');
                mediaElement.src = mediaSrc;
                mediaElement.controls = true;
                mediaElement.muted = true;
                mediaElement.classList.add('media-preview');
            }

            const removeBtn = document.createElement('button');
            removeBtn.classList.add('remove-btn');
            removeBtn.innerHTML = '&times;';
            removeBtn.onclick = function () {
                carouselItem.remove();
                if (carouselInner.children.length === 0) {
                    carouselInner.innerHTML = '<div class="carousel-item active"><p>Нет медиа</p></div>';
                } else {
                    carouselInner.children[0].classList.add('active');
                }
            };

            carouselItem.appendChild(mediaElement);
            carouselItem.appendChild(removeBtn);
            carouselInner.appendChild(carouselItem);

            // Активируем первый элемент, если это первый медиафайл
            if (carouselInner.children.length === 1) {
                carouselItem.classList.add('active');
            }
        };

        reader.readAsDataURL(file);
    });
});

// Обработчик отправки формы
document.querySelector('.add-post-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    // Показываем индикатор загрузки
    const submitBtn = this.querySelector('input[type="submit"]');
    const originalBtnText = submitBtn.value;
    submitBtn.value = 'Отправка...';
    submitBtn.disabled = true;

    try {
        const formData = new FormData(this);
        const carouselItems = document.querySelectorAll('#carouselInner .carousel-item:not(:has(p))');

        // Добавляем медиафайлы из карусели в FormData
        carouselItems.forEach((item, index) => {
            const mediaElement = item.querySelector('img, video');
            if (mediaElement) {
                const blob = dataURItoBlob(mediaElement.src);
                const fileType = mediaElement.tagName.toLowerCase() === 'img' ? 'jpg' : 'mp4';
                formData.append(`media-${index}`, blob, `media-${index}.${fileType}`);
            }
        });

        // Добавляем информацию о количестве медиафайлов
        formData.append('media-count', carouselItems.length);

        // Отправляем данные на сервер
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            // Успешная отправка - скрываем форму и обновляем страницу
            hideAddPost();
            window.location.reload();
        } else {
            const errorData = await response.json();
            alert(`Ошибка: ${errorData.message || 'Неизвестная ошибка'}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке поста');
    } finally {
        // Восстанавливаем кнопку
        submitBtn.value = originalBtnText;
        submitBtn.disabled = false;
    }
});

// Вспомогательная функция для преобразования DataURL в Blob
function dataURItoBlob(dataURI) {
    // Разбираем DataURL
    const split = dataURI.split(',');
    const byteString = atob(split[1]);
    const mimeString = split[0].split(':')[1].split(';')[0];

    // Создаем ArrayBuffer и представление для него
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);

    // Заполняем ArrayBuffer
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    // Создаем и возвращаем Blob
    return new Blob([ab], { type: mimeString });
}

// Инициализация карусели при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем обработчик для стандартных файлов (если нужно)
    const fileInput = document.querySelector('input[type="file"]:not(#media-upload)');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            // Можно добавить предпросмотр для обычных файлов, если нужно
            console.log('Обычные файлы выбраны:', this.files);
        });
    }
});