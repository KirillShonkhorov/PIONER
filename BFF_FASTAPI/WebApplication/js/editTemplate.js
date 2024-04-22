// Функция для загрузки всех элементов DOM
async function loadDOMElements() {
    const getElement = id => document.getElementById(id);
    return await{
        notificationContainer: getElement('error-container'),
        notificationMsg: getElement('notification-msg'),
        inputFileName: getElement('file-name'),
        inputFileContent: getElement('file-content'),
        saveBtn: getElement('save-run-btn')
    };
}

// Функция для загрузки и обработки данных
async function loadDataAndProcess() {
    const { inputFileName, inputFileContent, saveBtn } = await loadDOMElements();
    const params = new URLSearchParams(window.location.search);
    const fileName = params.get('fileName');
    const fileContent = params.get('fileContent');

    if (fileName && fileContent) {
        inputFileName.value = fileName;
        inputFileContent.value = fileContent;
        await adjustTextareaHeight(inputFileContent);
        saveBtn.style.display = 'block';
    } else {
        inputFileName.value = '';
        inputFileContent.value = '';
        const shortFileName = fileName?.length > 50 ? fileName.slice(0, 47) + '...' : fileName;
        const shortFileContent = fileContent?.length > 50 ? fileContent.slice(0, 47) + '...' : fileContent;
        await handleError(`Данные файла не были получены.<br>
            Имя файла: "${shortFileName}"<br>Содержимое файла: "${shortFileContent}"`);
    }
}

async function adjustTextareaHeight(textarea) {
    const lines = textarea.value.split('\n');
    textarea.rows = lines.length;
}

// Функция для сохранения и запуска шаблона
async function saveAndRunTemplate() {
    const { inputFileName, inputFileContent } = await loadDOMElements();
    const fileName = inputFileName.value;
    const fileContent = inputFileContent.value;

    const response = await fetch('/save_input_template', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ fileName, fileContent })
    });

    if (!response.ok) {
        await handleError(`Не удалось сохранить файл.<br>Детали: ${response.text()}`);
    } else {
        window.location.href = `/static/html/outputWebsocket.html?fileName=${encodeURIComponent(fileName)}`;
    }
}

// Загрузка данных и обработка после загрузки DOM
window.onload = async function () {
    await loadDataAndProcess();
};

// Функция для обработки ошибок
async function handleError(error) {
    const { notificationContainer, notificationMsg } = await loadDOMElements();
    notificationMsg.innerHTML = error;
    notificationContainer.style.display = 'block';
}
