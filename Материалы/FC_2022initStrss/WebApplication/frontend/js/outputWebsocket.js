//ws.onmessage = async function(event) {
//    try {
//        const { message, messages } = loadDOMElements();
//        const data = JSON.parse(event.data);
//
//        const DisplacementsScriptElement = document.createElement('script');
//        DisplacementsScriptElement.innerHTML = data.displacements.scripts;
//        document.body.appendChild(DisplacementsScriptElement);
//
//        // Разбираем строку divAttributes и извлекаем атрибуты
//        const DisplacementsDivAttributes = data.displacements.divs
//        const DisplacementsIdMatch = DisplacementsDivAttributes.match(/id="([^"]+)"/);
//        const DisplacementsDataRootIdMatch = DisplacementsDivAttributes.match(/data-root-id="([^"]+)"/);
//        const DisplacementsStyleMatch = DisplacementsDivAttributes.match(/style="([^"]+)"/);
//
//        const DisplacementsDivElement = document.createElement('div');
//
//        // Устанавливаем атрибуты извлеченных данных
//        if (DisplacementsIdMatch) {DisplacementsDivElement.setAttribute('id', DisplacementsIdMatch[1]);}
//        if (DisplacementsDataRootIdMatch) {DisplacementsDivElement.setAttribute('data-root-id', DisplacementsDataRootIdMatch[1]);}
//        if (DisplacementsStyleMatch) {DisplacementsDivElement.setAttribute('style', DisplacementsStyleMatch[1]);}
//
//        message.appendChild(DisplacementsDivElement);
//
//        const StressScriptElement = document.createElement('script');
//        StressScriptElement.innerHTML = data.stress.scripts;
//        document.body.appendChild(StressScriptElement);
//
//        // Разбираем строку divAttributes и извлекаем атрибуты
//        const StressDivAttributes = data.stress.divs
//        const StressIdMatch = StressDivAttributes.match(/id="([^"]+)"/);
//        const StressDataRootIdMatch = StressDivAttributes.match(/data-root-id="([^"]+)"/);
//        const StressStyleMatch = StressDivAttributes.match(/style="([^"]+)"/);
//
//        const StressDivElement = document.createElement('div');
//
//        // Устанавливаем атрибуты извлеченных данных
//        if (StressIdMatch) {StressDivElement.setAttribute('id', StressIdMatch[1]);}
//        if (StressDataRootIdMatch) {StressDivElement.setAttribute('data-root-id', StressDataRootIdMatch[1]);}
//        if (StressStyleMatch) {StressDivElement.setAttribute('style', StressStyleMatch[1]);}
//
//        message.appendChild(StressDivElement);
//
//        messages.appendChild(message);
//
//    } catch (error) {
//        await handleError(error);
//    }
//};

// Функция для загрузки всех элементов DOM
async function loadDOMElements() {
    const getElement = id => document.getElementById(id);
    const createElement = type => document.createElement(type);

    return {
        notificationContainer: getElement('error-container'),
        notificationMsg: getElement('notification-msg'),
        messages: getElement('messages'),
        dropdown: createElement('div'),
        button: createElement('button'),
        dropdownContent: createElement('div')
    };
}

// Функция для подключения к веб-сокету при загрузке страницы
window.onload = async function ConnectToWebsocket() {
    try {
        const response = await fetch('/get_ip_address');
        const ipAddress = await response.text().then(data => data.replace(/"/g, ''));
        const ws = new WebSocket(`ws://${ipAddress}/ws`);

        ws.onopen = async event => WebsocketOpen(event, ws);
        ws.onerror = async event => handleError(event);
        ws.onmessage = async event => WebsocketMessage(event);
        ws.onclose = async event => handleError(event);
    } catch (error) {
        handleError(error);
    }
};

// Функция для отправки запроса на сервер при открытии соединения с веб-сокетом
async function WebsocketOpen(event, ws) {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const fileName = urlParams.get('fileName');
        await ws.send(fileName);
        await event.preventDefault();
    } catch (error) {
        handleError(error);
    }
}

// Функция для обработки сообщений от веб-сокета
async function WebsocketMessage(event) {
    try{
        const data = JSON.parse(event.data);
        const { messages } = await loadDOMElements();
        console.log(data);

        for (const [key, value] of Object.entries(data)) {
            if (key !== 'graphs') {
                const dropdown = await createDropdown(key, value, data.graphs);
                messages.appendChild(dropdown);
            }
        }
    }catch (error){
        handleError(error);
    }
}

// Функция для создания выпадающего списка
async function createDropdown(key, value, graphs) {
    try{
        const { dropdown, button, dropdownContent } = await loadDOMElements();

        dropdown.classList.add('dropdown');

        button.textContent = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
        button.addEventListener('click', async () => {
            dropdown.classList.toggle('show');
        });
        dropdown.appendChild(button);

        dropdownContent.classList.add('dropdown-content');

        for (const [titleKey, titleValue] of Object.entries(value)) {
            const title = document.createElement('h3');
            title.textContent = titleKey;
            title.style.textAlign = 'center';
            dropdownContent.appendChild(title);

            const tableContainer = document.createElement('div');
            tableContainer.classList.add('table-div');

            const table = document.createElement('table');
            table.classList.add('table');

            const tbody = document.createElement('tbody');
            const headerRow = document.createElement('tr');

            for (const [headerKey, headerValue] of Object.entries(titleValue[0])) {
                const headerCell = document.createElement('td');
                headerCell.textContent = headerKey;
                headerRow.appendChild(headerCell);
            }
            tbody.appendChild(headerRow);

            titleValue.forEach(item => {
                const row = document.createElement('tr');

                for (const [, value] of Object.entries(item)) {
                    const cell = document.createElement('td');
                    cell.textContent = value;
                    row.appendChild(cell);
                }
                tbody.appendChild(row);
            });

            table.appendChild(tbody);
            tableContainer.appendChild(table);
            dropdownContent.appendChild(tableContainer);

            for (const [graphsKey, graphsValue] of Object.entries(graphs)) {
                for (const [modelKey, modelValue] of Object.entries(graphsValue)) {
                    if (modelKey == 'scripts'){
                        const ScriptElement = document.createElement('script');
                        ScriptElement.innerHTML = modelValue;
                        document.body.appendChild(ScriptElement);
                    }
                    else{
                        const DivAttributes = modelValue;
                        const IdMatch = DivAttributes.match(/id="([^"]+)"/);
                        const DataRootIdMatch = DivAttributes.match(/data-root-id="([^"]+)"/);
                        const StyleMatch = DivAttributes.match(/style="([^"]+)"/);

                        DivElement = document.createElement('div');

                        // Устанавливаем атрибуты извлеченных данных
                        if (IdMatch) {DivElement.setAttribute('id', IdMatch[1]);}
                        if (DataRootIdMatch) {DivElement.setAttribute('data-root-id', DataRootIdMatch[1]);}
                        if (StyleMatch) {DivElement.setAttribute('style', StyleMatch[1]);}

                        dropdownContent.appendChild(DivElement);
                    }
                }
            }
        }

        dropdown.appendChild(dropdownContent);
        return await dropdown;
    } catch (error){
        handleError(error);
    }
}

// Функция для обработки ошибок
async function handleError(error) {
    const { notificationContainer, notificationMsg } = await loadDOMElements();
    notificationMsg.textContent += error;
    notificationContainer.style.display = 'block';
}