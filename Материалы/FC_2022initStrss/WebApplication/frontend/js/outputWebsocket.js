//const userIP = document.currentScript.getAttribute('data-user-ip');
//const userPort = document.currentScript.getAttribute('data-user-port');
//const webSocketURL = `ws://${userIP}:${userPort}/ws`;

const getElement = id => document.getElementById(id);
const notificationContainer = getElement('error-container');
const notificationMsg = getElement('notification-msg');

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
    try {
        var messages = document.getElementById('messages')
        var message = document.createElement('li')

        const data = JSON.parse(event.data);
        const divAttributes = data.div;

        const scriptElement = document.createElement('script');
        scriptElement.innerHTML = data.script;
        document.body.appendChild(scriptElement);

        // Разбираем строку divAttributes и извлекаем атрибуты
        const idMatch = divAttributes.match(/id="([^"]+)"/);
        const dataRootIdMatch = divAttributes.match(/data-root-id="([^"]+)"/);
        const styleMatch = divAttributes.match(/style="([^"]+)"/);

        const divElement = document.createElement('div');

        // Устанавливаем атрибуты извлеченных данных
        if (idMatch) {divElement.setAttribute('id', idMatch[1]);}
        if (dataRootIdMatch) {divElement.setAttribute('data-root-id', dataRootIdMatch[1]);}
        if (styleMatch) {divElement.setAttribute('style', styleMatch[1]);}

        message.appendChild(divElement);
        messages.appendChild(message);

    } catch (error) {
        handleError(error);
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
