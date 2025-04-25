document.addEventListener('DOMContentLoaded', function() {
    // Подключаемся к WebSocket серверу
    const socket = io();
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendMessage');
    const chatList = document.getElementById('chatList');
    
    // Обработчик отправки сообщения
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message && window.currentChatId) {
            const data = {
                chat_id: window.currentChatId,
                sender: window.currentUser,
                message: message
            };
            
            console.log('Sending message:', data); // Добавим лог для отладки
            
            socket.emit('send_message', data);
            messageInput.value = '';
            
            // Добавляем сообщение в чат сразу (оптимистичное обновление)
            addMessageToChat(data, true);
        }
    }
    
    // Добавление сообщения в чат
    function addMessageToChat(data, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user' : 'other');
        messageDiv.textContent = data.message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Обновляем превью в списке чатов
        updateChatPreview(data.chat_id, data.message);
    }
    
    // Обновление превью чата
    function updateChatPreview(chatId, message) {
        const chatItems = document.querySelectorAll('.chat-item');
        chatItems.forEach(item => {
            if (item.dataset.chatId === chatId.toString()) {
                const preview = item.querySelector('.chat-preview');
                if (preview) {
                    preview.textContent = message.length > 30 
                        ? message.substring(0, 30) + '...' 
                        : message;
                }
            }
        });
    }
    
    // Обработчики событий
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Обработчик клика по чату в списке
    chatList.addEventListener('click', function(e) {
        const chatItem = e.target.closest('.chat-item');
        if (chatItem) {
            // Удаляем активный класс у всех чатов
            document.querySelectorAll('.chat-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Добавляем активный класс выбранному чату
            chatItem.classList.add('active');
            
            // Обновляем текущий chat_id
            window.currentChatId = parseInt(chatItem.dataset.chatId);
            
            // Загружаем сообщения для этого чата
            fetch(`/chat/${window.currentChatId}`)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newMessages = doc.getElementById('chatMessages');
                    chatMessages.innerHTML = newMessages.innerHTML;
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                });
            
            // Обновляем заголовок чата
            document.querySelector('.chat-header h2').textContent = 
                chatItem.querySelector('.chat-name').textContent;
        }
    });
    
    // Обработчики WebSocket событий
    socket.on('connect', () => {
        console.log('Connected to WebSocket server');
        
        // При подключении подписываемся на чат
        if (window.currentChatId) {
            socket.emit('join_chat', { chat_id: window.currentChatId });
        }
    });
    
    socket.on('new_message', (data) => {
        console.log('Received new message:', data); // Лог для отладки
        // Проверяем, что сообщение для текущего чата
        if (data.chat_id == window.currentChatId) {
            addMessageToChat(data, data.sender === window.currentUser);
        }
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from WebSocket server');
    });
    
    // Добавим обработчик ошибок
    socket.on('connect_error', (error) => {
        console.error('Socket connection error:', error);
    });
});