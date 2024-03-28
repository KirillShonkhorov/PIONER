//Div's ID
const HEAD_SECTION = 0;
const KEY_DATA_SECTION = 1;
const TIME_PARAMETERS_SECTION = 2;
const ITERATION_PARAMETERS_SECTION = 3;
const NODE_COORDINATES_SECTION = 4;
const CONTROL_TIME_FUNCTION_SECTION = 5;
const TIME_FUNCTION1_SECTION = 6;

//Float input elements
const inputElements = ['Tfinal', 'r_initial_delta_t', 'r_minimum_delta_t', 'r_maximum_delta_t', 'Dtol', 'Ftol', 'Etol'];
inputElements.forEach(elementId => document.getElementById(elementId).addEventListener('input', handleInput));

function getElementByIdValue(id) {
    return document.getElementById(id).value.trim();
}

//Generate N-count group fields
function generateGroups(sectionId, groupName, groupId, countId, groupDivId, createInputsFunction, visibilityFunction) {
    var groupCount = getElementByIdValue(countId);
    var inputDiv = document.getElementById(sectionId);

    inputDiv.innerHTML = '';

    createAndAppend('h3', groupName, inputDiv);

    for (var i = 1; i <= groupCount; i++) {
        var generatedGroup = createAndAppend('div', null, inputDiv, 'group');
        createAndAppend('p1', `${groupId} ${i}`, generatedGroup);

        createInputsFunction(i, generatedGroup);
    }

    var button = createAndAppend('button', 'Далее', inputDiv);
    button.id = groupDivId;
    button.type = 'button';
    button.addEventListener('click', visibilityFunction);

    createAndAppend('hr', null, inputDiv);
}

function createAndAppendNodeCoordinatesInputs(i, parent) {
    createAndAppendInput('n', 'Номер узла (n 1-10):', i, parent, i);
    createAndAppendInput('id(1,n)', 'Код смещения по оси X (id(1,n) 11-15):', '1 OR 0', parent, null);
    createAndAppendInput('id(2,n)', 'Код смещения по оси Y (id(2,n) 16-20):', '1 OR 0', parent, null);
    createAndAppendInput('X', 'X-координата (X 31-50):', 'default =0.001', parent, null);
    createAndAppendInput('Y', 'Y-координата (Y 51-70):', 'default =0.001', parent, null);
}

function createAndAppendTimeFunction1Inputs(i, parent) {
    createAndAppendInput('k', 'Номер функции расписания (k 1-5):', i, parent, i);
    createAndAppendInput('npt', 'Количество точек, используемых для определения этой функции (npt 6-10):', 'npt ≤ Nptm', parent, null);
}

function createAndAppend(tag, text, parent, className) {
    var element = document.createElement(tag);

    if (text) element.textContent = text;
    if (className) element.className = className;
    if (parent) parent.appendChild(element);

    return element;
}

function createAndAppendInput(id, label, placeholder, parent, value) {
    var groupDiv = createAndAppend('div', null, parent);
    var labelElement = createAndAppend('label', label, groupDiv);
    var inputElement = createAndAppend('input', null, groupDiv);

    switch (id){
        case 'n':
        case 'k':
            inputElement.type = 'number';
            inputElement.id = id;
            inputElement.name = id;
            inputElement.readOnly = true;
            inputElement.value = value;
            break;

        case 'id(1,n)':
        case 'id(2,n)':
            inputElement.type = 'number';
            inputElement.id = id;
            inputElement.name = id;
            inputElement.placeholder = placeholder;
            inputElement.min = '0';
            inputElement.max = '1';
            inputElement.addEventListener('input', handleBinaryInput);
            break;

        case 'X':
        case 'Y':
            inputElement.type = 'text';
            inputElement.id = id;
            inputElement.name = id;
            inputElement.placeholder = placeholder;
            inputElement.maxLength = '8';
            inputElement.addEventListener('input', handleInput);
            break;

        case 'npt':
            inputElement.type = 'number';
            inputElement.id = id;
            inputElement.name = id;
            inputElement.placeholder = placeholder;
            inputElement.max = getElementByIdValue('Nptm');
            inputElement.addEventListener('input', handleInput);

            document.getElementById('Nptm').addEventListener('input', function () {
                var nptInput = document.getElementById('npt');
                nptInput.max = this.value;
            });

            break;
    }

    labelElement.htmlFor = id;
    return inputElement;
}

function handleInput(event) {
    var value = event.target.value;
    var replacement = event.target.type === 'number' ? /[^\d]/g : /[^\d.]/g;
    event.target.value = value.replace(replacement, '');
}

function handleBinaryInput(event) {
    event.target.value = event.target.value.replace(/[^0-1]/g, '');
}

function validateInput(value, errorMessage, count, notificationId = 'notification') {
    var notificationDiv = document.getElementById(notificationId);

    if (value === '') {
        notificationDiv.innerHTML = errorMessage;
        notificationDiv.style.backgroundColor = '#f44336';
        notificationDiv.style.display = 'block';

        hideSections(count);
        return false;
    } else {
        notificationDiv.style.display = 'none';
        return true;
    }
}

function validateInputToParams(Bool, section) {
    var notificationDiv = document.getElementById('notification');

    if(Bool){
        notificationDiv.style.display = 'none';
        return true;
    }
    else{
        notificationDiv.innerHTML = `Введены неккоректные данные в разделе "${section}"!`;
        notificationDiv.style.backgroundColor = '#f44336';
        notificationDiv.style.display = 'block';
        return false;
    }
}

function hideSections(count) {
    const sections = [
        inputKeyData,
        inputTimeParameters,
        inputIterationParameters,
        inputNodeCoordinates,
        inputControlTimeFunction,
        inputTimeFunction1
    ];

    sections.slice(count).forEach(section => section.style.display = 'none');
}

function validateNumber(value, max, sectionName, section) {
    var errorMessage = `Заполните все поля в разделе "${sectionName}"!`;

    if (!validateInput(value, errorMessage, section)) {
        return false;
    } else {
        return validateInputToParams(value <= max, sectionName);
    }
}

function inputHeadValidation() {
    return validateInput(getElementByIdValue('hed'), 'Введите заголовок!', HEAD_SECTION);
}

function inputKeyDataValidation() {
    var numnp = getElementByIdValue('numnp');
    var negl = getElementByIdValue('negl');
    var negnl = getElementByIdValue('negnl');

    var sectionName = 'Ввод контрольных данных';

    return validateNumber(numnp, 100, sectionName, KEY_DATA_SECTION)
        && validateNumber(negl, 100, sectionName, KEY_DATA_SECTION)
        && validateNumber(negnl, 100, sectionName, KEY_DATA_SECTION);
}

function inputTimeParametersValidation() {
    var ivartime = getElementByIdValue('ivartime');
    var Nste = getElementByIdValue('Nste');
    var Tstart = getElementByIdValue('Tstart');
    var Tfinal = getElementByIdValue('Tfinal');
    var r_initial_delta_t = getElementByIdValue('r_initial_delta_t');
    var r_minimum_delta_t = getElementByIdValue('r_minimum_delta_t');
    var r_maximum_delta_t = getElementByIdValue('r_maximum_delta_t');

    var sectionName = 'Ввод параметра времени';

    return validateNumber(ivartime, 1, sectionName, TIME_PARAMETERS_SECTION)
        && validateNumber(Nste, 1000, sectionName, TIME_PARAMETERS_SECTION)
        && validateNumber(Tstart, 1000, sectionName, TIME_PARAMETERS_SECTION)
        && validateNumber(Tfinal, 1000, sectionName, TIME_PARAMETERS_SECTION)
        && validateNumber(r_initial_delta_t, 1000, sectionName, TIME_PARAMETERS_SECTION)
        && validateNumber(r_minimum_delta_t, 1000, sectionName, TIME_PARAMETERS_SECTION)
        && validateNumber(r_maximum_delta_t, 1000, sectionName, TIME_PARAMETERS_SECTION);
}

function inputIterationParametersValidation() {
    var Isref = getElementByIdValue('Isref');
    var Nutmre = getElementByIdValue('Nutmre');
    var Iequit = getElementByIdValue('Iequit');
    var Itemax = getElementByIdValue('Itemax');
    var Iteopt = getElementByIdValue('Iteopt');
    var Dtol = getElementByIdValue('Dtol');
    var Ftol = getElementByIdValue('Ftol');
    var Etol = getElementByIdValue('Etol');

    var sectionName = 'Ввод параметра времени';

    return validateNumber(Isref, 1000, sectionName, ITERATION_PARAMETERS_SECTION)
        && validateNumber(Nutmre, 1000, sectionName, ITERATION_PARAMETERS_SECTION)
        && validateNumber(Iequit, 1000, sectionName, ITERATION_PARAMETERS_SECTION)
        && validateNumber(Itemax, 1000, sectionName, ITERATION_PARAMETERS_SECTION)
        && validateNumber(Iteopt, 1000, sectionName, ITERATION_PARAMETERS_SECTION)
        && validateNumber(Dtol, 1000, sectionName, ITERATION_PARAMETERS_SECTION)
        && validateNumber(Ftol, 1000, sectionName, ITERATION_PARAMETERS_SECTION)
        && validateNumber(Etol, 1000, sectionName, ITERATION_PARAMETERS_SECTION);
}

function inputNodeCoordinatesValidation() {
    var inputNodeCoordinatesDiv = document.getElementById('inputNodeCoordinates');
    var generatedDivs = inputNodeCoordinatesDiv.querySelectorAll('div.group');
    var sectionName = 'Ввод координат узла';

    for (var i = 0; i < generatedDivs.length; i++) {
        var inputs = generatedDivs[i].querySelectorAll('input');

        for (var j = 1; j < inputs.length; j++) {
            var value = inputs[j].value.trim();

            if(inputs[j].type === 'text'){
                if (!validateNumber(value, 1000, sectionName, NODE_COORDINATES_SECTION)) return false;
            }
            else if (!validateNumber(value, 1, sectionName, NODE_COORDINATES_SECTION)) return false;
                
        }
    }
    return true;
}

function inputControlTimeFunctionValidation() {
    var nlcur = getElementByIdValue('nlcur');
    var Nptm = getElementByIdValue('Nptm');

    var sectionName = 'Линия управления функциями времени';

    return validateNumber(nlcur, 100, sectionName, CONTROL_TIME_FUNCTION_SECTION)
        && validateNumber(Nptm, 100, sectionName, CONTROL_TIME_FUNCTION_SECTION);
}

function inputTimeFunction1Validation(){
    var inputTimeFunction1Div = document.getElementById('inputTimeFunction1');
    var generatedDivs = inputTimeFunction1Div.querySelectorAll('div.group');
    var sectionName = 'Ввод табличных функций времени. Контрольная линия 1';

    for (var i = 0; i < generatedDivs.length; i++) {
        var inputs = generatedDivs[i].querySelectorAll('input');

        for (var j = 1; j < inputs.length; j++) {
            var value = inputs[j].value.trim();

            if (!validateNumber(value, getElementByIdValue('Nptm'), sectionName, TIME_FUNCTION1_SECTION)) {
                return false;
            }
        }
    }
    return true;
}

function toggleVisibility(elementId) {
    var element = document.getElementById(elementId);
    element.style.display = (element.style.display === 'none') ? 'block' : 'block';
}

function inputKeyDataVisibility() {
    if(inputHeadValidation()) toggleVisibility('inputKeyData');
}

function inputTimeParametersVisibility() {
    if(inputHeadValidation() && inputKeyDataValidation()) toggleVisibility('inputTimeParameters')
}

function inputIterationParametersVisibility() {
    if (inputHeadValidation() && inputKeyDataValidation() && inputTimeParametersValidation()) {
        toggleVisibility('inputIterationParameters');
    }
}

function inputNodeCoordinatesVisibility(){
    if(inputHeadValidation() && inputKeyDataValidation() && inputTimeParametersValidation() 
        && inputIterationParametersValidation()){

         generateGroups('inputNodeCoordinates',
            'Ввод координат узла. Формат (i10, 2 i5, 2f20.0)',
            'Узел: ',
            'numnp',
            'inputControlTimeFunctionButton',
            createAndAppendNodeCoordinatesInputs,
            inputControlTimeFunctionVisibility);
        toggleVisibility('inputNodeCoordinates');
        
    }
}

function inputControlTimeFunctionVisibility(){
    if(inputHeadValidation() && inputKeyDataValidation() && inputTimeParametersValidation() 
        && inputIterationParametersValidation() && inputNodeCoordinatesValidation()){

        toggleVisibility('inputControlTimeFunction');
    }
}

function inputTimeFunction1Visibility(){
    if(inputHeadValidation() && inputKeyDataValidation() && inputTimeParametersValidation() 
        && inputIterationParametersValidation() && inputNodeCoordinatesValidation()
        && inputControlTimeFunctionValidation()){
        
        generateGroups('inputTimeFunction1',
            'Ввод табличных функций времени. Контрольная линия 1. Формат (2i5)',
            'Номер функции: ',
            'nlcur',
            'inputTimeFunction2Button',
            createAndAppendTimeFunction1Inputs,
            inputTimeFunction2Visibility);
        toggleVisibility('inputTimeFunction1');
        
    }
}

function inputTimeFunction2Visibility(){
    if(inputHeadValidation() && inputKeyDataValidation() && inputTimeParametersValidation() 
    && inputIterationParametersValidation() && inputNodeCoordinatesValidation()
    && inputControlTimeFunctionValidation() && inputTimeFunction1Validation()){
        toggleVisibility('inputTimeFunction2');

    }
}

document.getElementById('inputKeyDataButton').addEventListener('click', inputKeyDataVisibility);
document.getElementById('inputTimeParametersButton').addEventListener('click', inputTimeParametersVisibility);
document.getElementById('inputIterationParametersButton').addEventListener('click', inputIterationParametersVisibility);
document.getElementById('inputNodeCoordinatesButton').addEventListener('click', inputNodeCoordinatesVisibility);
document.getElementById('inputTimeFunction1Button').addEventListener('click', inputTimeFunction1Visibility);