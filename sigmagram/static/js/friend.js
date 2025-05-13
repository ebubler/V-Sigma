function friendShowList(listNumber) {
            // Скрываем все списки
            document.getElementById('friend-list1').style.display = 'none';
            document.getElementById('friend-list2').style.display = 'none';
            document.getElementById('friend-list3').style.display = 'none';

            // Показываем выбранный список
            document.getElementById('friend-list' + listNumber).style.display = 'block';

            // Удаляем класс friend-active со всех кнопок
            const buttons = document.querySelectorAll('.friend-button');
            buttons.forEach(button => {
                button.classList.remove('friend-active');
            });

            // Добавляем класс friend-active к нажатой кнопке
            event.target.classList.add('friend-active');
        }