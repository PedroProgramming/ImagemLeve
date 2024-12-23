# Strategy
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFile
from abc import ABC, abstractmethod

from .exceptions import NotImage


class ImageOptimizerTypesStratagy(ABC):
    @abstractmethod
    def optimize(self, img: ImageFile, quality: int):
        ...


class WebpPILOptimizer(ImageOptimizerTypesStratagy):
    def optimize(self, img: ImageFile, quality: int):
        output = BytesIO()
        img.save(output, 'webp', optimize=True, quality=quality)
        return output


# Otimizador de imagem
class ImageOptimizer:
    def __init__(
        self,
        input_path: str,
        compression: int,
        optimizer: ImageOptimizerTypesStratagy,
    ):
        self.input_path = input_path
        self.compression = compression
        self.optimizer = optimizer
        self.img = self._open_image()

    def optimize(self):
        return self.optimizer.optimize(self.img, self.quality)

    def _open_image(self):
        try:
            img = Image.open(self.input_path)
            img.verify()
            return Image.open(self.input_path)
        except:
            raise NotImage(self.input_path)

    @property
    def quality(self):
        return 1 if (100 - self.compression) == 0 else (100 - self.compression)
