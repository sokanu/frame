from django.test import Client
from django.test import TestCase
import os
from PIL import Image
import StringIO

# helper
def initialize_request_image(url):
    c = Client()
    response = c.get(url)
    response_data = StringIO.StringIO(response.content)
    response_image = Image.open(response_data)
    return response_image


# tests
class ImageViewTestCase(TestCase):
    def test_response_image(self):
        image = initialize_request_image('/')

        image_path = os.path.dirname(os.path.realpath(__file__)) + '/test_resources/frame.jpg'
        expected_image = Image.open(image_path)

        self.assertEqual(image.size, expected_image.size)

class ImageSizeTestCase(TestCase):
    def test_response_image_resize_width(self):
        image = initialize_request_image('/')

        image_path = os.path.dirname(os.path.realpath(__file__)) + '/test_resources/frame.jpg'
        expected_image = Image.open(image_path)

        # test initial response size
        self.assertEqual(image.size[0], expected_image.size[0])
        self.assertNotEqual(image.size[0], 100)

        # request modified width image
        modified_width_image = initialize_request_image('/?width=100')

        # test modified response size
        self.assertEqual(modified_width_image.size[0], 100)
        self.assertNotEqual(image.size[0], modified_width_image.size[0])

        # ensure ratios are identical
        self.assertNotEqual(image.size[0] / float(image.size[1]), modified_width_image.size[0] / float(modified_width_image.size[1])) 
        
    def test_response_image_resize_height(self):
        image = initialize_request_image('/')

        image_path = os.path.dirname(os.path.realpath(__file__)) + '/test_resources/frame.jpg'
        expected_image = Image.open(image_path)

        # test initial response size
        self.assertEqual(image.size[1], expected_image.size[1])
        self.assertNotEqual(image.size[1], 100)

        # request modified width image
        modified_height_image = initialize_request_image('/?height=100')

        # test modified response size
        self.assertEqual(modified_height_image.size[1], 100)
        self.assertNotEqual(image.size[1], modified_height_image.size[1])

        # ensure ratios are identical
        self.assertNotEqual(image.size[0] / float(image.size[1]), modified_height_image.size[0] / float(modified_height_image.size[1])) 
 
    def test_response_image_resize_width_height(self):
        # request modified height & width image
        modified_image = initialize_request_image('/?width=100&height=100')

        # test modified response size
        self.assertEqual(modified_image.size[0], 100)
        self.assertEqual(modified_image.size[1], 100)

    def test_response_larger_image(self):
        image = initialize_request_image('/')
        larger_image = initialize_request_image('/?width=%d' % (image.size[0] * 2))

        self.assertEqual(image.size[0] * 2, larger_image.size[0])
        self.assertEqual(image.size[1] * 2, larger_image.size[1])

    def test_image_sizes_are_integers(self):
        image = initialize_request_image('/?width=100.432')
        self.assertEqual(image.size[0], 100)

        image = initialize_request_image('/?height=150.432')
        self.assertEqual(image.size[1], 150)


class ImageQualityResponse(TestCase):
    def test_full_quality_image(self):
        image = initialize_request_image('/?quality=100')

        image_path = os.path.dirname(os.path.realpath(__file__)) + '/test_resources/frame.jpg'
        expected_image = Image.open(image_path)

        i1d = StringIO.StringIO()
        image.save(i1d, 'jpeg')

        i2d = StringIO.StringIO()
        expected_image.save(i2d, 'jpeg')

        data_size_diff = abs(float(i1d.len) / i2d.len - 1)

        self.assertTrue(data_size_diff < 0.005)

    def test_variable_quality_image(self):
        lower_quality_image = initialize_request_image('/?quality=80')
        i1d = StringIO.StringIO()
        lower_quality_image.save(i1d, 'jpeg')

        even_lower_quality_image = initialize_request_image('/?quality=20')
        i2d = StringIO.StringIO()
        even_lower_quality_image.save(i2d, 'jpeg')

        self.assertTrue(i1d.len > i2d.len)


class ImageUploaderTest(TestCase):
    def test_simple(self):
        c = Client()

        image_path = os.path.dirname(os.path.realpath(__file__)) + '/test_resources/frame.jpg'
        with open(image_path, 'r') as fp:
            response = c.post('/upload/', {'attachment': fp})
            fp.seek(0,2) # go to end
            print fp.tell()
        self.assertEqual(response.content, 'ok')


    # try all accepted file formats
    # try invalid file format
    # try file size limits
    # test to ensure that only valid image files are accepted
    # try retrieving the uploaded image
    # try using the wrong argument for file
    # fail basic validation
    # pass basic validation
    # test uploading thousands of files? may be a little intensive, but good for testing memory leaks and forgotten file closing
