from flask import render_template, url_for, flash, redirect

from DFD2GUI import app

@app.route("/")
@app.route("/login")
def login():
    return render_template('login.html', title="Login DFD2GUI")

@app.route("/register")
def register():
    return render_template('register.html')