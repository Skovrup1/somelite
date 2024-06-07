from flask import Blueprint, render_template, url_for, redirect, request, abort
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
    groups = db.get_posts_of_groups_ordered(current_user.id)

    new = []
    for group in groups:
        posts, group_name = group

        new_posts = []
        for post in posts:
            (user_name, *without_name) = post
            obj = Post(*without_name)
            new_posts.append((user_name, obj))

        new.append((new_posts, group_name))
    groups = new

    key = request.args.get("key", None)
    if not key:
        posts = None
        if groups:
            posts = groups[0][0]

        return render_template(
            "groups.html", posts=posts, groups=groups, user=current_user
        )

    group_posts = None
    for group in groups:
        group_posts, name = group

        if key == name:
            posts = group_posts

    if not group_posts:
        abort(404)

    return render_template("groups.html", posts=posts, groups=groups, user=current_user)


@main.route("/groups", methods=["POST"])
@login_required
def groups_post():
    post_id = request.form.get("post_id")

    db.like_post(current_user.id, post_id)

    return redirect(url_for("main.groups", **request.args.to_dict()))
