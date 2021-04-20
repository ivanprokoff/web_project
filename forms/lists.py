from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class GetTableName(FlaskForm):
    tablename = StringField('Введите название нового листа', validators=[DataRequired()])
    submit = SubmitField('Далее')


class AddNewItem(FlaskForm):
    thing = StringField('Наименование', validators=[DataRequired()])
    count = IntegerField('Количество', validators=[DataRequired()])
    multiplier = IntegerField('Множитель (на сколько человек, по умолчанию 1)', validators=[DataRequired()])
    price = IntegerField('Цена за одну шт (в рублях)', validators=[DataRequired()])
    description = StringField('Описание (опционально)', validators=[])
    submit = SubmitField('Добавить')
