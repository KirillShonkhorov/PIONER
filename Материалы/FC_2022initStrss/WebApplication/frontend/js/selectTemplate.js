window.onload = async function () {
    const notificationContainer = document.getElementById('error-container');
    const notificationMsg = document.getElementById('notification-msg');

    const templatesContainer = document.getElementById('templates-container');
    const noTemplatesMsg = document.getElementById('no-templates-msg');
    const createTemplateBtn = document.getElementById('create-template-btn');

    try {
        const response = await fetch('/get_input_templates');
        const data = await response.json();

        if (Object.keys(data).length === 0) {
            noTemplatesMsg.style.display = createTemplateBtn.style.display = 'block';
        } else {
            for (const [fileName, fileContent] of Object.entries(data)) {
                const fileDiv = document.createElement('div');
                fileDiv.classList.add('file');

                const fileNameHeading = document.createElement('h3');
                fileNameHeading.textContent = fileName;
                fileDiv.appendChild(fileNameHeading);

                const fileContentPre = document.createElement('pre');
                fileContentPre.classList.add('file-content');
                fileContentPre.textContent = fileContent;
                fileDiv.appendChild(fileContentPre);

                const selectBtn = document.createElement('button');
                selectBtn.textContent = 'Выбрать шаблон';
                selectBtn.classList.add('btn');
                selectBtn.addEventListener('click', function () {
                    const selectedFileName = fileName;
                    const selectedFileContent = fileContent;
                    window.location.href = `/static/html/editTemplate.html?fileName=${encodeURIComponent(selectedFileName)}&fileContent=${encodeURIComponent(selectedFileContent)}`;
                });
                fileDiv.appendChild(selectBtn);

                templatesContainer.appendChild(fileDiv);
            }
        }
    } catch (error) {
        handleError(error);
    }
};

async function createNewTemplate() {
    window.location.href = "static/html/index.html";
}

async function handleError(error) {
    console.error('Error:', error);
    notificationMsg.textContent += error;
    notificationContainer.style.display = 'block';
}