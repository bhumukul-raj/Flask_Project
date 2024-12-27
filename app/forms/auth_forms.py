from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', 
                         validators=[DataRequired(), Length(min=3, max=50)],
                         render_kw={"placeholder": "Enter your username"})
    password = PasswordField('Password', 
                           validators=[DataRequired(), Length(min=6)],
                           render_kw={"placeholder": "Enter your password"})
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', 
                         validators=[DataRequired(), Length(min=3, max=50)],
                         render_kw={"placeholder": "Choose a username"})
    email = EmailField('Email',
                      validators=[DataRequired(), Email()],
                      render_kw={"placeholder": "Enter your email"})
    password = PasswordField('Password',
                           validators=[DataRequired(), Length(min=6)],
                           render_kw={"placeholder": "Choose a password"})
    confirm_password = PasswordField('Confirm Password',
                                   validators=[DataRequired(), EqualTo('password')],
                                   render_kw={"placeholder": "Confirm your password"}) 