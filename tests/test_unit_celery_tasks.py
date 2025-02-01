from celery.result import AsyncResult

from server.tasks import upscale_image


def test_upscale_image_sync(image_factory):
    image: bytes = image_factory(bytes_only=True)

    task: AsyncResult = upscale_image.apply(
        kwargs={"save_result": False, "image": image, "ext": "png"}
    )
    result, ext = task.result

    assert isinstance(result, bytes)
    assert len(image) < len(result)
    assert ext == "png"


def test_upscale_image_async(celery_worker, image_factory):
    image: bytes = image_factory(bytes_only=True)

    task: AsyncResult = upscale_image.delay(save_result=False, image=image, ext="png")
    result, ext = task.get(timeout=60)

    assert isinstance(result, bytes)
    assert len(image) < len(result)
    assert ext == "png"
