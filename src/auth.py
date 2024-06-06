from flask import Blueprint, render_template, redirect, url_for, request  # , flash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required

from database import Db
from app import db
from user import User

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    email = email.lower()

    with db.connect().cursor() as cur:
        print("USERS")
        print(Db.get_users(cur))
        user = Db.get_user_by_email(cur, email)

    if not user:
        print("no user by that email")
        return redirect(url_for("auth.login"))

    # create user from id
    user = User.get(user[0])

    password = request.form.get("password")

    pass_match = check_password_hash(user.password, password)
    if pass_match:
        login_user(user, remember=False)

        return redirect(url_for("main.home"))
    else:
        return redirect(url_for("auth.login"))


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

    with db.connect().cursor() as cur:
        Db.create_user(cur, name, email, password, 20)

        users = Db.get_users(cur)
        print(users)

    # if email_exists:
    #    flash('Email address already exists')
    #    return redirect(url_for("auth.signup"))

    return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
