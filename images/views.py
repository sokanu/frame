from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from images.modifiers import SizeModifier
from images.modifiers import QualityModifier
from images.models import Image as ImageModel
from shutil import copyfileobj
from PIL import Image
import StringIO
import os


class ImageView(View):
    def get(self, request):
        image_path = os.path.dirname(os.path.realpath(__file__)) + '/test_resources/frame.jpg'
        image_data = open(image_path, 'r')
        image = Image.open(image_data)

        # apply modifiers
        modifiers = [SizeModifier, QualityModifier]
        for modifier_class in modifiers:
            image = modifier_class(image=image, params=request.GET).run().image

        response = HttpResponse(content_type='image/jpeg')
        image.save(response, 'jpeg')
        return response

class ImageUploaderView(View):

    def post(self, request):
        fr = request.FILES['attachment']

        if not fr.content_type in settings.ALLOWED_FORMATS:
            return HttpResponseForbidden()


        # Ugh, we should change this; needs to be a better way to get a unique ID
        # rather than relying on creating instance first
        image_instance = ImageModel.objects.create(file_name=fr.name)

        file_id = image_instance.encrypted_pk
        file_extension = fr.name.split('.')[-1]
        file_name = os.path.join(settings.MEDIA_ROOT, '%s.%s' % (file_id, file_extension))

        with open(file_name, 'w') as fw:
            copyfileobj(fr, fw)

        return HttpResponse(file_id)
