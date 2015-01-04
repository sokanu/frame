from django.conf import settings
from images.models import S3Connection
from shutil import copyfileobj
import tinys3
import os
import urllib

class LocalStorage(object):
    def __init__(self, file_instance, hash, variation):
        """
        Concerns:
        - The variation property is a little confusing; should it be a dictionary or the argument slug approach? The argument slug method is in a totally different world, so if anything else had to use this it would be screwed. Maybe we should force a dictionary and then move the argument slug creation code here
        - Should we include file_instance during initialization, or on upload? This library was originally about uploading and uploading only, but now that we're getting into downloading it doesn't make sense. Maybe we put this in the store method
        """

        self.file_instance = file_instance
        self.hash = hash
        self.variation = variation

    def get_filename(self):
        """
        Builds a filename by combining the hash name and the variation slug
        """
        return self.hash + (self.variation or '')

    def get_file_data(self):
        """
        Returns the raw data for the specified file
        """
        image_path = os.path.join(settings.MEDIA_ROOT, self.get_filename())
        # TODO: do you need to close this?
        data = open(image_path, 'r').read()
        return data

    def get_remote_path(self):
        """
        Builds a relative remote path by combining the MEDIA_URL setting and the filename
        """
        path = '%s%s' % (settings.MEDIA_URL, self.get_filename())
        return path

    def store(self):
        """
        Copy over the `file_instance` to the local storage
        """
        image_path = os.path.join(settings.MEDIA_ROOT, self.get_filename())

        with open(image_path, 'w') as fw:
            copyfileobj(self.file_instance, fw)


class S3Storage(LocalStorage):
    def __init__(self, *args, **kwargs):
        """
        Overrides the LocalStorage and initializes a shared S3 connection
        """
        super(S3Storage, self).__init__(*args, **kwargs)
        self.conn = tinys3.Connection(self.S3_ACCESS_KEY, self.S3_SECRET_KEY, default_bucket=self.S3_BUCKET, tls=True)

    def get_remote_path(self):
        """
        Returns an absolute remote path for the filename from the S3 bucket
        """
        path = 'https://%s.%s/%s' % (self.conn.default_bucket, self.conn.endpoint, self.get_filename())
        return path

    def get_file_data(self):
        """
        Returns the raw data for the specific file, downloading it from S3
        """
        path = self.get_remote_path()
        data = urllib.urlopen(path).read()
        return data

    def store(self):
        """
        Copy over the `file_instance` from memory to S3
        """
        self.conn.upload(self.get_filename(), self.file_instance)

    @property
    def S3_BUCKET(self):
        """
        Returns the S3_BUCKET. Checks local environment variables first, database-stored settings second
        """
        return os.environ.get('S3_BUCKET', self.database_settings.bucket)

    @property
    def S3_ACCESS_KEY(self):
        """
        Returns the S3_ACCESS_KEY. Checks local environment variables first, database-stored settings second
        """
        return os.environ.get('S3_ACCESS_KEY', self.database_settings.access_key)

    @property
    def S3_SECRET_KEY(self):
        """
        Returns the S3_SECRET_KEY. Checks local environment variables first, database-stored settings second
        """
        return os.environ.get('S3_SECRET_KEY', self.database_settings.secret_key)

    @property
    def database_settings(self):
        """
        Pulls an S3Connection instance, which contains S3 connection settings, from the databas. Result is cached locally
        """
        if not getattr(self, '__database_settings', None):
            self.__database_settings = S3Connection.objects.get()
        return self.__database_settings


