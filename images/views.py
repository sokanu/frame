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
from images.storage import LocalStorage as StorageLibrary
from django.shortcuts import render
from django.shortcuts import redirect
from PIL import Image
import StringIO
import os


class ImageView(View):
    def get(self, request, image_identifier):
        arguments_slug = StorageLibrary.create_argument_slug(request.GET)

        try:
            image_instance = ImageModel.objects.get(hash=image_identifier, variation=arguments_slug)
        except ImageModel.DoesNotExist:
            image_instance = self.get_modified_image(request, image_identifier)

        # TODO: serving static assets is an issue for test cases; how do we fix?
        #from django.core.urlresolvers import reverse
        #return redirect(reverse('image_test_case_viewer', kwargs={'local_filename': image_instance.path.split('/')[-1]}))

        return redirect(image_instance.path)

    def get_modified_image(self, request, image_identifier):

        # grab original image instance data
        try:
            image_instance = ImageModel.objects.get(hash=image_identifier, variation__isnull=True)
        except ImageModel.DoesNotExist:
            raise Http404

        # download original image data
        err_is_this_duplicate_image_data = StorageLibrary(filename=image_identifier).get_file_data()

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
        filename = image_identifier + StorageLibrary.create_argument_slug(request.GET)
        storage_instance = StorageLibrary(filename=filename)
        storage_instance.store(temporary_file_string)

        # create a new modified instance
        image_instance.pk = None
        image_instance.variation = StorageLibrary.create_argument_slug(request.GET)
        image_instance.path = storage_instance.get_remote_path()
        image_instance.save()

        return image_instance

# TODO: serving static assets is an issue for test cases; how do we fix?
class ImageTestCaseViewer(View):
    def get(self, request, local_filename):
        with open(os.path.join(settings.MEDIA_ROOT, local_filename), 'r') as fr:
            return HttpResponse(fr.read())

class ImageUploaderView(View):

    def get(self, request):
        images = ImageModel.objects.filter(variation__isnull=True)
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
        image_identifier = ImageModel.generate_hash()

        storage_instance = StorageLibrary(filename=image_identifier)
        storage_instance.store(fr)

        image_instance = ImageModel(file_name=fr.name, content_type=fr.content_type)
        image_instance.hash = image_identifier
        image_instance.path = storage_instance.get_remote_path()
        image_instance.save()

        return HttpResponse(image_identifier)

