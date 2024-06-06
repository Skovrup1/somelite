from flask import Blueprint, render_template, redirect, url_for, request#, flash
from werkzeug.security import generate_password_hash#, check_password_hash
#from app import db

auth = Blueprint("auth", __name__)

@auth.route("/login")
def login():
    email = request.form.get("email")
    email = email.lower()

    ##

    return render_template("login.html")

@auth.route("/signup")
def signup():
    return render_template("signup.html")

@auth.route("/signup", methods=["POST"])
def signup_post():
    name = request.form.get("name")
    name = name.lower()
    print(name)

    email = request.form.get("email")
    email = email.lower()
    print(email)

    password = request.form.get("password")
    hashed_password = generate_password_hash(password)
    print(hashed_password)

    #if email_exists:
    #    flash('Email address already exists')
    #    return redirect(url_for("auth.signup"))

    return redirect(url_for("auth.login"))

@auth.route("/logout")
def logout():
    return "Logout"
