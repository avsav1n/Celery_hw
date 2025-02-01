from io import BytesIO

from celery.result import AsyncResult
from flask import Response, jsonify, request, send_file

from server.applications import app, celery
from server.exeptions import HttpError
from server.tasks import upscale_image


@app.errorhandler(HttpError)
async def errorhandler(error: HttpError):
    error_response: Response = jsonify({"error": error.message})
    error_response.status_code = error.status_code
    return error_response


@app.route("/upscale", methods=["POST"])
async def create_task() -> Response:
    if not request.files:
        raise HttpError(400, "No images to process")
    tasks = []
    for name, image in request.files.items():
        ext: str = image.filename.split(".")[-1].lower()
        task: AsyncResult = upscale_image.delay(image=image.read(), ext=ext, save_result=False)
        tasks.append({"status": task.status, "name": name, "task_id": task.id})
    return jsonify(tasks), 201


@app.route("/tasks/<string:task_id>", methods=["GET"])
async def get_task(task_id: str) -> Response:
    task = AsyncResult(id=task_id, app=celery)
    result = f"{request.host_url}processed/{task.id}" if task.ready() else None
    return jsonify({"status": task.status, "link": result})


@app.route("/processed/<string:task_id>", methods=["GET"])
async def get_image(task_id: str) -> Response:
    task = AsyncResult(id=task_id, app=celery)
    if not task.ready():
        raise HttpError(400, f"The task {task_id} is not completed")
    result, ext = task.result
    return send_file(
        BytesIO(result),
        mimetype=f"image/{ext}",
        as_attachment=True,
        download_name=f"{task.id}.{ext}",
    )


@app.route("/healthcheck", methods=["GET"])
async def healthcheck():
    return {"STATUS": "OK"}


if __name__ == "__main__":
    app.run()
