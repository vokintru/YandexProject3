from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class NewPostForm(FlaskForm):
    text = TextAreaField('Квакание', validators=[DataRequired()])
    file = FileField('Прикрепить жабфайл')
    submit = SubmitField('Квакнуть')


class EditPostForm(FlaskForm):
    text = TextAreaField('Квакание', validators=[DataRequired()])
    submit = SubmitField('Квакнуть')


class RepostForm(FlaskForm):
    text = TextAreaField('Реквакание', validators=[DataRequired()])
    submit = SubmitField('Реквакнуть')


class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Квакнуть')
