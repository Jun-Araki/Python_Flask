from wtforms import Form, HiddenField, RadioField, StringField
from wtforms.validators import InputRequired, Length


class RateForm(Form):
    user_name = HiddenField("user_name")
    restaurant = StringField(
        "restaurant", validators=[InputRequired(), Length(min=1, max=50)]
    )
    rate = RadioField(
        "radio", choices=[1, 2, 3, 4, 5], default=3, validators=[InputRequired()]
    )


class YesOrNoForm(Form):
    user_name = HiddenField("user_name")
    value = RadioField(
        "radio", choices=["Yes", "No"], default="Yes", validators=[InputRequired()]
    )
