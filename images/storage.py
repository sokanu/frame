from django.conf import settings
from shutil import copyfileobj
import os

class LocalStorage(object):
    def __init__(self, file_instance, request, hash, variation):
        self.file_instance = file_instance
        self.request = request
        self.hash = hash
        self.variation = variation

    def get_remote_path(self):
        path = 'http://%s%s%s%s' % (self.request.META['HTTP_HOST'], settings.MEDIA_URL, self.hash, self.variation or '')
        return path

    def store(self):
        image_path = os.path.join(settings.MEDIA_ROOT, self.hash + (self.variation or ''))

        with open(image_path, 'w') as fw:
            copyfileobj(self.file_instance, fw)

