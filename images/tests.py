from django.test import Client
from django.test import TestCase
import os
from PIL import Image
import StringIO

# helpers
def request_image(url):
    c = Client()
    response = c.get(url)
    response_data = StringIO.StringIO(response.content)
    response_image = Image.open(response_data)
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
    def test_response_image(self):
        image = request_image('/')

        image_path = build_path('frame.jpg')
        expected_image = Image.open(image_path)

        self.assertEqual(image.size, expected_image.size)

class ImageSizeTestCase(TestCase):
    def test_response_image_resize_width(self):
        image = request_image('/')

        image_path = build_path('frame.jpg')
        expected_image = Image.open(image_path)

        # test initial response size
        self.assertEqual(image.size[0], expected_image.size[0])
        self.assertNotEqual(image.size[0], 100)

        # request modified width image
        modified_width_image = request_image('/?width=100')

        # test modified response size
        self.assertEqual(modified_width_image.size[0], 100)
        self.assertNotEqual(image.size[0], modified_width_image.size[0])

        # ensure ratios are identical
        self.assertNotEqual(image.size[0] / float(image.size[1]), modified_width_image.size[0] / float(modified_width_image.size[1])) 
        
    def test_response_image_resize_height(self):
        image = request_image('/')

        image_path = build_path('frame.jpg')
        expected_image = Image.open(image_path)

        # test initial response size
        self.assertEqual(image.size[1], expected_image.size[1])
        self.assertNotEqual(image.size[1], 100)

        # request modified width image
        modified_height_image = request_image('/?height=100')

        # test modified response size
        self.assertEqual(modified_height_image.size[1], 100)
        self.assertNotEqual(image.size[1], modified_height_image.size[1])

        # ensure ratios are identical
        self.assertNotEqual(image.size[0] / float(image.size[1]), modified_height_image.size[0] / float(modified_height_image.size[1])) 
 
    def test_response_image_resize_width_height(self):
        # request modified height & width image
        modified_image = request_image('/?width=100&height=100')

        # test modified response size
        self.assertEqual(modified_image.size[0], 100)
        self.assertEqual(modified_image.size[1], 100)

    def test_response_larger_image(self):
        image = request_image('/')
        larger_image = request_image('/?width=%d' % (image.size[0] * 2))

        self.assertEqual(image.size[0] * 2, larger_image.size[0])
        self.assertEqual(image.size[1] * 2, larger_image.size[1])

    def test_image_sizes_are_integers(self):
        image = request_image('/?width=100.432')
        self.assertEqual(image.size[0], 100)

        image = request_image('/?height=150.432')
        self.assertEqual(image.size[1], 150)


class ImageQualityResponse(TestCase):
    def test_full_quality_image(self):
        image = request_image('/?quality=100')

        image_path = build_path('frame.jpg')
        expected_image = Image.open(image_path)

        i1d = StringIO.StringIO()
        image.save(i1d, 'jpeg')

        i2d = StringIO.StringIO()
        expected_image.save(i2d, 'jpeg')

        data_size_diff = abs(float(i1d.len) / i2d.len - 1)

        self.assertTrue(data_size_diff < 0.005)

    def test_variable_quality_image(self):
        lower_quality_image = request_image('/?quality=80')
        i1d = StringIO.StringIO()
        lower_quality_image.save(i1d, 'jpeg')

        even_lower_quality_image = request_image('/?quality=20')
        i2d = StringIO.StringIO()
        even_lower_quality_image.save(i2d, 'jpeg')

        self.assertTrue(i1d.len > i2d.len)


class ImageUploaderTest(TestCase):
    def test_basic_upload(self):
        for image_file in ['frame.jpg', 'frame.png']:
            image_path = build_path(image_file)
            response = upload_image(image_path)
            file_id = response.content

            response_image = request_image('/' + file_id)
            initial_image = Image.open(image_path)
            self.assertEqual(response_image.size[0], initial_image.size[0])
            self.assertEqual(response_image.size[1], initial_image.size[1])

    def test_valid_formats(self):
        for image_file in ['frame.jpg', 'frame.jpeg', 'frame.png', 'frame.gif']:
            image_path = build_path(image_file)
            response = upload_image(image_path)
            self.assertEqual(response.status_code, 200)
            print 'RESPONSE: %s ' % response.content

    def test_invalid_format(self):
        invalid_path = build_path('document.txt')
        response = upload_image(invalid_path)
        self.assertEqual(response.status_code, 403)

    def test_large_file_name(self):
        pass


    # try file size limits
    # test to ensure that only valid image files are accepted
    # try retrieving the uploaded image
    # try using the wrong argument for file
    # fail basic validation
    # pass basic validation
    # test uploading thousands of files? may be a little intensive, but good for testing memory leaks and forgotten file closing

