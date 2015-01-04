from django.conf import settings
from shutil import copyfileobj
import tinys3
import os

class LocalStorage(object):
    def __init__(self, file_instance, request, hash, variation):
        self.file_instance = file_instance
        self.request = request
        self.hash = hash
        self.variation = variation

    def get_filename(self):
        return self.hash + (self.variation or '')

    def get_remote_path(self):
        path = 'http://%s%s%s%s' % (self.request.META['HTTP_HOST'], settings.MEDIA_URL, self.get_filename())
        return path

    def store(self):
        image_path = os.path.join(settings.MEDIA_ROOT, self.get_filename())

        with open(image_path, 'w') as fw:
            copyfileobj(self.file_instance, fw)


class S3Storage(LocalStorage):
    def get_remote_path(self):
        path = 'https://%s.s3.amazonaws.com/%s' % (self.S3_BUCKET, self.get_filename())
        return path

    def store(self):
        conn = tinys3.Connection(self.S3_ACCESS_KEY, self.S3_SECRET_KEY, default_bucket=self.S3_BUCKET, tls=True)
        conn.upload(self.get_filename(), self.file_instance)

    @property
    def S3_BUCKET(self):
        return os.environ.get('S3_BUCKET')

    @property
    def S3_ACCESS_KEY(self):
        return os.environ.get('S3_ACCESS_KEY')

    @property
    def S3_SECRET_KEY(self):
        return os.environ.get('S3_SECRET_KEY')


