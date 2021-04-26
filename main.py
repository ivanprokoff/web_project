from flask import Flask, render_template, redirect, request, abort, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.users import User
from data.items import Items
from forms.user import LoginForm, RegisterForm, FeedbackForm
from forms.edit_profile import EditInfo
from data import db_session
from flask_restful import Api
from forms.lists import GetTableName, AddNewItem
import smtplib
import pandas as pd
import sqlite3

from data import users_resources


app = Flask(__name__)
api = Api(app)
api.add_resource(users_resources.UserResource, '/api/users/<int:user_id>')
api.add_resource(users_resources.UserListResource, '/api/users')


login_manager = LoginManager()
login_manager.init_app(app)

with open('secret/secret_key.txt') as key_file:
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
    return render_template('first.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(f"/{current_user.username}")
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
            phone_number=form.phone_number.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        with open('secret/mail.txt') as mail_file:
            login_password = mail_file.readlines()
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login(login_password[0].strip(), login_password[1].strip())
        smtpObj.sendmail(login_password[0].strip(), form.email.data, "Thank you for choosing our service!")
        smtpObj.quit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        message = form.message.data
        message = current_user.username + ': ' + message
        print(message)
        with open('secret/mail.txt') as mail_file:
            login_password = mail_file.readlines()
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login(login_password[0].strip(), login_password[1].strip())
        smtpObj.sendmail(login_password[0].strip(), login_password[0].strip(), message)
        smtpObj.quit()
        return redirect('/')
    return render_template('feedback.html', form=form, title='Обратная свзяь')


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
@app.route('/<username>/create', methods=['GET', 'POST'])
def create(username):
    form = GetTableName()
    if form.validate_on_submit():
        tablename = form.tablename.data
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        try:
            if user.all_lists:
                if tablename in user.all_lists:
                    return render_template('get_table_name.html', title='Создать новый лист',
                                           form=form,
                                           message="Такой лист уже есть")
                else:
                    if user.all_lists is not None:
                        user.all_lists = user.all_lists + ',' + tablename
                        db_sess.commit()
                    elif user.all_lists is None:
                        user.all_lists = tablename
                        db_sess.commit()
                return redirect(f'/{username}/list/{tablename}')
            else:
                user.all_lists = tablename
                db_sess.commit()
                return redirect(f'/{username}/list/{tablename}')
        except Exception as ex:
            print(ex)
            return abort(404)
    return render_template('get_table_name.html', title='Создать новый лист', form=form)


@login_required
@app.route('/<username>/list/<list_name>', methods=['GET', 'POST'])
def create_new_list(username, list_name):
    summary = 0
    db_sess = db_session.create_session()
    items = db_sess.query(Items).filter(Items.list_name == list_name)
    for i in items:
        summary = summary + (i.price * int(i.multiplier) * int(i.count))
    return render_template('new_list.html', title=f'{list_name}', items=items, name=list_name, summary=summary)


@login_required
@app.route('/<username>/list/<tablename>/add', methods=['GET', 'POST'])
def add(username, tablename):
    form = AddNewItem()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        item = Items()
        item.thing = form.thing.data
        item.count = form.count.data
        item.multiplier = form.multiplier.data
        item.price = form.price.data
        item.description = form.description.data
        item.list_name = tablename
        current_user.item.append(item)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/{username}/list/{tablename}')
    return render_template('add_item.html', form=form)


@login_required
@app.route('/<username>/list/<tablename>/delete', methods=['GET', 'POST'])
def delete_list(username, tablename):
    db_sess = db_session.create_session()
    items = db_sess.query(Items).filter(Items.list_name == tablename)
    for i in items:
        db_sess.delete(i)
    db_sess.commit()
    user = db_sess.query(User).filter(User.username == current_user.username).first()
    user_lists = user.all_lists.split(',')
    for i in user_lists:
        if i == tablename:
            user_lists.remove(i)
    if user_lists:
        user_lists = ','.join(user_lists)
    else:
        user_lists = '_'
    user.all_lists = user_lists
    db_sess.commit()
    return redirect(f'/{username}')


@login_required
@app.route('/<username>/list/<string:tablename>/download', methods=['GET', 'POST'])
def download(username, tablename):
    cnx = sqlite3.connect('db/data.db')
    df = pd.read_sql_query("SELECT * FROM items", cnx)
    df.to_excel(f'xlsx/{tablename}.xlsx')
    return send_from_directory(f'xlsx', f'{tablename}.xlsx')


@login_required
@app.route('/<username>/my_lists')
def lists(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()
    try:
        all_lists = user.all_lists.split(',')
        if '_' in all_lists:
            all_lists.remove('_')
    except Exception:
        all_lists = None
    return render_template('lists.html', items=all_lists)


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    app.run()
