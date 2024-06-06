from flask import Flask
from database import Db

db = Db("somelite", "postgres")

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "password"

    # delete the old db if it exists
    db.delete()
    db.create()
    db.create_tables()

    from .auth import auth
    app.register_blueprint(auth)

    from .main import main
    app.register_blueprint(main)

    return app
