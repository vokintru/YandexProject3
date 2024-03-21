from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NewPostForm(FlaskForm):
    text = StringField('Квакание', validators=[DataRequired()])
    submit = SubmitField('Квакнуть')

