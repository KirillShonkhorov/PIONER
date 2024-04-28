// Функция для загрузки всех элементов DOM
async function loadDOMElements() {
    const getElement = id => document.getElementById(id);
    return await {
        notificationContainer: getElement('error-container'),
        notificationMsg: getElement('notification-msg'),
        templatesContainer: getElement('templates-container'),
        noTemplatesMsg: getElement('no-templates-msg'),
        createTemplateBtn: getElement('create-template-btn')
    };
}

// Функция для удаления всех дочерних элементов из контейнера
async function removeAllChildElements(container) {
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
}

// Функция для создания дочернего элемента, представляющего файл
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

    const selectBtn = await createSelectButton(fileName, fileContent);
    innerDiv.appendChild(selectBtn);

    const deleteBtn = await createDeleteButton(fileName);
    innerDiv.appendChild(deleteBtn);

    const hideBtn = await createHideButton(innerDiv);
    fileDiv.appendChild(hideBtn);

    fileDiv.appendChild(innerDiv);

    return await fileDiv;
}

// Функция для создания кнопки выбора файла
async function createHideButton(innerDiv) {
    const HideBtn = document.createElement('button');
    HideBtn.classList.add('btn');
    HideBtn.textContent = 'Показать';
    HideBtn.addEventListener('click', async function () {
        if (innerDiv.style.display === "none") {
            HideBtn.textContent = 'Скрыть';
            innerDiv.style.display = "block";
        } else {
            HideBtn.textContent = 'Показать';
            innerDiv.style.display = "none";
        }
    });
    return await HideBtn;
}

// Функция для создания кнопки удаления файла
async function createDeleteButton(fileName) {
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Удалить шаблон';
    deleteBtn.classList.add('btn');
    deleteBtn.addEventListener('click', async function () {
        try {
            const selectedFileName = fileName;
            const response = await fetch('/delete_input_template', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ fileName })
            });

            if (!response.ok) {
                await handleError(`Не удалось удалить шаблон.<br>Детали: ${await response.text}`);
            }

            await loadDataAndProcess();
        } catch (error) {
            await handleError(`Не удалось удалить шаблон.<br>Детали: ${error}`);
        }
    });
    return await deleteBtn;
}

// Функция для создания кнопки выбора файла
async function createSelectButton(fileName, fileContent) {
    const selectBtn = document.createElement('button');
    selectBtn.textContent = 'Выбрать шаблон';
    selectBtn.classList.add('btn');
    selectBtn.addEventListener('click', async function () {
        const selectedFileName = fileName;
        const selectedFileContent = fileContent;
        window.location.href = `/static/html/editTemplate.html?fileName=${encodeURIComponent(selectedFileName)}&fileContent=${encodeURIComponent(selectedFileContent)}`;
    });
    return await selectBtn;
}

let dataProcessed = false;

// Функция для загрузки и обработки данных
async function loadDataAndProcess() {
    try {
        const response = await fetch('/get_input_templates');
        const answer = await response.json();

        const { templatesContainer, noTemplatesMsg, createTemplateBtn } = await loadDOMElements();
        await removeAllChildElements(templatesContainer);

        if (await answer.data && await answer.data.status_code) {
            await handleError(`Сервер не вернул ответ.<br>Детали: ${await answer.data.details}`);
        } else {
            if (answer.templates.length === 0) {
                noTemplatesMsg.style.display = createTemplateBtn.style.display = 'block';
            } else {
                noTemplatesMsg.style.display = createTemplateBtn.style.display = 'none';

                for (const [, fileContent] of Object.entries(answer.templates)) {
                    const fileDiv = await createFileDiv(fileContent.file_name, fileContent.file_content);
                    await templatesContainer.appendChild(fileDiv);
                }
            }
        }
        dataProcessed = true;
    } catch (error) {
        await handleError(error);
    }
}

// Загрузка данных и обработка после загрузки DOM
window.onload = async function () {
    try {
        // Установить таймер для отображения уведомления о долгой загрузке
        const timeoutPromise = new Promise((resolve) => {
            setTimeout(async () => {
                if (!dataProcessed) {
                    await showNotification();
                }
                resolve();
            }, 5000); // Время в миллисекундах (в данном случае 3 секунды)
        });

        // Выполнить запрос на получение данных и таймер параллельно
        await Promise.all([loadDataAndProcess(), timeoutPromise]);
    } catch (error) {
        await handleError(error);
    }
};

// Функция для создания нового шаблона
async function createNewTemplate() {
    window.location.href = "static/html/index.html";
}

// Функция для отображения уведомления
async function showNotification() {
    document.getElementById("load-notification").style.display = "block";
}

// Функция для загрузки облегченной версии сайта
async function loadLightVersion() {
    window.location.href = '/light_app';
}

async function hideNotification() {
    const notification = document.getElementById('load-notification');
    notification.style.display = 'none';
}

// Функция для обработки ошибок
async function handleError(error) {
    const { notificationContainer, notificationMsg } = await loadDOMElements();
    notificationMsg.innerHTML = error;
    notificationContainer.style.display = 'block';
}