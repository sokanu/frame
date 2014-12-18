from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from PIL import Image
import StringIO
import os

# Create your views here.

class ImageView(View):
    def get(self, request):
        image_path = os.path.dirname(os.path.realpath(__file__)) + '/test_resources/frame.jpg'
        image_data = open(image_path, 'r')

        image = Image.open(image_data)

        if request.GET.get('width') or request.GET.get('height'):
            image_ratio = image.size[0] / float(image.size[1]) #  width / height

            if request.GET.get('width') and request.GET.get('height'):
                width = int(float(request.GET['width']))
                height = int(float(request.GET['height']))
            elif request.GET.get('width'):
                width = int(float(request.GET['width']))
                height = int(width / image_ratio)
            elif request.GET.get('height'):
                height = int(float(request.GET['height']))
                width = int(height * image_ratio)
            else:
                raise Exception('Internal Error. Something really strange happened')

            image = image.resize((width, height))

        if request.GET.get('quality') and not float(request.GET['quality']) >= 100:
            quality = int(float(request.GET['quality']))
            quality_modified_data = StringIO.StringIO()
            image.save(quality_modified_data, 'jpeg', quality=quality)
            quality_modified_data.seek(0)
            image = Image.open(quality_modified_data)


        response = HttpResponse(content_type='image/jpeg')
        image.save(response, 'jpeg')
        return response

