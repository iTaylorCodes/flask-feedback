from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired


class RegisterUserForm(FlaskForm):
    """Form for registering a new user."""

    username = StringField("Username", validators=[InputRequired(message="Enter a username")])
    password = PasswordField("Password", validators=[InputRequired(message="Enter a password")])
    email = StringField("Email Address", validators=[InputRequired(message="Enter an email address")])
    first_name = StringField("First Name", validators=[InputRequired(message="Enter a first name")])
    last_name = StringField("Last Name", validators=[InputRequired(message="Enter a last name")])

class LoginForm(FlaskForm):
    """Form for logging in an existing user."""

    username = StringField("Username", validators=[InputRequired(message="Enter a username")])
    password = PasswordField("Password", validators=[InputRequired(message="Enter a password")])

class FeedbackForm(FlaskForm):
    """Form for adding feedback."""

    title = StringField("Feedback Title", validators=[InputRequired(message="Enter a title for this feedback")])
    content = StringField("Content", validators=[InputRequired(message="Enter feedback description")])