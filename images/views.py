from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
import os

# Create your views here.

class ImageView(View):
    def get(self, request):
        image_path = os.path.dirname(os.path.realpath(__file__)) + '/test_resources/frame.jpg'
        img = open(image_path, 'r')
        data = img.read()

        response = HttpResponse(data, content_type='image/jpg')
        return response

