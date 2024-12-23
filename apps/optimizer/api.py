import base64
from ninja import Router
from core.auth import ApiKey
from datetime import datetime
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from image_optimize.app import ImageOptimizer, WebpPILOptimizer

from .choices import ImageStatus
from .models import OptimizingImages
from .schemas import ImageUploadSchema
from .tasks import optimizer_images_async


optimizer_router = Router()

@optimizer_router.post("imagem/", auth=ApiKey())
def optimize_image(request: HttpRequest, image_upload: ImageUploadSchema):
    """
        Nesse endpoint você poderá enviar uma imagem em base64 que iremos te devolver já otimizada
        Você poderá escolher o modo (Sync ou Async), se Sync devolveremos ná própria requisição a imagem já otimizada
        caso você prefira de forma Async devolveremos no webhook criado em sua perfil 
    """
    img = base64.b64decode(image_upload.img)

    content = ContentFile(img, name=f"optmizing.{image_upload.format}")
    image_instance = OptimizingImages(
        user=request.auth,
        default_image=content,
        mode=image_upload.mode,
        format=image_upload.format,
        compression=image_upload.compressin
    )
    image_instance.save()

    if image_upload.mode.upper() == "SYNC":
        file_path = settings.MEDIA_ROOT / image_instance.default_image.name if settings.DEBUG else image_instance.default_image.url
        webp_pil_optmizer = ImageOptimizer(file_path, image_upload.compression, WebpPILOptimizer())

        img_result = webp_pil_optmizer.optimize().getvalue()

        name = f"optmized.{image_upload.format}"
        image_instance.optimized_image.save(
            name,
            ContentFile(img_result, name=name)
        )
        image_instance.status = ImageStatus.PROCESSED
        image_instance.complete_at = datetime.now()
        image_instance.save()
    
        return 200, {"encoded_image": base64.b64encode(img_result).decode(), "image_url": image_instance.optimized_image.url, "uuid": image_instance.id}
    
    elif image_upload.mode.upper() == "ASYNC":
        optimizer_images_async.delay(image_instance.id)
        return 200, {"status": "Imagem em processamento", "uuid": image_instance.id}
    else:
        return 404, {"error": "Modo de processamento não encontrado"}
    
@optimizer_router.get("imagem/{image_id}", auth=ApiKey())
def get_optimized_image(request, image_id: str):
    image_instance = get_object_or_404(OptimizingImages, id=image_id)
    if image_instance.status != "processed":
        return {"status": image_instance.status}
    
    optmized_image_url = request.build_absolute_uri(image_instance.optimized_image.url) if settings.DEBUG else image_instance.optimized_image.url
    
    with image_instance.optimized_image.open("rb") as image_file:
        image_bytes = image_file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

    return {
        "status": image_instance.status,
        "url": optmized_image_url,
        "enconded_image": base64_image
    }