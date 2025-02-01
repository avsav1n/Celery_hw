from server.applications import celery
from server.upscale import Scaler


@celery.task(bind=True)
def upscale_image(self, /, **kwargs) -> bytes:
    result: bytes = Scaler.upscale(image_name=self.request.id, **kwargs)
    return result, kwargs.get("ext")
