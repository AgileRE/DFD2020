from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from DFD2GUI import app
from DFD2GUI.models import User
import os

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')

class RegistrationForm(FlaskForm):
    name = StringField('Name',
                        validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')
            
class UploadDFDFileForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    submit = SubmitField('Upload')

    def validate_project_name(self, project_name):
        path = os.path.join(app.root_path, "user_project", current_user.email)
        lis_dir = os.listdir(path)
        if project_name.data in lis_dir:
            raise ValidationError('This project name has been used. Please choose a different name')