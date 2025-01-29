import os

import cv2
import numpy as np
from cv2.dnn_superres import DnnSuperResImpl
from cv2.typing import MatLike
from numpy.typing import NDArray


class Scaler:
    _scaler: DnnSuperResImpl | None = None

    @classmethod
    def _initial(cls, model_path: str) -> None:
        if cls._scaler is None:
            cls._scaler = DnnSuperResImpl.create()
            cls._scaler.readModel(path=model_path)
            cls._scaler.setModel(algo="edsr", scale=2)

    @classmethod
    def _bytes_to_matlike(cls, img: bytes) -> MatLike:
        nparr: NDArray = np.frombuffer(img, dtype=np.uint8)
        return cv2.imdecode(buf=nparr, flags=cv2.IMREAD_COLOR)

    @classmethod
    def _matlike_to_bytes(cls, img: MatLike, ext: str = "png") -> bytes:
        _, nparr = cv2.imencode(ext=f".{ext}", img=img)
        return nparr.tobytes()

    @classmethod
    def _save_result_to_folder(cls, folder_path: str, image_name: str, img: MatLike) -> None:
        try:
            os.mkdir(folder_path)
        except FileExistsError:
            pass
        finally:
            cv2.imwrite(filename=f"{folder_path}{image_name}", img=img)

    @classmethod
    def upscale(
        cls,
        image: bytes,
        image_name: str,
        ext: str = "png",
        save_result: bool = True,
        save_result_path: str = "./results/",
        model_path: str = "EDSR_x2.pb",
    ) -> bytes:
        cls._initial(model_path=model_path)
        image: MatLike = cls._bytes_to_matlike(img=image)
        result: MatLike = cls._scaler.upsample(img=image)
        if save_result:
            cls._save_result_to_folder(
                folder_path=save_result_path, image_name=f"{image_name}.{ext}", img=result
            )
        return cls._matlike_to_bytes(img=result, ext=ext)
