// Асинхронная функция для загрузки всех элементов DOM
async function loadDOMElements() {
    const getElement = id => document.getElementById(id);
    const notificationContainerPromise = getElement('error-container');
    const notificationMsgPromise = getElement('notification-msg');
    const templatesContainerPromise = getElement('templates-container');
    const noTemplatesMsgPromise = getElement('no-templates-msg');
    const createTemplateBtnPromise = getElement('create-template-btn');

    // Ожидаем загрузку всех элементов DOM
    const [
        notificationContainer,
        notificationMsg,
        templatesContainer,
        noTemplatesMsg,
        createTemplateBtn
    ] = await Promise.all([
        notificationContainerPromise,
        notificationMsgPromise,
        templatesContainerPromise,
        noTemplatesMsgPromise,
        createTemplateBtnPromise
    ]);

    return await { notificationContainer, notificationMsg, templatesContainer, noTemplatesMsg, createTemplateBtn };
}

// Асинхронная функция для загрузки и обработки данных
async function loadDataAndProcess() {
    try {
        const response = await fetch('/get_input_templates');
        const answer = await response.json();

        if (answer.data && answer.data.status_code) {
            handleError(answer.data.details);
        } else {
            const { templatesContainer, noTemplatesMsg, createTemplateBtn } = await loadDOMElements();

            while (templatesContainer.firstChild){
                templatesContainer.removeChild(templatesContainer.firstChild);
            }

            if (Object.keys(answer).length === 0) {
                noTemplatesMsg.style.display = createTemplateBtn.style.display = 'block';
            } else {
                noTemplatesMsg.style.display = createTemplateBtn.style.display = 'none';

                for (const [fileName, fileContent] of Object.entries(answer)) {
                    const fileDiv = await createFileDiv(fileName, fileContent);
                    templatesContainer.appendChild(fileDiv);
                }
            }
        }
    } catch (error) {
        handleError(error);
    }
}

// Загрузка данных и обработка после загрузки DOM
window.onload = async function () {
    await loadDataAndProcess();
};

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

    return fileDiv;
}

async function createDeleteButton(fileName) {
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Удалить шаблон';
    deleteBtn.classList.add('btn');
    deleteBtn.addEventListener('click', async function () {
        try{
            const selectedFileName = fileName;

            const response = await fetch('/delete_input_template', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ fileName })
            });

            if (!response.ok) {
                handleError(response.text());
            }

            loadDataAndProcess();
        }
        catch (error){
            handleError(error);
        }
    });
    return deleteBtn;
}

async function createSelectButton(fileName, fileContent) {
    const selectBtn = document.createElement('button');
    selectBtn.textContent = 'Выбрать шаблон';
    selectBtn.classList.add('btn');
    selectBtn.addEventListener('click', async function () {
        const selectedFileName = fileName;
        const selectedFileContent = fileContent;
        window.location.href = `/static/html/editTemplate.html?fileName=${encodeURIComponent(selectedFileName)}&fileContent=${encodeURIComponent(selectedFileContent)}`;
    });
    return selectBtn;
}

async function createNewTemplate() {
    window.location.href = "static/html/index.html";
}

async function handleError(error) {
    console.error('Error:', error);
    const { notificationContainer, notificationMsg } = await loadDOMElements();
    notificationMsg.textContent += error;
    notificationContainer.style.display = 'block';
}