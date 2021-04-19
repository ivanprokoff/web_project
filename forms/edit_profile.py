from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class EditInfo(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    work = StringField('Должность', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    submit = SubmitField('Вперед!')
