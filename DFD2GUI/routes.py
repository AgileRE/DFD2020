from flask import render_template, url_for, flash, redirect
from DFD2GUI import app, db
from DFD2GUI.forms import RegistrationForm, LoginForm
from DFD2GUI.models import User, Project

@app.route("/",  methods=['POST', 'GET'])
@app.route("/login",  methods=['POST', 'GET'])
def login():
    form = LoginForm()
    return render_template('login.html', title="Login DFD2GUI", form=form)

@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title="Register DFD2GUI", form=form)