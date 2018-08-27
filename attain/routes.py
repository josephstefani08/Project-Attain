from flask import Flask, flash, render_template, request, session, redirect, url_for, abort
from attain import app, db, bcrypt, mail
from attain.forms import RegistrationForm, LoginForm, UpdateProfileForm, CreateGoal, UpdateGoal, CompleteGoal, SubmitPasswordResetForm, PasswordResetForm
from attain.models import User, YearGoals
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import secrets
import os
from PIL import Image
from sqlalchemy import and_
from flask_mail import Message


# Home route
@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template("home.html")


# Logout function
@app.route("/logout")
@login_required
def logout():
    # This is just a logout function
    logout_user()
    flash('You were just logged out!', 'success')
    return redirect(url_for('login'))


# Register page
@app.route("/register", methods=['GET', 'POST'])
def register():
    # Figure out if the user is logged in or not. No need for a registered user to register again.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Figure out if the user is logged in or not. No need to double log in
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Locate the user in the database and verify their passsword
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # This is done so that if a user tries to go to a page, they first can log in and are then sent to the page they were trying to access without having to navigate back to it.
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


# This function is from Corey Schafer.
# Using this function to be able to save the profile pictures uploaded by users without issues with images having the same name.
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    # Using _ because not using the first value "f_name"...."throwing away"
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_fn)

    # Resize the image so that it does not take up a lot of room
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    form_picture.save(picture_path)
    return picture_fn


# Profile settings page for the logged in user
@app.route('/profilesettings', methods=['GET', 'POST'])
@login_required
def profilesettings():
    form = UpdateProfileForm()
    # Update the user's information
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.alternative_email.data:
            alt_email = form.alternative_email.data
            current_user.alternative_email = alt_email
        if not form.alternative_email.data:
            current_user.alternative_email = ""
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('profilesettings'))
    elif request.method == 'GET':
        # Show the user's information on the profile page
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.alternative_email.data = current_user.alternative_email
    image_file = url_for('static', filename='profile_pictures/' + current_user.image_file)
    return render_template("profilesettings.html", title='Profile Settings', image_file=image_file, form=form)


# Create a goal
@app.route('/creategoals', methods=['GET', 'POST'])
@login_required
def creategoal():
    form = CreateGoal()
    if form.validate_on_submit():
        goal = YearGoals(title=form.title.data, content=form.content.data, author=current_user, username=current_user.username, measure_success=form.measure_success.data, six_month=form.six_month.data, three_month=form.three_month.data, one_month=form.one_month.data)
        db.session.add(goal)
        db.session.commit()
        flash('Your goal has been created', 'success')
        return redirect(url_for('goals'))
    return render_template("creategoals.html", title='Create A Goal!', form=form)


# Shows a list of goal for the logged in user
# Goals shown are new or in progress
@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    page = request.args.get('page', 1, type=int)
    goals = YearGoals.query.filter(and_(YearGoals.completed == False, YearGoals.username == current_user.username)).paginate(page=page, per_page=5)
    return render_template("goals.html", title='Goals', goals=goals)


# Goal page
@app.route("/goal/<int:goal_id>")
def goal(goal_id):
    goal = YearGoals.query.get_or_404(goal_id)
    return render_template('goal.html', title=goal.title, goal=goal)


# Start a goal
@app.route("/goal/<int:goal_id>/startgoal", methods=['GET', 'POST'])
def start_goal(goal_id):
    goal = YearGoals.query.get_or_404(goal_id)
    if goal.author != current_user:
        abort(403)
    goal.started = True
    goal.start_date = datetime.utcnow()
    db.session.commit()
    flash('Goal has been started.', 'success')
    return redirect(url_for('goals', goal_id=goal.id))


# Update a goal
@app.route("/goal/<int:goal_id>/updategoal", methods=['GET', 'POST'])
@login_required
def update_goal(goal_id):
    goal = YearGoals.query.get_or_404(goal_id)
    if goal.author != current_user:
        abort(403)
    form = UpdateGoal()
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.content = form.content.data
        goal.measure_success = form.measure_success.data
        goal.six_month = form.six_month.data
        goal.three_month = form.three_month.data
        goal.one_month = form.one_month.data
        goal.notes = form.notes.data
        db.session.commit()
        flash('Goal has been updated.', 'success')
        return redirect(url_for('goal', goal_id=goal.id))
    elif request.method == 'GET':
        form.title.data = goal.title
        form.content.data = goal.content
        form.date_created.data = goal.date_created
        form.start_date.data = goal.start_date
        form.measure_success.data = goal.measure_success
        form.six_month.data = goal.six_month
        form.three_month.data = goal.three_month
        form.one_month.data = goal.one_month
        form.notes.data = goal.notes
    return render_template("updategoal.html", title='Update Goal', form=form)


# Mark a goal as complete
@app.route("/goal/<int:goal_id>/complete_a_goal", methods=['GET', 'POST'])
@login_required
def complete_a_goal(goal_id):
    goal = YearGoals.query.get_or_404(goal_id)
    if goal.author != current_user:
        abort(403)
    form = CompleteGoal()
    # Mark the goal as completed
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.notes = form.notes.data
        goal.completed = True
        goal.completed_date = datetime.now()
        db.session.commit()
        flash('Goal has been marked as complete.', 'success')
        return redirect(url_for('goals'))
    elif request.method == 'GET':
        form.title.data = goal.title
    return render_template("complete_a_goal.html", title='Complete Goal', form=form)


#  Delete a goal
@app.route("/goal/<int:goal_id>/delete", methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = YearGoals.query.get_or_404(goal_id)
    if goal.author != current_user:
        abort(403)
    db.session.delete(goal)
    db.session.commit()
    flash('Goal has been deleted.', 'success')
    return redirect(url_for('home'))


# Show the completed goals for the logged in user
@app.route('/completedgoals', methods=['GET', 'POST'])
@login_required
def completedgoals():
    page = request.args.get('page', 1, type=int)
    goals = YearGoals.query.filter(and_(YearGoals.completed == True, YearGoals.username == current_user.username)).paginate(page=page, per_page=5)
    return render_template("completedgoals.html", title='Completed Goals', goals=goals)


@app.route('/reset_password', methods=['GET', 'POST'])
def submit_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SubmitPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        reset_email(user)
        flash('An email has been sent to the email provided.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token. Please reset password again to generate a new email.', 'warning')
        return redirect(url_for('submit_password_reset'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_your_password.html', title='Reset Password', form=form)


def reset_email(user):
    token = user.get_reset_token()
    message = Message('Attain Password Reset', sender='noreplyattain@gmail.com', recipients=[user.email])
    message.body = f'''Click the following link to reset your password.
{url_for('reset_password', token=token, _external=True)}

If you recieved this email in error, please ignore.
'''
    mail.send(message)
