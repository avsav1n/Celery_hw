from server.celery_app import create_celery_app
from server.flask_app import create_flask_app

app = create_flask_app()
celery = create_celery_app(app=app)
