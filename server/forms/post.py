from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class NewPostForm(FlaskForm):
    text = TextAreaField('Квакание', validators=[DataRequired()])
    submit = SubmitField('Квакнуть')


class RepostForm(FlaskForm):
    text = TextAreaField('Реквакание', validators=[DataRequired()])
    submit = SubmitField('Реквакнуть')

