// Получаем элементы из DOM
const toggleButton = document.getElementById('toggleButton');
const sideBlock = document.getElementById('sideBlock');
const closeButton = document.getElementById('closeButton');

function showSideBlock() {
    sideBlock.classList.add('active');
}

function hideSideBlock() {
    sideBlock.classList.remove('active');
}

toggleButton.addEventListener('click', showSideBlock);

closeButton.addEventListener('click', hideSideBlock);

document.addEventListener('click', (event) => {
    if (
        !sideBlock.contains(event.target) &&
        event.target !== toggleButton
    ) {
        hideSideBlock();
    }
});



document.addEventListener('DOMContentLoaded', function () {
    const bannerPreview = document.getElementById('bannerPreview');
    const bannerInput = document.getElementById('bannerInput');

    const avatarPreview = document.getElementById('avatarPreview');
    const avatarInput = document.getElementById('avatarInput');

    bannerPreview.addEventListener('click', function () {
        bannerInput.click();
    });

    avatarPreview.addEventListener('click', function () {
        avatarInput.click();
    });

    bannerInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                bannerPreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    avatarInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                avatarPreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});