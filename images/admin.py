from django.contrib import admin
from images.models import Image
from images.models import S3Connection

# Register your models here.
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('hash', 'variation', 'created_at')

@admin.register(S3Connection)
class S3ConnectionAdmin(admin.ModelAdmin):
    list_display = ('bucket',)
