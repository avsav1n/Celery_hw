from io import BytesIO
from uuid import UUID

from celery.result import AsyncResult
from flask import jsonify, request, send_file
from werkzeug.datastructures import FileStorage

from server.applications import app, celery
from server.tasks import upscale_image
from server.utils import ImageInfo


@app.route("/upscale", methods=["POST"])
async def create_task():
    image: FileStorage = request.files.get("image")
    ext: str = f'.{image.filename.split(".")[-1].lower()}'
    task: AsyncResult = upscale_image.delay(
        image=image.read(),
        ext=ext,
        model_path="./upscale/EDSR_x2.pb",
    )
    return jsonify(
        {
            "status": "STARTED",
            "task_id": task.id,
        }
    )


@app.route("/tasks/<uuid:task_id>", methods=["GET"])
async def get_task(task_id: UUID):
    task = AsyncResult(id=task_id, app=celery)
    result = None
    if task.ready():
        task_result: ImageInfo = task.result
        result = f"{request.host_url}processed/{task.id}{task_result.ext}"
    return jsonify({"status": task.status, "link": result})


@app.route("/processed/<uuid:task_id>", methods=["GET"])
async def get_photo(task_id: str):
    task = AsyncResult(id=task_id, app=celery)
    task_result: ImageInfo = task.result
    return send_file(
        BytesIO(task_result.size),
        mimetype=f"image/{task_result.ext}",
        as_attachment=True,
        download_name=f"{task.id}.{task_result.ext}",
    )


if __name__ == "__main__":
    app.run()
