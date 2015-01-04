from django.db import models
import random
import string


class Image(models.Model):
    hash = models.CharField(max_length=255, blank=True)
    file_name = models.CharField(max_length=1204)
    content_type = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=1024)
    variation = models.CharField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('hash', 'variation')

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
        

class S3Connection(models.Model):
    bucket = models.CharField(max_length=255)
    access_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.pk and S3Connection.objects.count():
            raise Exception('Cannot store more than one S3Connection')
        super(S3Connection, self).save(*args, **kwargs)
