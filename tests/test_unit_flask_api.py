from uuid import uuid4

from flask.testing import FlaskClient

from tests.utils import validate_uuid

TASK_STATUSES = ("PENDING", "STARTED", "RETRY", "FAILURE", "SUCCESS")


def test_create_one_task(monkeypatch, image_factory, scaler_mock, client: FlaskClient):
    monkeypatch.setattr("server.tasks.Scaler", scaler_mock)
    fake_images: dict = image_factory()

    response = client.post("/upscale", data=fake_images)
    response_json: list[dict[str, str]] = response.json

    assert response.status_code == 201
    assert len(response_json) == 1
    assert response_json[0]["status"] in TASK_STATUSES
    assert validate_uuid(response_json[0]["task_id"])


def test_create_two_tasks(monkeypatch, image_factory, scaler_mock, client: FlaskClient):
    monkeypatch.setattr("server.tasks.Scaler", scaler_mock)
    tasks_quantity = 2
    fake_images: dict = image_factory(quantity=tasks_quantity)

    response = client.post("/upscale", data=fake_images)
    response_json: list[dict[str, str]] = response.json

    assert response.status_code == 201
    assert len(response_json) == tasks_quantity


def test_get_task_ready(monkeypatch, asyncresult_mock, client: FlaskClient):
    monkeypatch.setattr("server.views.AsyncResult", asyncresult_mock())

    response = client.get(f"/tasks/{str(uuid4())}")
    response_json: dict[str, str | None] = response.json
    link = response_json["link"].split("/")[-1]

    assert response.status_code == 200
    assert len(response_json) == 2
    assert validate_uuid(link)
    assert response_json["status"] == "mocked_success"


def test_get_task_not_ready(monkeypatch, asyncresult_mock, client: FlaskClient):
    monkeypatch.setattr("server.views.AsyncResult", asyncresult_mock(is_ready=False))

    response = client.get(f"/tasks/{str(uuid4())}")
    response_json: dict[str, str | None] = response.json

    assert response.status_code == 200
    assert len(response_json) == 2
    assert response_json["link"] is None
    assert response_json["status"] == "mocked_pending"


def test_get_image(monkeypatch, asyncresult_mock, client: FlaskClient):
    monkeypatch.setattr("server.views.AsyncResult", asyncresult_mock())

    response = client.get(f"/processed/{str(uuid4())}")

    assert response.status_code == 200
    assert isinstance(response.data, bytes)
    assert response.content_type == "image/png"
