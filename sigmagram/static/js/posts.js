function showAddPost() {
    document.querySelector('.add-post').style.display = 'block';
}

function hideAddPost() {
    document.querySelector('.add-post').style.display = 'none';
}

document.getElementById('media-upload').addEventListener('change', function (event) {
    const files = event.target.files;
    const carouselInner = document.getElementById('carouselInner');

    // Если карусель пустая, удаляем placeholder "Нет медиа"
    if (carouselInner.children.length === 1 && carouselInner.querySelector('.carousel-item p')) {
        carouselInner.innerHTML = '';
    }

    Array.from(files).forEach((file) => {
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
            } else if (file.type.startsWith('video')) {
                mediaElement = document.createElement('video');
                mediaElement.src = mediaSrc;
                mediaElement.controls = true;
                mediaElement.muted = true;
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