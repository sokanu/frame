from django.db import models
import random
import string


class Image(models.Model):
    hash = models.CharField(max_length=255, unique=True, blank=True)
    file_name = models.CharField(max_length=1204)
    content_type = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=1024)
    variation = models.CharField(max_length=1024, blank=True, null=True)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('image', kwargs={'image_identifier': self.hash})

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
        
