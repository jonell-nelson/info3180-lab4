import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm
from app.forms import UploadForm
from app.utils import get_uploaded_images


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Jonell Nelson")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    print(f"Current user: {current_user.username}")  # Debugging
    form = UploadForm()

    if form.validate_on_submit():
        # Get file data and save to your uploads folder
        file = form.photo.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('File Saved', 'success')
        return redirect(url_for('home'))  # Update this to redirect to a route that displays all uploaded image files

    return render_template('upload.html', form=form)

@app.route('/uploads/<filename>')
@login_required
def get_image(filename):
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

@app.route('/files')
@login_required
def files():
    upload_folder = app.config['UPLOAD_FOLDER']
    image_list = get_uploaded_images(upload_folder)
    return render_template('files.html', image_list=image_list)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Get the username and password from the form
        username = form.username.data
        password = form.password.data

        # Query the database for the user
        user = UserProfile.query.filter_by(username=username).first()

        # Debugging: Print the username, hashed password, and plaintext password
        print(f"Username from form: {username}")
        if user:
            print(f"Hashed password from database: {user.password}")
        print(f"Plaintext password from form: {password}")

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            # Log the user in
            login_user(user)
            flash('Login successful!', 'success')

            # Redirect to the "next" page if it exists, otherwise to the upload page
            next_page = request.args.get('next')
            return redirect(next_page or url_for('upload'))
        else:
            # If authentication fails, show an error message
            flash('Incorrect username or password', 'danger')
            return redirect(url_for('login'))

    # Render the login form for GET requests
    return render_template('login.html', form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session

@login_manager.user_loader
def load_user(id):
    print(f"Loading user with ID: {id}")  # Debugging
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404