from flask import Blueprint, render_template
from flask_login import login_required, current_user

from util import Util
from app import db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    posts = db.get_posts()
    posts = Util.convert_to_web(posts)

    return render_template("main.html", posts=posts, user=current_user)



@main.route("/home")
@login_required
def home():
    #posts = db.get_posts_by_user()
    posts = db.get_posts()
    posts = Util.convert_to_web(posts)

    return render_template("main.html", posts=posts, user=current_user)


@main.route("/friends")
@login_required
def friends():
    posts = db.get_posts_of_friends(current_user.id)
    posts = Util.convert_to_web(posts)

    print(friends)
    return render_template("main.html", posts=posts, user=current_user)


@main.route("/groups")
@login_required
def groups():
    #posts = db.get_posts_of_groups()
    posts = db.get_posts()
    posts = Util.convert_to_web(posts)

    return render_template("main.html", posts=posts, user=current_user)
