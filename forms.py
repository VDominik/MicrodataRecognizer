from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.widgets import TextArea

class TextForm(FlaskForm):
    text = StringField('Vložte svoj text', widget=TextArea())
    submit = SubmitField('Pridať microdata')




