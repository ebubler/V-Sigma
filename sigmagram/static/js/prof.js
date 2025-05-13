// Функция для получения значения куки
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.split('=');
        if (cookieName.trim() === name) {
            return cookieValue;
        }
    }
    return null;
}

// Обработчик удаления поста
document.addEventListener('click', async function(e) {
    if (e.target.closest('.delete-post-btn')) {
        const btn = e.target.closest('.delete-post-btn');
        const postId = btn.dataset.postId;

        // Подтверждение удаления
        const isConfirmed = confirm('Вы уверены, что хотите удалить этот пост?');

        if (isConfirmed) {
            try {
                const response = await fetch(`/post/delete/${postId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    // Удаляем пост из DOM
                    btn.closest('.post-item').remove();
                } else {
                    const error = await response.json();
                    alert(error.error || 'Ошибка при удалении поста');
                }
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при удалении поста');
            }
        }
    }
});

// Функции для показа/скрытия формы добавления поста
function showAddPost() {
    document.querySelector('.add-post').style.display = 'block';
}

function hideAddPost() {
    document.querySelector('.add-post').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
        let currentStart = 0;
        const postsPerLoad = 5;
        const postsContainer = document.getElementById('posts-container');
        const loadMoreBtn = document.getElementById('load-more-btn');

        function formatFileName(filename, maxLength = 40) {
            if (filename.length <= maxLength) return filename;

            const extensionIndex = filename.lastIndexOf('.');
            if (extensionIndex === -1) {
                // Если нет расширения
                return filename.substring(0, maxLength - 3) + '...';
            }

            const extension = filename.substring(extensionIndex);
            const name = filename.substring(0, extensionIndex);

            if (maxLength < 10) {
                // Если очень маленький лимит, просто обрезаем
                return filename.substring(0, maxLength - 3) + '...';
            }

            const partLength = Math.floor((maxLength - extension.length - 3) / 2);
            return name.substring(0, partLength) + '.......' + name.slice(-partLength) + extension;
        }

        function createFilesList(fileString) {
            if (!fileString) return '';

            const files = fileString.split(',');
            let filesHTML = '<ul class="file-list">';

            files.forEach(file => {
                if (file.trim()) {
                    const fileExt = file.split('.').pop().toLowerCase();
                    const iconClass = getFileIconClass(fileExt);
                    const displayName = formatFileName(file.trim(), 80); // 25 символов максимум

                    filesHTML += `
                        <li class="file-item">
                            <img href="/static/uploads/files/${file}" class="file-icon" src="/static/img/download_35dp_FFFFFF_FILL0_wght400_GRAD0_opsz40.svg"></img>
                            <a href="/static/uploads/files/${file}" download title="${file}">${displayName}</a>
                        </li>
                    `;
                }
            });

            filesHTML += '</ul>';
            return filesHTML;
        }

        function getFileIconClass(ext) {
            const iconMap = {
                'pdf': 'fa-file-pdf',
                'doc': 'fa-file-word',
                'docx': 'fa-file-word',
                'xls': 'fa-file-excel',
                'xlsx': 'fa-file-excel',
                'ppt': 'fa-file-powerpoint',
                'pptx': 'fa-file-powerpoint',
                'txt': 'fa-file-alt',
                'zip': 'fa-file-archive',
                'rar': 'fa-file-archive',
                'jpg': 'fa-file-image',
                'jpeg': 'fa-file-image',
                'png': 'fa-file-image',
                'gif': 'fa-file-image',
                'mp4': 'fa-file-video',
                'mov': 'fa-file-video'
            };

            return iconMap[ext] || 'fa-file';
        }

        // Функция загрузки постов
        async function loadPosts() {
            try {
                loadMoreBtn.disabled = true;
                loadMoreBtn.textContent = 'Загрузка...';

                const url = new URL(window.location.href);
                const login = url.pathname.split('/').pop();

                const response = await fetch(`/posts/range/user/${login}?start=${currentStart}&end=${currentStart + postsPerLoad - 1}`);

                if (!response.ok) {
                    throw new Error('Ошибка загрузки постов');
                }

                const posts = await response.json();

                if (posts.length === 0) {
                    loadMoreBtn.style.display = 'none';
                    return;
                }

                posts.forEach(post => {
                    const postElement = createPostElement(post);
                    postsContainer.appendChild(postElement);
                });

                currentStart += postsPerLoad;

                // Скрываем кнопку, если загружено меньше постов, чем ожидалось
                if (posts.length < postsPerLoad) {
                    loadMoreBtn.style.display = 'none';
                }
            } catch (error) {
                console.error('Ошибка:', error);
                loadMoreBtn.style.display = 'none';
            } finally {
                loadMoreBtn.disabled = false;
                loadMoreBtn.textContent = 'Показать еще';
            }
        }

        // Функция создания HTML для поста
        function createPostElement(post) {
            const postDiv = document.createElement('div');
            postDiv.className = 'post-item';

            const currentUserLogin = getCookie('login');
            console.log(currentUserLogin);

            // Форматируем дату
            const postDate = new Date(post.date_create);
            const formattedDate = postDate.toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit'
            }) + ' ' + postDate.toLocaleDateString('ru-RU');

            postDiv.innerHTML = `
                <div class="author-header">
                    <img class="author-image" src="/static/${post.photo_avatar ? 'user_img/' + post.photo_avatar : 'img/avatar 1.png'}" alt="Аватар">
                    <a href="/prof/${post.author}" class="author-post" style="color: inherit;">${post.author_surname} ${post.author_name}</a>
                    ${post.author === currentUserLogin ? `
                        <button class="delete-post-btn" data-post-id="${post.id}" title="Удалить пост">
                            <i class="fas fa-trash"></i>
                        </button>
                        ` : ''}
                </div>
                <h3 class="post-title">${post.title}</h3>
                <div class="post-text">${post.description}</div>
                ${post.content ? `
                <div class="post-media">
                    ${createMediaCarousel(post.content, post.id)}
                </div>
                ` : ''}
                ${post.file ? `
                <div class="post-files">
                    <h4>Прикрепленные файлы:</h4>
                    ${createFilesList(post.file)}
                </div>
                ` : ''}
                <div class="post-date">${formattedDate}</div>

                <div class="post-actions">
                <button class="like-btn" data-post-id="${post.id}" style="color: ${post.liked ? 'red' : 'white'};">
                    <i class="${post.liked ? 'fas' : 'far'} fa-heart"></i>
                    <span class="like-count">${post.likes}</span>
                </button>
                <button class="comment-btn" data-post-id="${post.id}">
                    <i class="far fa-comment"></i>
                    <span class="comment-count" id="comment-count-${post.id}">${post.len_comments}</span>
                </button>
            </div>
            <div class="comments-section" id="comments-${post.id}" style="display: none;">
                <div class="comments-list"></div>
                <form class="add-comment-form">
                    <input type="text" placeholder="Добавить комментарий..." required>
                    <button type="submit">Отправить</button>
                </form>
            </div>
            `;
            return postDiv;
        }

        // Функция создания карусели медиа
        function createMediaCarousel(content, postId) {
            const mediaItems = content.split(',');
            let carouselHTML = `
                <div id="postCarousel-${postId}" class="carousel slide" data-bs-ride="carousel">
                    <div class="carousel-inner">
            `;

            mediaItems.forEach((media, index) => {
                const isImage = media.toLowerCase().match(/\.(jpg|jpeg|png|gif)$/);
                const isVideo = media.toLowerCase().match(/\.(mp4|webm)$/);

                carouselHTML += `
                    <div class="carousel-item ${index === 0 ? 'active' : ''}">
                        ${isImage ?
                            `<img src="/static/uploads/media/${media}" class="d-block w-100" alt="Media">` : ''}
                        ${isVideo ?
                            `<video controls class="d-block w-100">
                                <source src="/static/uploads/media/${media}" type="video/mp4">
                            </video>` : ''}
                    </div>
                `;
            });

            carouselHTML += `</div>`;

            if (mediaItems.length > 1) {
                carouselHTML += `
                    <button class="carousel-control-prev" type="button" data-bs-target="#postCarousel-${postId}" data-bs-slide="prev">
                        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                        <span class="visually-hidden">Previous</span>
                    </button>
                    <button class="carousel-control-next" type="button" data-bs-target="#postCarousel-${postId}" data-bs-slide="next">
                        <span class="carousel-control-next-icon" aria-hidden="true"></span>
                        <span class="visually-hidden">Next</span>
                    </button>
                `;
            }

            carouselHTML += `</div>`;
            return carouselHTML;
        }

        // Обработчик кнопки "Показать еще"
        loadMoreBtn.addEventListener('click', loadPosts);

        // Первоначальная загрузка постов
        loadPosts();
    });

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
        if (file.size > 10 * 1024 * 1024 * 1024 * 1024) {
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

// Обработчик лайков
document.addEventListener('click', async function(e) {
    if (e.target.closest('.like-btn')) {
        const btn = e.target.closest('.like-btn');
        const postId = btn.dataset.postId;
        const likeCount = btn.querySelector('.like-count');

        try {
            const response = await fetch(`/posts/${postId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                likeCount.textContent = result.likes;
                btn.querySelector('i').classList.toggle('far');
                btn.querySelector('i').classList.toggle('fas');

                if (result.liked) {
                    btn.style.color = 'red';
                } else {
                    btn.style.color = 'white';
                }
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }

    // Обработчик кнопки комментариев
    if (e.target.closest('.comment-btn')) {
        const btn = e.target.closest('.comment-btn');
        const postId = btn.dataset.postId;
        const commentsSection = document.getElementById(`comments-${postId}`);

        if (commentsSection.style.display === 'none') {
            commentsSection.style.display = 'block';
            loadComments(postId);
        } else {
            commentsSection.style.display = 'none';
        }
    }

    // Отправка комментария
    if (e.target.closest('.add-comment-form')) {
        e.preventDefault();
        const form = e.target.closest('.add-comment-form');
        const postId = form.closest('.comments-section').id.split('-')[1];
        const input = form.querySelector('input');
        const commentText = input.value.trim();

        if (commentText) {
            await addComment(postId, commentText);
            input.value = '';
        }
    }
});

// Функция загрузки комментариев
async function loadComments(postId) {
    try {
        const response = await fetch(`/posts/${postId}/comments`);
        if (response.ok) {

            const comments = await response.json();
            const container = document.querySelector(`#comments-${postId} .comments-list`);
            container.innerHTML = comments.map(comment => `
                <div class="comment">
                    <img src="/static/${comment.photo_avatar ? 'user_img/' + comment.photo_avatar : 'img/avatar 1.png'}" alt="${comment.author_name} ${comment.author_surname}" class="author-image-comment">
                    <strong>${comment.author_surname} ${comment.author_name}:</strong>
                    <p>${comment.message}</p>
                    <small>${new Date(comment.date).toLocaleString()}</small>
                </div>
            `).join('');

        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Функция добавления комментария
async function addComment(postId, text) {
    try {
        const response = await fetch(`/posts/${postId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Ошибка при добавлении комментария');
        }

        await loadComments(postId);
        const commentsSection = document.getElementById(`comments-${postId}`);
        commentsSection.scrollTop = commentsSection.scrollHeight;

    } catch (error) {
        console.error('Ошибка:', error);
        alert(error.message);
    }
}