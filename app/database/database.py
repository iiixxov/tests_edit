import sqlite3


def _exec(sql, values=None):
    connection = sqlite3.connect('app/database/forms.sqlite')
    cursor = connection.cursor()
    if values is None:
        return cursor.execute(sql)
    return cursor.executemany(sql, values)


def create_user(name="Пользователь") -> None:
    _exec(f"""
          INSERT INTO user (name)
          VALUES (?)
    """, [[name]])


def create_test(user_id, request_post):
    result = {'test_name': '', 'questions': []}
    for key, value in request_post:
        if key == 'test_name':
            result['test_name'] = value
        elif key.split()[0] == 'question_text':
            result['questions'].append({'multi': False, 'text': value, 'answers': []})
        elif key.split()[0] == 'multi_question_text':
            result['questions'].append({'multi': True, 'text': value, 'answers': []})
        elif key.split()[0] == 'answer_text':
            result['questions'][-1]['answers'].append({'text': value, 'is_true': False})
        elif key.split()[0] == 'answer_is_true':
            result['questions'][-1]['answers'][-1]['is_true'] = True
    return result


def create_question(test_id, multiple_true=False, text="") -> None:
    _exec(f"""
        INSERT INTO test_question (test_id, multiple_true_variants, question_text)
        VALUES (?, ?, ?)
    """, [[test_id, multiple_true, text]])


def create_answer(question_id, is_true=False, text="") -> None:
    _exec(f"""
            INSERT INTO test_question (test_question_id, is_true_variant, answer_text)
            VALUES (?, ?, ?)
        """, [[question_id, is_true, text]])


def get_question_by_test_id(test_id) -> list:
    test = []
    for n, (test_question_id, multiple_true_variant, question_text,) in enumerate(_exec(f"""
        SELECT test_question_id, multiple_true_variant, question_text
        FROM test_question
        WHERE test_id={test_id}
        ORDER BY test_question_id
    """)):
        question = {"n": n, "multiple": multiple_true_variant, "text": question_text, "answers": []}
        for (answer,) in _exec(f"""
            SELECT answer_text
            FROM test_answer
            WHERE test_question_id = {test_question_id}
        """):
            question["answers"].append(answer)
        test.append(question)
    return test


def get_test_name_by_id(test_id) -> str:
    for (name,) in _exec(f"SELECT test_name FROM test WHERE test_id = {test_id}"):
        return name


def login(name, password) -> int:
    for (user_id,) in _exec(f"""
        SELECT user_id FROM user WHERE name='{name}' AND password='{password}'
    """):
        return user_id


def get_user_name_by_id(user_id) -> str:
    for (name,) in _exec(f"""
        SELECT name FROM user WHERE user_id='{user_id}'
    """):
        return name


def get_tests_by_user_id(user_id):
    for (test_id, name) in _exec(f"""
        SELECT test_id, test_name FROM test
        WHERE user_id='{user_id}'
    """):
        yield {'test_id': test_id, 'name': name}


def test_permission(user_id, test_id) -> bool:
    for (test_id, ) in _exec(f"""
        SELECT test_id FROM test WHERE user_id='{user_id}' AND test_id='{test_id}'
    """):
        return test_id is not None
