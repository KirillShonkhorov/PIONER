const elements = {
    notificationContainer: document.getElementById('error-container'),
    notificationMsg: document.getElementById('notification-msg'),
    inputFileName: document.getElementById('file-name'),
    inputFileContent: document.getElementById('file-content'),
    saveBtn: document.getElementById('save-run-btn'),
    loadingSpinner: document.getElementById('loading-spinner'),
    overlay: document.getElementById('overlay'),
    customNotification: document.getElementById('custom-notification'),
    closeSpan: document.getElementById('close-notification'),
    confirmNotificationButton: document.getElementById('confirm-notification'),
    infoNotification: document.getElementById('info-custom-notification'),
    cancelNotificationButton: document.getElementById('cancel-notification')
};

elements.confirmNotificationButton.addEventListener('click', confirmNotification);
elements.cancelNotificationButton.addEventListener('click', async () => {elements.overlay.style.display = 'none'; elements.customNotification.style.display = 'none';});
elements.closeSpan.addEventListener('click', async () => {elements.overlay.style.display = 'none'; elements.customNotification.style.display = 'none';});

loadDataAndProcess();

async function loadDataAndProcess() {
    elements.overlay.style.display = 'block';
    elements.loadingSpinner.style.display = 'block';

    const params = new URLSearchParams(window.location.search);
    const fileName = params.get('fileName');

    try {
        const response = await fetch('/get_input_template_by_name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fileName })
        });
        const { file_name: outputFileName, file_content: outputFileContent } = await response.json();

        if (outputFileName && outputFileContent) {
            elements.inputFileName.value = outputFileName;
            elements.inputFileContent.value = outputFileContent;

            const lines = elements.inputFileContent.value.split('\n');
            elements.inputFileContent.rows = lines.length;

            elements.saveBtn.style.display = 'block';
        } else {
            elements.inputFileName.value = '';
            elements.inputFileContent.value = '';
            const shortFileName = outputFileName?.length > 50 ? outputFileName.slice(0, 47) + '...' : outputFileName;
            const shortFileContent = outputFileContent?.length > 50 ? outputFileContent.slice(0, 47) + '...' : outputFileContent;
            handleError(`Данные файла не были получены.<br>Имя файла: "${shortFileName}"<br>Содержимое файла: "${shortFileContent}"`);
        }
    } catch (error) {
        handleError(error);
    }
    elements.loadingSpinner.style.display = 'none';
    elements.overlay.style.display = 'none';
}

async function saveAndRunTemplate() {
    elements.overlay.style.display = 'block';
    elements.loadingSpinner.style.display = 'block';

    const fileName = elements.inputFileName.value;
    const fileContent = elements.inputFileContent.value;

    try {
        const checkResponse = await fetch('/get_input_template_by_name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fileName })
        });
        const answer = await checkResponse.json();

        if (answer.data && answer.data.status_code === 400){
            await saveInputTemplate(fileName, fileContent);
        } else {
            elements.loadingSpinner.style.display = 'none';
            elements.infoNotification.innerHTML = `Файл "${fileName}" уже существует, перезаписать?`
            elements.customNotification.style.display = 'block';
        }
    } catch (error) {
        handleError(error);
    }
}

async function confirmNotification() {
    elements.customNotification.style.display = 'none';
    elements.loadingSpinner.style.display = 'block';

    const fileName = elements.inputFileName.value;
    const fileContent = elements.inputFileContent.value;

    await saveInputTemplate(fileName, fileContent);
}

async function saveInputTemplate(fileName, fileContent) {
    try {
        const saveResponse = await fetch('/save_input_template', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fileName, fileContent })
        });

        elements.loadingSpinner.style.display = 'none';
        elements.overlay.style.display = 'none';

        if (!saveResponse.ok) {
            handleError(`Не удалось сохранить файл.<br>Детали: ${await saveResponse.text()}`);
        } else {
            window.location.href = `/static/html/outputWebsocket.html?fileName=${encodeURIComponent(fileName)}`;
        }
    } catch (error) {
        handleError(`Не удалось сохранить файл.<br>Детали: ${error}`);
    }
}

async function handleError(error) {
    elements.notificationMsg.innerHTML = error;
    elements.notificationContainer.style.display = 'block';
}