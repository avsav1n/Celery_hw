import time

from server.applications import celery
from server.utils import ImageInfo
from upscale.upscale import Scaler


@celery.task(bind=True)
def upscale_image(self, /, **kwargs) -> bytes:
    result_size: bytes = Scaler.upscale(image_name=self.request.id, **kwargs)
    return ImageInfo(size=result_size, ext=kwargs.get("ext"))
