from flask import Blueprint, render_template
from app import db, current_user

main = Blueprint("main", __name__)


@main.route("/")
def index():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


@main.route("/home")
def home():
    posts = db.get_posts()
    return render_template(
        "home.html", posts=posts, user=(current_user.id, current_user.name.capitalize())
    )


@main.route("/friends")
def friends():
    # hardcoded as alice for now
    posts = db.get_posts_of_friends(current_user.id)
    print(friends)
    return render_template("main.html", posts=posts)


@main.route("/groups")
def groups():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


@main.route("/logout")
def logout():
    posts = db.get_posts()
    return render_template("main.html", posts=posts)


@main.route("/login")
def login():
    return render_template("log.html")
