from flask import render_template, url_for, flash, redirect
from DFD2GUI import app
from DFD2GUI.forms import RegistrationForm, LoginForm

@app.route("/",  methods=['POST', 'GET'])
@app.route("/login",  methods=['POST', 'GET'])
def login():
    form = LoginForm()
    return render_template('login.html', title="Login DFD2GUI", form=form)

@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash("Your account has been created", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title="Register DFD2GUI", form=form)