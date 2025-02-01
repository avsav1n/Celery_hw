import time

from flask.testing import FlaskClient


def test_upscale_success(celery_worker, image_factory, client: FlaskClient):
    fake_images: dict = image_factory()
    response = client.post("/upscale", data=fake_images)

    assert response.status_code == 201

    response_json: list[dict[str, str]] = response.json
    task_id: str = response_json[0]["task_id"]
    status: str = response_json[0]["status"]
    timeout: int = 60
    while status != "SUCCESS" and timeout > 0:
        response = client.get(f"/tasks/{task_id}")
        status: str = response.json["status"]
        time.sleep(1)
        timeout -= 1

    assert timeout > 0

    response = client.get(f"/processed/{task_id}")

    assert response.status_code == 200
    assert isinstance(response.data, bytes)
    assert response.content_type == "image/png"


def test_upscale_fail_no_images(client: FlaskClient):
    response = client.post("/upscale")

    assert response.status_code == 400
    assert "error" in response.json
