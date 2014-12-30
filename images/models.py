from django.db import models
from images.encrypted_models import EncryptedPKModelManager
from images.encrypted_models import EncryptedPKModel
import random
import string


class ImageModelManager(EncryptedPKModelManager):
    pass


class Image(EncryptedPKModel):
    PK_SECRET_KEY = 't&32$$a#'

    hash = models.CharField(max_length=255, unique=True, blank=True)
    file_name = models.CharField(max_length=1204)
    content_type = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ImageModelManager()

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = Image.generate_hash()
        super(Image, self).save(*args, **kwargs)

    @staticmethod
    def generate_hash():
        while True:
            hash = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(32)])
            if not Image.objects.filter(hash=hash).exists():
                return hash
        
