from io import BytesIO
from uuid import UUID

from celery.result import AsyncResult
from flask import Response, jsonify, request, send_file
from werkzeug.datastructures import FileStorage

from server.applications import app, celery
from server.tasks import upscale_image
from server.utils import ImageInfo


@app.route("/upscale", methods=["POST"])
async def create_task() -> Response:
    if request.files is None:
        return jsonify({"error": "No images to process"})
    tasks = []
    for image in request.files.values():
        ext: str = image.filename.split(".")[-1].lower()
        task: AsyncResult = upscale_image.delay(
            image=image.read(),
            ext=ext,
            model_path="./upscale/EDSR_x2.pb",
        )
        tasks.append({"status": task.status, "task_id": task.id})
    return jsonify(tasks)


@app.route("/tasks/<string:task_id>", methods=["GET"])
async def get_task(task_id: str) -> Response:
    task = AsyncResult(id=task_id, app=celery)
    result = f"{request.host_url}processed/{task.id}" if task.ready() else None
    return jsonify({"status": task.status, "link": result})


@app.route("/processed/<string:task_id>", methods=["GET"])
async def get_image(task_id: str) -> Response:
    task = AsyncResult(id=task_id, app=celery)
    result, ext = task.result
    return send_file(
        BytesIO(result),
        mimetype=f"image/{ext}",
        as_attachment=True,
        download_name=f"{task.id}.{ext}",
    )


if __name__ == "__main__":
    app.run()
