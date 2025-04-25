const imageInput = document.getElementById('imageInput');
const previewDiv = document.getElementById('preview');
const imageInput2 = document.getElementById('imageInput2');
const previewDiv2 = document.getElementById('preview2');

imageInput.addEventListener('change', function(event) {
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            previewDiv.innerHTML = '';
            previewDiv.appendChild(img);
        };

        reader.readAsDataURL(file);
    } else {
        previewDiv.innerHTML = '';
    }
});

imageInput2.addEventListener('change', function(event) {
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            previewDiv2.innerHTML = '';
            previewDiv2.appendChild(img);
        };

        reader.readAsDataURL(file);
    } else {
        previewDiv2.innerHTML = '';
    }
});