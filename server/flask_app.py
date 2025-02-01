import flask

from server.config import REDIS_BACKEND, REDIS_BROKER


def create_flask_app():
    app = flask.Flask(__name__)
    app.config["UPLOAD_FOLDER"] = "results"
    app.config.update(
        CELERY_CONFIG={
            "broker_url": REDIS_BROKER,
            "result_backend": REDIS_BACKEND,
            "broker_connection_retry_on_startup": True,
        }
    )
    return app
