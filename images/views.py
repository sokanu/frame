from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from images.modifiers import SizeModifier
from images.modifiers import QualityModifier
from images.models import Image as ImageModel
from django.shortcuts import render
from django.shortcuts import redirect
from PIL import Image
import importlib
import StringIO
import os
import mimetypes

# initialize the storage module
storage_library_module_name, storage_library_class_name = settings.FRAME_STORAGE_LIBRARY.rsplit('.', 1)
STORAGE_LIBRARY = getattr(importlib.import_module(storage_library_module_name), storage_library_class_name)

class ImageView(View):
    def get(self, request, image_identifier):
        arguments_slug = STORAGE_LIBRARY.create_argument_slug(request.GET)

        # check cache
        cache_key = '%s__%s' % (image_identifier, arguments_slug)

        path = cache.get(cache_key)
        if not path:

            try:
                image_instance = ImageModel.objects.get(hash=image_identifier, variation=arguments_slug)
            except ImageModel.DoesNotExist:
                image_instance = self.get_modified_image(request, image_identifier)

            path = image_instance.path
            cache.set(cache_key, path)

        return redirect(path)

    def get_modified_image(self, request, image_identifier):

        # grab original image instance data
        try:
            image_instance = ImageModel.objects.get(hash=image_identifier, variation__isnull=True)
        except ImageModel.DoesNotExist:
            raise Http404

        # download original image data
        err_is_this_duplicate_image_data = STORAGE_LIBRARY(filename=image_identifier).get_file_data()

        # why is this needed?
        image_data = StringIO.StringIO()
        image_data.write(err_is_this_duplicate_image_data)
        image_data.seek(0)

        # open PIL image instance with image data
        image = Image.open(image_data)

        # apply modifiers
        modifiers = [SizeModifier, QualityModifier]
        for modifier_class in modifiers:
            image = modifier_class(image=image, params=request.GET).run().image

        # save the modified image to a temporary file string
        temporary_file_string = StringIO.StringIO()
        image.save(temporary_file_string, 'jpeg')
        temporary_file_string.seek(0)

        # create a new storage instance and save the modified file
        filename = image_identifier + STORAGE_LIBRARY.create_argument_slug(request.GET)
        storage_instance = STORAGE_LIBRARY(filename=filename)
        storage_instance.store(temporary_file_string, content_type=image_instance.content_type)

        # create a new modified instance
        image_instance.pk = None
        image_instance.variation = STORAGE_LIBRARY.create_argument_slug(request.GET)
        image_instance.path = storage_instance.get_remote_path()
        image_instance.save()

        return image_instance

class ImageUploaderView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ImageUploaderView, self).dispatch(*args, **kwargs)

    def get(self, request):
        images = ImageModel.objects.filter(variation__isnull=True)
        return render(request, 'images/uploader.html', {
            'images': images
        })

    def post(self, request):
        if not request.FILES.get('attachment'):
            return HttpResponseBadRequest('A file must be provided under the `attachment` POST parameter')

        fr = request.FILES['attachment']

        mimetype, encoding = mimetypes.guess_type(fr.name)
        if not mimetype in settings.ALLOWED_FORMATS:
            return HttpResponseForbidden('The provided file\'s mimetype of `%s` is not in the ALLOWED_FORMATS list' % mimetype)


        # Ugh, we should change this; needs to be a better way to get a unique ID
        # rather than relying on creating instance first
        image_identifier = ImageModel.generate_hash()

        storage_instance = STORAGE_LIBRARY(filename=image_identifier)
        storage_instance.store(fr, content_type=fr.content_type)

        image_instance = ImageModel(file_name=fr.name, content_type=fr.content_type)
        image_instance.hash = image_identifier
        image_instance.path = storage_instance.get_remote_path()
        image_instance.save()

        return HttpResponse(image_identifier)


