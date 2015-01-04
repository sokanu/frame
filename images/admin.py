from django.contrib import admin
from images.models import Image
from images.models import S3Connection

# Register your models here.
admin.site.register(Image)
admin.site.register(S3Connection)
