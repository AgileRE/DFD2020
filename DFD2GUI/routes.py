from flask import render_template, url_for, flash, redirect, request
from DFD2GUI import app, db
from DFD2GUI.forms import RegistrationForm, LoginForm
from DFD2GUI.models import User, Project
from flask_login import login_user, current_user, logout_user, login_required

active_link = {'dashboard':'', 'project-list':'', 'upload-dfd':''}

@app.route("/login",  methods=['POST', 'GET'])
@app.route("/",  methods=['POST', 'GET'])
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
            login_user(user)
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
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    active_link['dashboard'] = 'active'
    return render_template('dashboard.html', title="Dashboard", active_link=active_link)

@app.route("/project-list")
@login_required
def project_list():
    return "Ini list project"
    # return render_template('dashboard.html', title="Dashboard")

@app.route("/upload-dfd")
@login_required
def upload_dfd():
    return "Ini upload DFD"
    # return render_template('dashboard.html', title="Dashboard")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))