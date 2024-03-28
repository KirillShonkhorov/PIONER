// Функция для загрузки всех элементов DOM
async function loadDOMElements() {
    const getElement = id => document.getElementById(id);
    return await{
        notificationContainer: getElement('error-container'),
        notificationMsg: getElement('notification-msg'),
        inputFileName: getElement('file-name'),
        inputFileContent: getElement('file-content')
    };
}

// Функция для загрузки и обработки данных
async function loadDataAndProcess() {
    try {
        const { inputFileName, inputFileContent } = await loadDOMElements();
        const params = new URLSearchParams(window.location.search);
        const fileName = params.get('fileName');
        const fileContent = params.get('fileContent');

        inputFileName.value = fileName;
        inputFileContent.value = fileContent;
    } catch (error) {
        await handleError(error);
    }
}

// Функция для сохранения и запуска шаблона
async function saveAndRunTemplate() {
    try {
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
            await handleError(response.text());
        } else {
            window.location.href = `/static/html/outputWebsocket.html?fileName=${encodeURIComponent(fileName)}`;
        }

    } catch (error) {
        await handleError(error);
    }
}

// Загрузка данных и обработка после загрузки DOM
window.onload = async function () {
    await loadDataAndProcess();
};

// Функция для обработки ошибок
async function handleError(error) {
    console.error('Error:', error);
    const { notificationContainer, notificationMsg } = await loadDOMElements();
    notificationMsg.textContent += error;
    notificationContainer.style.display = 'block';
}
