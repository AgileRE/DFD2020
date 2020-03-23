from flask import render_template, url_for, flash, redirect, request
from DFD2GUI import app, db
from DFD2GUI.forms import RegistrationForm, LoginForm, UploadDFDFileForm
from DFD2GUI.models import User, Project
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from datetime import date
from itertools import count
import os

def activate_link(page):
    active_link = {'dashboard':'', 'project-list':'', 'new-project':''}
    active_link[page] = 'active'
    return active_link

@app.route("/", methods=["POST", "GET"])
@app.route("/login",  methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
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
        return redirect(url_for('login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Add user to database
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        # Add user's folder
        directory = form.email.data
        parent_dir = os.path.join(app.root_path, "user_project")
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)

        # Redirect to login
        flash("Your account has been created", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    projects = {"latest": "", "recent":""}
    # Latest Project Query
    projects["latest"] = Project.query.filter_by(user_id=current_user.id).order_by(Project.id).limit(5)
    
    # Recent Project Query
    projects["recent"] = Project.query.filter_by(user_id=current_user.id).order_by(Project.date_accessed).limit(5)

    return render_template('dashboard.html', title="Dashboard", active_link=activate_link('dashboard'), projects=projects)

@app.route("/project-list")
@login_required
def project_list():
    project_list = Project.query.filter_by(user_id=current_user.id).order_by(Project.id)
    project_list = list(enumerate(project_list, 1))
    return render_template('project_list.html', title="Project list", active_link=activate_link('project-list'), projects=project_list)

@app.route("/new-project", methods=["POST", "GET"])
@login_required
def new_project():
    form = UploadDFDFileForm()
    if form.validate_on_submit():
        # Create Directory Project
        path = os.path.join(app.root_path, "user_project", current_user.email, form.project_name.data)
        os.mkdir(path)
        os.mkdir(os.path.join(path, "GUI"))

        # Add to Database
        project = Project(project_name=form.project_name.data, user_id=current_user.id)
        db.session.add(project)
        db.session.commit()

        return redirect(url_for("dashboard"))
    else:
        print(form.errors)
    return render_template('new_project.html', title="New Project",form=form ,active_link=activate_link('new-project'))

@app.route("/add-entity", methods=["POST", "GET"])
@login_required
def add_entity():
    return render_template('add_entity.html', title="Add Entity" ,active_link=activate_link('new-project'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))