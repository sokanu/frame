from django.conf import settings
from django.test import Client
from django.test import TestCase
import os
from PIL import Image
import StringIO

# helpers
def request_image(url):
    c = Client()
    response = c.get(url, follow=True)

    # The response should provide a redirection to the image, served via the media url
    # Because we cannot load media files in the test environment, we must extract the filename,
    # build a path to the file, and then load it locally
    media_url = response.redirect_chain[0][0]
    media_filename = media_url.split('/')[-1]
    media_path = os.path.join(settings.MEDIA_ROOT, media_filename)

    # load the local file
    response_image = Image.open(media_path)
    return response_image

def upload_image(file_path):
    c = Client()
    with open(file_path, 'r') as fp:
        response = c.post('/upload/', {'attachment': fp})
    return response

def build_path(file_name):
    return os.path.dirname(os.path.realpath(__file__)) + '/test_resources/%s' % file_name

# tests
class ImageViewTestCase(TestCase):
    def test_request_valid_image(self):
        # upload
        image_path = build_path('frame.jpg')
        upload_response = upload_image(image_path)
        image_identifier = upload_response.content

        # ensure we are redirected to an image
        c = Client()
        response = c.get('/%s/' % image_identifier)
        self.assertEqual(response.status_code, 302)

    def test_request_invalid_image(self):
        c = Client()
        response = c.get('/123123/', follow=True)
        self.assertEqual(response.status_code, 404)


class ImageSizeTestCase(TestCase):
    def test_response_image_resize_width(self):
        image_identifier = upload_image(build_path('frame.jpg')).content
        image = request_image('/%s/' % image_identifier)

        image_path = build_path('frame.jpg')
        expected_image = Image.open(image_path)

        # test initial response size
        self.assertEqual(image.size[0], expected_image.size[0])
        self.assertNotEqual(image.size[0], 100)

        # request modified width image
        modified_width_image = request_image('/%s/?width=100' % image_identifier)

        # test modified response size
        self.assertEqual(modified_width_image.size[0], 100)
        self.assertNotEqual(image.size[0], modified_width_image.size[0])

        # ensure ratios are identical
        self.assertNotEqual(image.size[0] / float(image.size[1]), modified_width_image.size[0] / float(modified_width_image.size[1])) 
        
    def test_response_image_resize_height(self):
        image_identifier = upload_image(build_path('frame.jpg')).content
        image = request_image('/%s/' % image_identifier)

        image_path = build_path('frame.jpg')
        expected_image = Image.open(image_path)

        # test initial response size
        self.assertEqual(image.size[1], expected_image.size[1])
        self.assertNotEqual(image.size[1], 100)

        # request modified width image
        modified_height_image = request_image('/%s/?height=100' % image_identifier)

        # test modified response size
        self.assertEqual(modified_height_image.size[1], 100)
        self.assertNotEqual(image.size[1], modified_height_image.size[1])

        # ensure ratios are identical
        self.assertNotEqual(image.size[0] / float(image.size[1]), modified_height_image.size[0] / float(modified_height_image.size[1])) 
 
    def test_response_image_resize_width_height(self):
        image_identifier = upload_image(build_path('frame.jpg')).content

        # request modified height & width image
        modified_image = request_image('/%s/?width=100&height=100' % image_identifier)

        # test modified response size
        self.assertEqual(modified_image.size[0], 100)
        self.assertEqual(modified_image.size[1], 100)

    def test_response_larger_image(self):
        image_identifier = upload_image(build_path('frame.jpg')).content
        image = request_image('/%s/' % image_identifier)
        larger_image = request_image('/%s/?width=%d' % (image_identifier, (image.size[0] * 2)))

        self.assertEqual(image.size[0] * 2, larger_image.size[0])
        self.assertEqual(image.size[1] * 2, larger_image.size[1])

    def test_image_sizes_are_integers(self):
        image_identifier = upload_image(build_path('frame.jpg')).content
        image = request_image('/%s/?width=100.432' % image_identifier)
        self.assertEqual(image.size[0], 100)

        image = request_image('/%s/?height=150.432' % image_identifier)
        self.assertEqual(image.size[1], 150)


class ImageQualityResponse(TestCase):
    def test_full_quality_image(self):
        image_identifier = upload_image(build_path('frame.jpg')).content
        image = request_image('/%s/?quality=100' % image_identifier)

        image_path = build_path('frame.jpg')
        expected_image = Image.open(image_path)

        i1d = StringIO.StringIO()
        image.save(i1d, 'jpeg')

        i2d = StringIO.StringIO()
        expected_image.save(i2d, 'jpeg')

        data_size_diff = abs(float(i1d.len) / i2d.len - 1)

        self.assertTrue(data_size_diff < 0.005)

    def test_variable_quality_image(self):
        image_identifier = upload_image(build_path('frame.jpg')).content
        lower_quality_image = request_image('/%s/?quality=80' % image_identifier)
        i1d = StringIO.StringIO()
        lower_quality_image.save(i1d, 'jpeg')

        even_lower_quality_image = request_image('/%s/?quality=20' % image_identifier)
        i2d = StringIO.StringIO()
        even_lower_quality_image.save(i2d, 'jpeg')

        self.assertTrue(i1d.len > i2d.len)


class ImageUploaderTest(TestCase):
    def test_basic_upload(self):
        for image_file in ['frame.jpg', 'frame.png']:
            image_path = build_path(image_file)
            response = upload_image(image_path)
            file_id = response.content

            response_image = request_image('/%s/' % file_id)
            initial_image = Image.open(image_path)
            self.assertEqual(response_image.size, initial_image.size)

    def test_wrong_upload_argument(self):
        file_path = build_path('frame.jpg')

        c = Client()
        with open(file_path, 'r') as fp:
            response = c.post('/upload/', {'invalid_argument': fp})

        self.assertEqual(response.status_code, 400)

    def test_valid_formats(self):
        for image_file in ['frame.jpg', 'frame.jpeg', 'frame.png', 'frame.gif']:
            image_path = build_path(image_file)
            response = upload_image(image_path)
            self.assertEqual(response.status_code, 200)

    def test_invalid_format(self):
        invalid_path = build_path('document.txt')
        response = upload_image(invalid_path)
        self.assertEqual(response.status_code, 403)

    def test_large_file_name(self):
        pass


    # try file size limits
    # test to ensure that only valid image files are accepted
    # fail basic validation
    # pass basic validation
    # test uploading thousands of files? may be a little intensive, but good for testing memory leaks and forgotten file closing

