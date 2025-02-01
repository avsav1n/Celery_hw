import sys
from functools import lru_cache
from pathlib import Path
from uuid import UUID

import cv2
import numpy as np
from numpy.typing import NDArray


def create_random_image(height: int = 100, width: int = 100) -> bytes:
    nparr: NDArray = np.random.randint(0, 256, size=(height, width, 3), dtype=np.uint8)
    _, image = cv2.imencode(ext=".png", img=nparr)
    return image.tobytes()


def validate_uuid(uuid: str) -> bool:
    try:
        UUID(uuid)
        return True
    except ValueError:
        return False


@lru_cache
def get_celery_exec_path():
    venv_path = Path(sys.prefix) / ("Scripts" if sys.platform.startswith("win") else "bin")
    return venv_path / "celery"
