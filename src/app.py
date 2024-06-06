from flask import Flask
from database import Db
from user import User

db = Db("somelite", "somelite", "postgres", "postgres")
current_user = User(1, "Alice")


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "password"

    # delete the old db if it exists
    print("recreating database")
    db.delete()
    db.create()
    db.create_tables()

    from auth import auth

    app.register_blueprint(auth)

    from main import main

    app.register_blueprint(main)

    return app
