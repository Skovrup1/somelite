from flask import Blueprint, render_template, url_for, redirect, request
from flask_login import login_required, current_user

from database import Db
from util import Util
from app import db
from post import Post

main = Blueprint("main", __name__)


@main.route("/")
def index():
    posts = db.get_posts()
    posts = Util.convert_to_web(posts)

    return render_template("main.html", posts=posts, user=current_user)


@main.route("/home")
@login_required
def home():
    # posts = db.get_posts_by_user()
    with db.connect().cursor() as cur:
        names_posts = Db.get_names_and_posts(cur)
        names, posts = Util.convert_to_web(names_posts)

        return render_template("main.html", names=names, posts=posts, user=current_user)

@main.route("/home", methods=["POST"])
def home_post():
    post_id = request.form.get("post_id")

    db.like_post(current_user.id, post_id)

    return redirect(url_for("main.home"))




@main.route("/friends")
@login_required
def friends():
    names_posts = db.get_posts_of_friends(current_user.id)
    names, posts = Util.convert_to_web(names_posts)

    return render_template("main.html", names=names, posts=posts, user=current_user)


@main.route("/friends", methods=["POST"])
@login_required
def friends_post():
    post_id = request.form.get("post_id")

    db.like_post(current_user.id, post_id)

    return redirect(url_for("main.friends"))


@main.route("/groups")
@login_required
def groups():
    # posts = db.get_posts_of_groups()
    names_posts = db.get_names_and_posts()
    names, posts = Util.convert_to_web(names_posts)

    return render_template("main.html", posts=posts, user=current_user)
