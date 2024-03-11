//const userIP = document.currentScript.getAttribute('data-user-ip');
//const userPort = document.currentScript.getAttribute('data-user-port');
//const webSocketURL = `ws://${userIP}:${userPort}/ws`;

const getElement = id => document.getElementById(id);
const messages = document.getElementById('messages')
const message = document.createElement('li')
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


        const data = JSON.parse(event.data);

        const DisplacementsScriptElement = document.createElement('script');
        DisplacementsScriptElement.innerHTML = data.displacements.scripts;
        document.body.appendChild(DisplacementsScriptElement);

        // Разбираем строку divAttributes и извлекаем атрибуты
        const DisplacementsDivAttributes = data.displacements.divs
        const DisplacementsIdMatch = DisplacementsDivAttributes.match(/id="([^"]+)"/);
        const DisplacementsDataRootIdMatch = DisplacementsDivAttributes.match(/data-root-id="([^"]+)"/);
        const DisplacementsStyleMatch = DisplacementsDivAttributes.match(/style="([^"]+)"/);

        const DisplacementsDivElement = document.createElement('div');

        // Устанавливаем атрибуты извлеченных данных
        if (DisplacementsIdMatch) {DisplacementsDivElement.setAttribute('id', DisplacementsIdMatch[1]);}
        if (DisplacementsDataRootIdMatch) {DisplacementsDivElement.setAttribute('data-root-id', DisplacementsDataRootIdMatch[1]);}
        if (DisplacementsStyleMatch) {DisplacementsDivElement.setAttribute('style', DisplacementsStyleMatch[1]);}

        message.appendChild(DisplacementsDivElement);

        const StressScriptElement = document.createElement('script');
        StressScriptElement.innerHTML = data.stress.scripts;
        document.body.appendChild(StressScriptElement);

        // Разбираем строку divAttributes и извлекаем атрибуты
        const StressDivAttributes = data.stress.divs
        const StressIdMatch = StressDivAttributes.match(/id="([^"]+)"/);
        const StressDataRootIdMatch = StressDivAttributes.match(/data-root-id="([^"]+)"/);
        const StressStyleMatch = StressDivAttributes.match(/style="([^"]+)"/);

        const StressDivElement = document.createElement('div');

        // Устанавливаем атрибуты извлеченных данных
        if (StressIdMatch) {StressDivElement.setAttribute('id', StressIdMatch[1]);}
        if (StressDataRootIdMatch) {StressDivElement.setAttribute('data-root-id', StressDataRootIdMatch[1]);}
        if (StressStyleMatch) {StressDivElement.setAttribute('style', StressStyleMatch[1]);}

        message.appendChild(StressDivElement);

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
