from wtforms import (Form, StringField, TextAreaField, 
                     SelectField, validators)

class ItemForm(Form):
    name = StringField('Name', [
        validators.DataRequired(),
        validators.Length(min=4, max=50)
    ])
    description = TextAreaField('Description', [
        validators.DataRequired(),
        validators.Length(max=1500)
    ])