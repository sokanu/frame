from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from images.modifiers import SizeModifier
from images.modifiers import QualityModifier
from images.models import Image as ImageModel
from django.shortcuts import render
from django.shortcuts import redirect
from shutil import copyfileobj
from PIL import Image
import StringIO
import os
import urllib


class ImageView(View):
    def get(self, request, image_identifier):
        arguments = request.META['QUERY_STRING']
        try:
            image_instance = ImageModel.objects.get(hash=image_identifier, variation=arguments)
        except ImageModel.DoesNotExist:
            return self.get_modified_image(request, image_identifier)
        else:
            return redirect(image_instance.path)


    def get_modified_image(self, request, image_identifier):
        image_instance = ImageModel.objects.get(hash=image_identifier)

        image_data = StringIO.StringIO()
        image_data.write(urllib.urlopen(image_instance.path).read())
        image_data.seek(0)

        image = Image.open(image_data)

        # apply modifiers
        modifiers = [SizeModifier, QualityModifier]
        for modifier_class in modifiers:
            image = modifier_class(image=image, params=request.GET).run().image

        response = HttpResponse(content_type=image_instance.content_type)
        image.save(response, 'jpeg')

        image_data.close()
        return response


class ImageUploaderView(View):

    def get(self, request):
        images = ImageModel.objects.all()
        return render(request, 'images/uploader.html', {
            'images': images
        })

    def post(self, request):
        if not request.FILES.get('attachment'):
            return HttpResponseBadRequest('A file must be provided under the `attachment` POST parameter')

        fr = request.FILES['attachment']

        if not fr.content_type in settings.ALLOWED_FORMATS:
            return HttpResponseForbidden()


        # Ugh, we should change this; needs to be a better way to get a unique ID
        # rather than relying on creating instance first
        image_instance = ImageModel(file_name=fr.name, content_type=fr.content_type)

        image_identifier = ImageModel.generate_hash()
        image_instance.hash = image_identifier
        image_instance.path = settings.MEDIA_URL + image_instance.hash

        image_extension = fr.name.split('.')[-1]
        image_path = os.path.join(settings.MEDIA_ROOT, image_identifier)

        with open(image_path, 'w') as fw:
            copyfileobj(fr, fw)

        image_instance.save()

        return HttpResponse(image_identifier)
