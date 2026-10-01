from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()


def create_app(testing=False):
    """Application factory — supports production and test modes."""
    app = Flask(__name__)

    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///splitbill.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)

    # Register models so SQLAlchemy can create tables
    import models  # noqa: F401

    # Register route blueprints
    from routes.bills   import bills_bp
    from routes.reports import reports_bp
    app.register_blueprint(bills_bp,   url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
