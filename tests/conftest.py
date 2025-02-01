import subprocess
import time
from io import BytesIO
from random import randbytes

import pytest
from flask.testing import FlaskClient

from server.views import app
from tests.utils import create_random_image, get_celery_exec_path


@pytest.fixture(scope="module")
def celery_worker():
    celery_path = get_celery_exec_path()
    celery_name = f"celery-{int(time.time())}"
    process = subprocess.Popen(
        [celery_path, "-A", "server.tasks", "worker", "-P", "solo", "-n", celery_name]
    )
    time.sleep(5)
    try:
        yield
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)


@pytest.fixture(scope="session")
def client() -> FlaskClient:
    app.testing = True
    return app.test_client()


@pytest.fixture(scope="session")
def image_factory():
    def factory(height: int = 100, width: int = 100, quantity: int = 1, bytes_only: bool = False):
        if bytes_only:
            return create_random_image(height=height, width=width)
        images = {}
        for i in range(quantity):
            image: bytes = create_random_image(height=height, width=width)
            images.update({f"image{i+1}": (BytesIO(image), f"fake_image{i+1}.png", "image/png")})
        return images

    return factory


@pytest.fixture(scope="session")
def asyncresult_mock():
    def wrapper(is_ready: bool = True):
        class AsyncResultMock:
            def __init__(self, id: str, **kwargs):
                self.id = id
                self.is_ready = is_ready
                self.status = self.get_status()
                self.result = (create_random_image(), "png")

            def get_status(self):
                return "mocked_success" if self.is_ready else "mocked_pending"

            def ready(self):
                return self.is_ready

        return AsyncResultMock

    return wrapper


@pytest.fixture(scope="session")
def scaler_mock():
    class ScalerMock:
        @classmethod
        def upscale(cls, *args, **kwargs):
            time.sleep(1)
            return randbytes(10)

    return ScalerMock
