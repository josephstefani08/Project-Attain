from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from attain.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms_components import read_only


class RegistrationForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired(), Length(min=2, max=60)])
    lastname = StringField('Last name', validators=[DataRequired(), Length(min=2, max=60)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Validate the user's input information to ensure it is not already taken
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired(), Length(min=2, max=60)])
    lastname = StringField('Last name', validators=[DataRequired(), Length(min=2, max=60)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    alternative_email = StringField('Alternative email')
    joined_date = StringField('Joined date', validators=[DataRequired()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    # Validate the user's input information to ensure it is not already taken
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists.')


    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered.')


    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        read_only(self.joined_date)


class CreateGoal(FlaskForm):
    title = StringField('Goal', validators=[DataRequired(), Length(min=2, max=60)])
    content = TextAreaField('Your why', validators=[DataRequired()])
    measure_success = TextAreaField('Measure of success', validators=[DataRequired(), Length(min=2, max=1500)])
    six_month = TextAreaField('Six month target', validators=[DataRequired(), Length(min=2, max=1500)])
    three_month = TextAreaField('Three month target', validators=[DataRequired(), Length(min=2, max=1500)])
    one_month = TextAreaField('One month target', validators=[DataRequired(), Length(min=2, max=1500)])
    date_created = DateField('Date created')
    started = BooleanField('Started')
    start_date = DateField('Start date')
    submit = SubmitField('Create')


class UpdateGoal(FlaskForm):
    title = StringField('Goal', validators=[DataRequired(), Length(min=2, max=60)])
    content = TextAreaField('Your why', validators=[DataRequired()])
    measure_success = TextAreaField('Measure of success', validators=[DataRequired(), Length(min=2, max=1500)])
    six_month = TextAreaField('Six month target', validators=[DataRequired(), Length(min=2, max=1500)])
    three_month = TextAreaField('Three month target', validators=[DataRequired(), Length(min=2, max=1500)])
    one_month = TextAreaField('One month target', validators=[DataRequired(), Length(min=2, max=1500)])
    date_created = DateField('Date created')
    started = BooleanField('Started')
    start_date = DateField('Start date')
    notes = TextAreaField('Notes', validators=[DataRequired(), Length(min=2, max=2500)])
    submit = SubmitField('Update')
    

class CompleteGoal(FlaskForm):
    title = StringField('Goal', validators=[DataRequired(), Length(min=2, max=60)])
    notes = TextAreaField('Final notes')
    submit = SubmitField('Complete Goal')


class SubmitPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('That email address is not registered to an account. Please check email and try again.')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')
