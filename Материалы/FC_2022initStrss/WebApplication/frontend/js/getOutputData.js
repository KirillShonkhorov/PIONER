const userIP = document.currentScript.getAttribute('data-user-ip');
const userPort = document.currentScript.getAttribute('data-user-port');
const webSocketURL = `ws://${userIP}:${userPort}/ws`;

var ws = new WebSocket(webSocketURL);

ws.onopen = function(event) {
    // Соединение установлено
    console.log("WebSocket connection established.");
};

ws.onerror = function(event) {
    // Ошибка при установке соединения
    console.error("WebSocket connection error:", event);
    // Ваш код для отображения сообщения об ошибке пользователю
};

// Обработчик события получения сообщения от сервера
ws.onmessage = function(event) {
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
};

ws.onclose = function(event) {
    // Соединение закрыто
    console.log("WebSocket connection closed.");
};

function getElementByIdValue(id) {
    return document.getElementById(id).value.trim();
}

function validateInput(value, errorMessage, notificationId = 'notification') {
    var notificationDiv = document.getElementById(notificationId);

    if (value === '') {
        notificationDiv.innerHTML = errorMessage;
        notificationDiv.style.backgroundColor = '#f44336';
        notificationDiv.style.display = 'block';
        return false;
    } else {
        notificationDiv.style.display = 'none';
        return true;
    }
}

function validateInputToParams(Bool, section) {
    var notificationDiv = document.getElementById('notification');

    if(Bool){
        notificationDiv.style.display = 'none';
        return true;
    }
    else{
        notificationDiv.innerHTML = `Введены неккоректные данные в разделе "${section}"!`;
        notificationDiv.style.backgroundColor = '#f44336';
        notificationDiv.style.display = 'block';
        return false;
    }
}

function validateNumber(value, max, sectionName) {
    var errorMessage = `Заполните все поля в разделе "${sectionName}"!`;

    if (!validateInput(value, errorMessage)) {
        return false;
    } else {
        return validateInputToParams(value <= max, sectionName)
               && validateInputToParams(value > 0, sectionName);
    }
}

function inputDataValidation(){
    var FileName = getElementByIdValue('inputFileName');
    var IterationCount = getElementByIdValue('inputIterationCount');

    var sectionName = 'Ввод входных данных';


    return validateNumber(IterationCount, 20, sectionName)

// Добавление обработчика клика на кнопку отправки сообщения
document.getElementById('inputDataButton').addEventListener('click', function() {
    var FileName = getElementByIdValue('inputFileName');
    var IterationCount = getElementByIdValue('inputIterationCount');

    var sectionName = 'Ввод входных данных';
    var errorMessage = `Заполните все поля в разделе "${sectionName}"!`;

    if(validateNumber(IterationCount, 20, sectionName) && validateInput(FileName, errorMessage)){
        if (!FileName.endsWith(".txt")) FileName += ".txt";

        ws.send(`${FileName}*${IterationCount}`);
        event.preventDefault();
    }
});