import flask


def create_flask_app():
    app = flask.Flask(__name__)
    app.config["UPLOAD_FOLDER"] = "results"
    app.config.update(
        CELERY_CONFIG={
            "broker_url": "redis://localhost:6379/0",
            "result_backend": "redis://localhost:6379/1",
            "broker_connection_retry_on_startup": True,
        }
    )
    return app
