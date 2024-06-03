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

    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from main import main_bp
    app.register_blueprint(main_bp)

    return app
