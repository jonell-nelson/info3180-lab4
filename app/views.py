import os
from flask import render_template, request, redirect, url_for, flash, session, abort, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash  # Required for password verification
from app import db, login_manager
from app.models import UserProfile
from app.forms import LoginForm

# Define Blueprint
main = Blueprint('main', __name__)

### Routing for your application ###

@main.route('/')
def home():
    return "Hello, Flask!"


@main.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@main.route('/upload', methods=['POST', 'GET'])
def upload():
    form = UploadForm()  # Ensure UploadForm is imported

    if form.validate_on_submit():
        file = form.file.data  # Assuming the form has a 'file' field
        filename = secure_filename(file.filename)
        file.save(os.path.join(Config.UPLOAD_FOLDER, filename))

        flash('File Saved', 'success')
        return redirect(url_for('main.upload'))  # Redirect to upload page

    return render_template('upload.html', form=form)


@main.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():  # Proper form validation
        username = form.username.data
        password = form.password.data

        # Query user by username
        user = db.session.execute(
            db.select(UserProfile).filter_by(username=username)
        ).scalar_one_or_none()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for("main.upload"))  # Redirect to upload page

        flash('Invalid username or password', 'danger')

    return render_template("login.html", form=form)


# user_loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(UserProfile, user_id)


### General Flask Functions ###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'danger')


@main.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    return main.send_static_file(file_name + '.txt')


@main.after_request
def add_header(response):
    """
    Add headers to force latest IE rendering engine or Chrome Frame
    and to prevent caching.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@main.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
