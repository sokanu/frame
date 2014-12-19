from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from images.modifiers import SizeModifier
from images.modifiers import QualityModifier
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
        with open(os.path.join(settings.MEDIA_ROOT, 'test.jpg'), 'w') as fw:
            copyfileobj(fr, fw)

        print dir(fw)
        return HttpResponse('ok')
