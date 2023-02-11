let questions = 1
let answers = []

function create_question() {
    let question = $(`
    <li class='question'>
        <input class="question-text" name='question_text ${questions}' placeholder='Текст вопроса'>
        <button class="btn-test" type='button' onclick="create_answer(${questions})">Добавить ответ</button>
        <ul id='answers_${questions}'></ul>
    </li>
    `);

    $('#questions').append(question);
    questions++;
    answers.push(1)
}

function create_answer(id) {
    let answer = $(`
    <li class="answer">
            <input class="answer-name" name='answer_text ${id} ${answers[id - 1]}' placeholder='Текст ответа'>
            <input name='answer_is_true ${id}' type='radio' value='${answers[id - 1]}' checked>
            <label for="answer_is_true ${id}">Верный</label>
    </li>
    `);
    $(`#answers_${id}`).append(answer);
    answers[id - 1]++;
}
