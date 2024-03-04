//const userIP = document.currentScript.getAttribute('data-user-ip');
//const userPort = document.currentScript.getAttribute('data-user-port');
//const webSocketURL = `ws://${userIP}:${userPort}/ws`;

const webSocketURL = 'ws://localhost:8000/ws'

var ws = new WebSocket(webSocketURL);

ws.onopen = async function(event) {
    try{
         // Соединение установлено
        const urlParams = new URLSearchParams(window.location.search);
        const fileName = urlParams.get('fileName');
        ws.send(fileName);
        event.preventDefault();
    }
    catch(error){
        handleError(error)
    }

};

ws.onerror = async function(event) {
    // Ошибка при установке соединения
    console.error("WebSocket connection error:", event);
    handleError(event)
};

// Обработчик события получения сообщения от сервера
ws.onmessage = async function(event) {
    try{
        const messages = document.getElementById('messages');
        const content = event.data;

        if (content === 'clear') {
            messages.innerHTML = '';
        } else {
            const message = document.createElement('li');
            message.textContent = content;
            messages.appendChild(message);
            window.scrollTo(0, document.body.scrollHeight);
        }
    }
    catch(error){
        handleError(error)
    }

};

ws.onclose =async function(event) {
    // Соединение закрыто
    console.log("WebSocket connection closed.");
};

async function handleError(error) {
    console.error('Error:', error);
    notificationMsg.textContent += error;
    notificationContainer.style.display = 'block';
}
