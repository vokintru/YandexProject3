from flask_wtf import FlaskForm
from wtforms import SubmitField, URLField, FileField
from wtforms.validators import DataRequired


class URLCutForm(FlaskForm):
    text = URLField('Сократить ссылку', validators=[DataRequired()])
    submit = SubmitField('Выполнить')


class IMGStock(FlaskForm):
    file = FileField('Прикрепить файл', validators=[DataRequired()])
    submit = SubmitField('Выполнить')
