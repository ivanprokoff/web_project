from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.users import User
from forms.user import LoginForm, RegisterForm
from forms.edit_profile import EditInfo
from data import db_session

import smtplib


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

with open('secret_key.txt') as key_file:
    key = key_file.read()
app.config['SECRET_KEY'] = key
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db_session.global_init('db/data.db')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def base():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_check.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, pass_=True,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, pass_=True,
                                   message="Такой пользователь уже есть")
        user = User(
            username=form.username.data,
            name=form.name.data,
            surname=form.surname.data,
            work=form.work.data,
            email=form.email.data,
            phone_number=form.phone_number.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        with open('mail.txt') as mail_file:
            login_password = mail_file.readlines()
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login(login_password[0].strip(), login_password[1].strip())
        smtpObj.sendmail(login_password[0].strip(), form.email.data, "Thank you for choosing our service!")
        smtpObj.quit()
        print('Письмо отправлено')
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/faq')
def faq():
    return render_template('')


@login_required
@app.route('/<username>')
def account(username):
    return render_template('account.html')


@login_required
@app.route('/<username>/edit_profile', methods=['GET', 'POST'])
def edit_profile(username):
    username = username
    form = EditInfo()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()
    if request.method == "GET":
        if user:
            form.username.data = user.username
            form.name.data = user.name
            form.surname.data = user.surname
            form.work.data = user.work
            form.email.data = user.email
            form.phone_number.data = user.phone_number
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        print(1)
        user.username = form.username.data
        user.name = form.name.data
        user.surname = form.surname.data
        user.work = form.work.data
        user.email = form.email.data
        user.phone_number = form.phone_number.data
        db_sess.commit()
        new_username = form.username.data
        return redirect(f'/{new_username}')
    return render_template('edit_account.html',
                           title='Редактирование профиля',
                           form=form)


@login_required
@app.route('/<username>/create')
def create_new_list(username):
    return render_template('new_list.html')


@login_required
@app.route('/<username>/lists')
def lists(username):
    return render_template('lists.html')


@login_required
@app.route('/settings')
def settings():
    return render_template('settings.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
