const elements = {
    notificationContainer: document.getElementById('error-container'),
    notificationMsg: document.getElementById('notification-msg'),
    templatesContainer: document.getElementById('templates-container'),
    noTemplatesMsg: document.getElementById('no-templates-msg'),
    createTemplateBtn: document.getElementById('create-template-btn'),
    customNotification: document.getElementById('custom-notification'),
    closeSpan: document.getElementById('close-notification'),
    confirmNotificationButton: document.getElementById('confirm-notification'),
    cancelNotificationButton: document.getElementById('cancel-notification'),
    infoNotification: document.getElementById('info-custom-notification'),
    overlay: document.getElementById('overlay'),
    loadingSpinner: document.getElementById('loading-spinner'),
    loadNotification: document.getElementById('load-notification'),
    createTemplateBtn: document.getElementById('create-template-btn'),
    loadNotificationCloseBtn: document.getElementById('close-btn'),
    loadLightAppBtn: document.getElementById('load-light-app-btn'),
};

elements.createTemplateBtn.addEventListener('click', async () => {window.location.href = "static/html/index.html";});
elements.loadNotificationCloseBtn.addEventListener('click', async () => {elements.loadNotification.style.display = 'none';});
elements.loadLightAppBtn.addEventListener('click', async () => {window.location.href = '/light_app';});
elements.confirmNotificationButton.addEventListener('click', confirmNotification);
elements.cancelNotificationButton.addEventListener('click', async () => {elements.overlay.style.display = 'none'; elements.customNotification.style.display = 'none';});
elements.closeSpan.addEventListener('click', async () => {elements.overlay.style.display = 'none'; elements.customNotification.style.display = 'none';});


async function createFileDiv(fileName, fileContent) {
    const fileDiv = document.createElement('div');
    fileDiv.classList.add('file');

    const fileNameHeading = document.createElement('h3');
    fileNameHeading.textContent = fileName;
    fileDiv.appendChild(fileNameHeading);

    const innerDiv = document.createElement('div');
    innerDiv.style.display = 'none';

    const fileContentPre = document.createElement('pre');
    fileContentPre.classList.add('file-content');
    fileContentPre.textContent = fileContent;
    innerDiv.appendChild(fileContentPre);

    const selectBtn = await createButton('Выбрать шаблон', async () => {
        window.location.href = `/static/html/editTemplate.html?fileName=${encodeURIComponent(fileName)}`;
    });
    innerDiv.appendChild(selectBtn);

    const deleteBtn = await createButton('Удалить шаблон', async () => {
        elements.overlay.style.display = 'block';
        elements.infoNotification.innerHTML = `Вы уверены, что хотите удалить файл "${fileName}"?`
        elements.customNotification.style.display = 'block';
    });
    innerDiv.appendChild(deleteBtn);

    const hideBtn = await createButton('Показать', async () => {
        if (innerDiv.style.display === "none") {
            hideBtn.textContent = 'Скрыть';
            innerDiv.style.display = "block";
        } else {
            hideBtn.textContent = 'Показать';
            innerDiv.style.display = "none";
        }
    });
    fileDiv.appendChild(hideBtn);
    fileDiv.appendChild(innerDiv);

    return fileDiv;
}

async function createButton(text, onClick) {
    const button = document.createElement('button');
    button.classList.add('btn');
    button.textContent = text;
    button.addEventListener('click', onClick);
    return button;
}

async function loadDataAndProcess() {
    try {
        elements.overlay.style.display = 'block';
        elements.loadingSpinner.style.display = 'block';

        const response = await fetch('/get_input_templates');
        const answer = await response.json();

        elements.templatesContainer.innerHTML = '';

        if (answer.data && answer.data.status_code) {
            handleError(`Сервер не вернул ответ.<br>Детали: ${answer.data.details}`);
        } else {
            if (answer.templates.length === 0) {
                 elements.noTemplatesMsg.style.display = elements.createTemplateBtn.style.display = 'block';
            } else {
                elements.noTemplatesMsg.style.display = elements.createTemplateBtn.style.display = 'none';

                for (const [, fileContent] of Object.entries(answer.templates)) {
                    const fileDiv = await createFileDiv(fileContent.file_name, fileContent.file_content);
                    elements.templatesContainer.appendChild(fileDiv);
                }
            }
        }
        elements.loadingSpinner.style.display = 'none';
        elements.overlay.style.display = 'none';
    } catch (error) {
        handleError(error);
    }
}

window.onload = async function () {
    try {
        const timeoutPromise = new Promise((resolve) => {
            setTimeout(async () => {
                elements.loadNotification.style.display = "block";
                resolve();
            }, 5000);
        });
        await Promise.all([loadDataAndProcess(), timeoutPromise]);
    } catch (error) {
        await handleError(error);
    }
};

async function confirmNotification() {
    try {
        elements.customNotification.style.display = 'none';
        elements.loadingSpinner.style.display = 'block';

        const htmlContent = elements.infoNotification.innerHTML;
        const matches = htmlContent.match(/"(.*?)"/);

        if (matches && matches.length > 1) {
            const fileName = matches[1];

            const response = await fetch('/delete_input_template', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ fileName })
            });
            if (!response.ok) {
                handleError(`Не удалось удалить шаблон.<br>Детали: ${await response.text}`);
            }
            await loadDataAndProcess();
        }
    } catch (error) {
        handleError(`Не удалось удалить шаблон.<br>Детали: ${error}`);
    }
}

async function handleError(error) {
    elements.notificationMsg.innerHTML = error;
    elements.notificationContainer.style.display = 'block';
}