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

    const fileContentPre = document.createElement('pre');
    fileContentPre.classList.add('file-content');
    fileContentPre.textContent = fileContent;
    fileDiv.appendChild(fileContentPre);

    const selectBtn = await createSelectButton(fileName, fileContent);
    fileDiv.appendChild(selectBtn);

    const deleteBtn = await createDeleteButton(fileName);
    fileDiv.appendChild(deleteBtn);

    return await fileDiv;
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
                await handleError(await response.text);
            }

            await loadDataAndProcess();
        } catch (error) {
            await handleError(error);
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

// Функция для загрузки и обработки данных
async function loadDataAndProcess() {
    try {
        const response = await fetch('/get_input_templates');
        const answer = await response.json();

        const { templatesContainer, noTemplatesMsg, createTemplateBtn } = await loadDOMElements();

        await removeAllChildElements(templatesContainer);

        if (await answer.data && await answer.data.status_code) {
            await handleError(await answer.data.details);
        } else {
            if (Object.keys(answer).length === 0) {
                noTemplatesMsg.style.display = createTemplateBtn.style.display = 'block';
            } else {
                noTemplatesMsg.style.display = createTemplateBtn.style.display = 'none';

                for (const [fileName, fileContent] of Object.entries(answer)) {
                    const fileDiv = await createFileDiv(fileName, fileContent);
                    await templatesContainer.appendChild(fileDiv);
                }
            }
        }
    } catch (error) {
        await handleError(error);
    }
}

// Загрузка данных и обработка после загрузки DOM
window.onload = async function () {
    await loadDataAndProcess();
};

// Функция для создания нового шаблона
async function createNewTemplate() {
    window.location.href = "static/html/index.html";
}

// Функция для обработки ошибок
async function handleError(error) {
    console.error('Error:', error);
    const { notificationContainer, notificationMsg } = await loadDOMElements();
    notificationMsg.textContent += error;
    notificationContainer.style.display = 'block';
}
