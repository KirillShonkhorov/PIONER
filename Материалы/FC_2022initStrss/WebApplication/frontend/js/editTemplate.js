const getElement = id => document.getElementById(id);

const notificationContainer = getElement('error-container');
const notificationMsg = getElement('notification-msg');

const inputFileName = getElement('file-name');
const inputFileContent = getElement('file-content');

try {
    const params = new URLSearchParams(window.location.search);
    const fileName = params.get('fileName');
    const fileContent = params.get('fileContent');

    inputFileName.value = fileName;
    inputFileContent.value = fileContent;
} catch (error) {
    handleError(error);
}

async function saveAndRunTemplate() {
    try {
        const { value: fileName } = inputFileName;
        const { value: fileContent } = inputFileContent;

        const response = await fetch('/save_input_template', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fileName, fileContent })
        });

        if (!response.ok) {
            handleError(response.text());
        }

        console.log('Template saved successfully.');
        window.location.href = `/static/html/outputWebsocket.html?fileName=${encodeURIComponent(fileName)}`;

    } catch (error) {
        handleError(error);
    }
}

async function handleError(error) {
    console.error('Error:', error);
    notificationMsg.textContent += error;
    notificationContainer.style.display = 'block';
}
