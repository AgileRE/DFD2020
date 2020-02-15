from flask import render_template, url_for, flash, redirect

from DFD2GUI import app

@app.route("/")
def index():
    return "<h1>halo </h1>"