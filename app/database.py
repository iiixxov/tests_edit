import sqlite3


def sql_exec(sql: str):
    connection = sqlite3.connect('form.sqlite')
    cursor = connection.cursor()
    result = cursor.execute(sql)
    connection.commit()
    return result


def create_user(name: str, password: str) -> None:
    sql_exec(f"""
          INSERT INTO user (name, password)
          VALUES ('{name}', '{password}')
    """)


def create_test(user_id: int, request_post) -> None:
    for name, value in request_post:
        name = name.split()[0]
        if name == 'test_name':
            sql_exec(f"INSERT INTO test (user_id, test_name) VALUES ('{user_id}', '{value}')")
        elif name == 'question_text':
            sql_exec(f"""
                INSERT INTO test_question (test_id, question_text) VALUES
                ((SELECT test_id FROM test ORDER BY 1 DESC LIMIT 1), '{value}')
            """)
        elif name == 'answer_text':
            sql_exec(f"""
                INSERT INTO test_answer (test_question_id, answer_text) VALUES
                    ((SELECT test_question_id FROM test_question ORDER BY 1 DESC LIMIT 1), '{value}')
            """)
        elif name == 'answer_is_true':
            sql_exec(f"""
                INSERT INTO true_answer (test_answer_id) VALUES
                ((SELECT test_answer_id FROM test_answer ORDER BY 1 DESC LIMIT 1))
            """)


def get_question_by_test_id(test_id: int) -> list:
    test = []
    for n, (test_question_id, question_text,) in enumerate(sql_exec(f"""
        SELECT test_question_id, question_text
        FROM test_question
        WHERE test_id={test_id}
        ORDER BY test_question_id
    """)):
        question = {"n": n, 'id': test_question_id,
                    "text": question_text, "answers": []}
        for (answer, id) in sql_exec(f"""
            SELECT answer_text, test_answer_id
            FROM test_answer
            WHERE test_question_id = {test_question_id}
        """):
            question["answers"].append({'text': answer, 'id': id})
        test.append(question)
    return test


def get_test_name_by_id(test_id: int) -> str:
    for (name,) in sql_exec(f"SELECT test_name FROM test WHERE test_id = {test_id}"):
        return name


def user_name_by_test_id(test_id: int) -> str:
    for (name,) in sql_exec(f"SELECT user.name FROM user"
                         f" JOIN test ON user.user_id = test.user_id WHERE test_id='{test_id}'"):
        return name


def login(name: str, password: str) -> int:
    """:return: user_id: int"""
    for (user_id,) in sql_exec(f"""
        SELECT user_id FROM user WHERE name='{name}' AND password='{password}'
    """):
        return user_id


def get_user_name_by_id(user_id) -> str:
    for (name,) in sql_exec(f"""
        SELECT name FROM user WHERE user_id='{user_id}'
    """):
        return name


def get_tests_by_user_id(user_id):
    for (test_id, name) in sql_exec(f"""
        SELECT test_id, test_name FROM test
        WHERE user_id='{user_id}'
        ORDER BY test_id DESC 
    """):
        yield {'test_id': test_id, 'name': name}


def test_permission(user_id, test_id) -> bool:
    for (test_id,) in sql_exec(f"""
        SELECT test_id FROM test WHERE user_id='{user_id}' AND test_id='{test_id}'
    """):
        return test_id is not None


def save_trying(user_id, request_post) -> int:
    for key, value in request_post:
        if key == 'test_id':
            sql_exec(f"""
                INSERT INTO trying (user_id, test_id) VALUES ('{user_id}', '{value}')
            """)
        else:
            sql_exec(f"""
                INSERT INTO trying_answer (trying_id, test_question_id, test_answer_id) VALUES
                ((SELECT trying_id FROM trying ORDER BY 1 DESC LIMIT 1),
                {key.split()[1]}, {value if 'radio' in key else key.split()[2]})
            """)
    for (trying_id,) in sql_exec('SELECT trying_id FROM trying ORDER BY 1 DESC LIMIT 1'):
        return trying_id


def get_trying_answers(trying_id):
    for (question_text, answer_text, is_true) in sql_exec(f"""
        SELECT 
        question_text, 
        answer_text,
        CASE 
            WHEN trying_answer.test_answer_id IN 
                (SELECT test_answer_id FROM true_answer)
            THEN 1
            ELSE 0
        END
        FROM trying_answer
        JOIN trying t on trying_answer.trying_id = t.trying_id
        JOIN test_answer ta on ta.test_answer_id = trying_answer.test_answer_id
        JOIN test_question tq on tq.test_question_id = ta.test_question_id
        WHERE t.trying_id = '{trying_id}'
    """):
        yield {'question_text': question_text, 'answer_text': answer_text, 'is_true': is_true}


def get_result(trying_id):
    for (true_answers, all_answers) in sql_exec(F"""
        SELECT 
            (SELECT COUNT(trying_answer.test_answer_id) FROM trying_answer
                JOIN true_answer ta on trying_answer.test_answer_id = ta.test_answer_id
                WHERE trying_answer.trying_id = '{trying_id}'),
            COUNT(test_question_id)
        FROM test_question
        WHERE test_id = (SELECT test_id FROM trying WHERE trying_id = '{trying_id}')
    """):
        return {'true': true_answers, 'all': all_answers}


def delete_test(test_id):
    sql_exec(f"DELETE FROM test WHERE test_id='{test_id}'")


def get_tryings_by_test_id(test_id):
    for (user_name, trying_id) in sql_exec(f"""
        SELECT u.name, trying_id FROM trying
        JOIN user u on trying.user_id = u.user_id
        WHERE test_id = '{test_id}'
    """):
        yield {'user_name': user_name, 'trying_id': trying_id, **get_result(trying_id)}


def trying_permission(user_id, trying_id) -> bool:
    for (trying_id,) in sql_exec(f"""
        SELECT trying_id FROM trying WHERE user_id='{user_id}' AND test_id='{trying_id}'
    """):
        return trying_id is not None


def get_test_id_by_trying_id(trying_id):
    for (test_id,) in sql_exec(f"SELECT test_id FROM trying WHERE trying_id='{trying_id}'"):
        return test_id


def get_avg_results(test_id):
    for (avg_true_answers, all_question) in sql_exec(f"""
        SELECT 
            ROUND(CAST(COUNT(true_answer.test_answer_id) AS FLOAT) / COUNT(DISTINCT u.user_id), 1),
            (SELECT COUNT(test_question_id) FROM test_question WHERE test_id = '{test_id}')
        FROM true_answer
        JOIN test_answer ta on true_answer.test_answer_id = ta.test_answer_id
        JOIN trying_answer t on ta.test_answer_id = t.test_answer_id
        JOIN trying t2 on t.trying_id = t2.trying_id
        JOIN user u on t2.user_id = u.user_id
        WHERE t2.test_id = '{test_id}'
    """):
        return {'avg': avg_true_answers, 'all': all_question}


