from flask import render_template, request, redirect, url_for, session, abort

from app import app, database as db


def check_user():
    return "user_id" in session


@app.route('/test/<int:test_id>/')
def test(test_id):
    if not check_user():
        return redirect(url_for('login', locate='test', test_id=test_id))
    test_name = db.get_test_name_by_id(test_id)
    if test_name is None:
        return render_template('base.html')
    questions = db.get_question_by_test_id(test_id)
    user_name = db.user_name_by_test_id(test_id)
    return render_template('test.html', questions=questions, test_name=test_name,
                           user_name=user_name, test_id=test_id, user=db.get_user_name_by_id(session['user_id']))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = db.login(request.form['login'], request.form['password'])
        if user_id is not None:
            session['user_id'] = user_id
            redirect_kwargs = {key: value for key, value in request.args.items()}
            return redirect(url_for(redirect_kwargs.pop('locate'), **redirect_kwargs))
        else:
            return render_template('login.html', login_response='Неудачная попытка входа')
    return render_template('login.html')


@app.route('/logout/')
def logout():
    if check_user():
        session.pop("user_id")
    return redirect(url_for('login', locate='profile'))


@app.route('/profile/')
def profile():
    if not check_user():
        return redirect(url_for('login', locate='profile'))

    return render_template('profile.html',
                           user=db.get_user_name_by_id(session['user_id']),
                           tests=db.get_tests_by_user_id(session['user_id']))


@app.route('/create/', methods=['GET', 'POST'])
def create():
    if not check_user():
        return redirect(url_for('login', locate=f'create'))

    if request.method == 'POST':
        db.create_test(session['user_id'], request.form.items())
        return redirect(url_for('profile'))

    return render_template('create_test.html', user=db.get_user_name_by_id(session['user_id']))


@app.route('/statistic/<int:test_id>/')
def statistic(test_id):
    if not check_user():
        return redirect(url_for('login', locate=f'/edit/{test_id}'))

    if not db.test_permission(session['user_id'], test_id):
        abort(404)

    return render_template('statistic.html',
                           user=db.get_user_name_by_id(session['user_id']),
                           tryings=db.get_tryings_by_test_id(test_id),
                           avg_result=db.get_avg_results(test_id))


@app.route('/save/', methods=['GET', 'POST'])
def save():
    if not check_user():
        return redirect(url_for('login', locate='main'))

    if request.method != 'POST':
        return abort(404)

    if db.test_permission(session['user_id'], request.form['test_id']):
        return redirect(url_for('profile'))

    trying_id = db.save_trying(session['user_id'], request.form.items())
    return redirect(url_for('results', trying_id=trying_id))


@app.route('/results/', methods=['GET'])
def results():
    if not (check_user() or not (not db.test_permission(session['user_id'], db.get_test_id_by_trying_id(
            request.args['trying_id'])) or not db.trying_permission(session['user_id'], request.args['trying_id']))):
        abort(404)

    else:
        return render_template('result.html',
                               answers=db.get_trying_answers(request.args['trying_id']),
                               result=db.get_result(request.args['trying_id']),
                               user=db.get_user_name_by_id(session['user_id']))


@app.route('/delete/', methods=['GET'])
def delete():
    if not check_user() or not db.test_permission(session['user_id'], request.args['test_id']):
        abort(404)

    db.delete_test(request.args['test_id'])
    return redirect(url_for('profile'))


@app.route('/')
def home():
    user = db.get_user_name_by_id(session['user_id']) if check_user() else None
    return render_template('home.html', user=user)
