from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, TextAreaField, FileField
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
    name = StringField('Имя', validators=[DataRequired()])
    username = StringField('Юзернейм', validators=[DataRequired()])
    bio = TextAreaField('Биография', validators=[DataRequired()])
    avatar = FileField('Аватарка')
    submit = SubmitField('Сохранить')

    def __repr__(self):
        return f"name: {self.name}; username: {self.username}; bio: {self.bio}; avatar: {self.avatar}; "
