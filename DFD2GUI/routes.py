from flask import render_template, url_for, flash, redirect, request
from DFD2GUI import app, db
from DFD2GUI.forms import RegistrationForm, LoginForm, UploadDFDFileForm
from DFD2GUI.models import User, Project
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os

def activate_link(page):
    active_link = {'dashboard':'', 'project-list':'', 'upload-dfd':''}
    active_link[page] = 'active'
    return active_link

@app.route("/", methods=["POST", "GET"])
@app.route("/login",  methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    print("email:",form.email.data)
    print("password:",form.password.data)
    print()
    print(form.email.errors)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(form.email.data, form.password.data)
        if user and form.password.data == user.password:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash("Your email or password is wrong", "danger")
    return render_template('login.html', title="Login", form=form)

@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Add user to database
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        # Add user's folder
        directory = form.email.data
        parent_dir = "DFD2GUI/user_project"
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)

        # Redirect to login
        flash("Your account has been created", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html', title="Dashboard", active_link=activate_link('dashboard'))

@app.route("/project-list")
@login_required
def project_list():
    return render_template('project_list.html', title="Project list", active_link=activate_link('project-list'))

@app.route("/upload-dfd", methods=["POST", "GET"])
@login_required
def upload_dfd():
    form = UploadDFDFileForm()
    if form.validate_on_submit():
        f = form.dfd_file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.root_path, filename
        ))
        return redirect(url_for("dashboard"))
    else:
        print(form.errors)
    return render_template('upload_dfd.html', title="Upload DFD",form=form ,active_link=activate_link('upload-dfd'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))