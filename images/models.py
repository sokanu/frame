from django.db import models
from images.encrypted_models import EncryptedPKModelManager
from images.encrypted_models import EncryptedPKModel


class ImageModelManager(EncryptedPKModelManager):
    pass


class Image(EncryptedPKModel):
    PK_SECRET_KEY = 't&32$$a#'

    file_name = models.CharField(max_length=1204)
    content_type = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ImageModelManager()
        
