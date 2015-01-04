from django.conf import settings
from images.models import S3Connection
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
    def __init__(self, *args, **kwargs):
        super(S3Storage, self).__init__(*args, **kwargs)
        self.conn = tinys3.Connection(self.S3_ACCESS_KEY, self.S3_SECRET_KEY, default_bucket=self.S3_BUCKET, tls=True)

    def get_remote_path(self):
        path = 'https://%s.%s/%s' % (self.conn.default_bucket, self.conn.endpoint, self.get_filename())
        return path

    def store(self):
        self.conn.upload(self.get_filename(), self.file_instance)

    @property
    def S3_BUCKET(self):
        return os.environ.get('S3_BUCKET', self.database_settings.bucket)

    @property
    def S3_ACCESS_KEY(self):
        return os.environ.get('S3_ACCESS_KEY', self.database_settings.access_key)

    @property
    def S3_SECRET_KEY(self):
        return os.environ.get('S3_SECRET_KEY', self.database_settings.secret_key)

    @property
    def database_settings(self):
        if not getattr(self, '__database_settings', None):
            self.__database_settings = S3Connection.objects.get()
        return self.__database_settings


