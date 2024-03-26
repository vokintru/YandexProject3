from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EditForm(FlaskForm):
    username = StringField('Имя Пользователя', validators=[DataRequired()])
    name = StringField('Имя Аккаунта', validators=[DataRequired()])
    bio = TextAreaField('Биография', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
