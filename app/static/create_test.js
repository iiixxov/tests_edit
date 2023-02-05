let questions = 1
let answers = []

function create_question() {
    let question = $(`
    <li class='question'>
        <input name='question_text ${questions}' placeholder='Текст вопроса'>
        <button type='button' onclick="create_answer(${questions})">Добавить ответ</button>
        <ul id='answers_${questions}'></ul>
    </li>
    `);

    $('#questions').append(question);
    questions++;
    answers.push(1)
}

function create_answer(id) {
    let answer = $(`
    <li>
            <input name='answer_text ${id} ${answers[id - 1]}' placeholder='Текст ответа'>
            Верный:
            <input name='answer_is_true ${id}' type='radio' value='${answers[id - 1]}'>
    </li>
    `);
    $(`#answers_${id}`).append(answer);
    answers[id - 1]++;
}

function create_m_question() {
    let question = $(`
    <li class='question'>
        <input name='multi_question_text ${questions}' placeholder='Текст вопроса'>
        <button type='button' onclick="create_m_answer(${questions})">Добавить ответ</button>
        <ul id='answers_${questions}'></ul>
    </li>
    `);

    $('#questions').append(question);
    questions++;
    answers.push(1)
}

function create_m_answer(id) {
    let answer = $(`
    <li>
            <input name='answer_text ${id} ${answers[id - 1]}' placeholder='Текст ответа'>
            Верный:
            <input name='answer_is_true ${id} ${answers[id - 1]}' type='checkbox'>
    </li>
    `);
    $(`#answers_${id}`).append(answer);
    answers[id - 1]++;
}
