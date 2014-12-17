from django.test import Client
from django.test import TestCase
import os


class ImageViewTestCase(TestCase):
    def test_request(self):
        c = Client()
        response = c.get('/')

        image_path = os.path.dirname(os.path.realpath(__file__)) + '/test_resources/frame.jpg'
        expected_data = open(image_path, 'r').read()

        self.assertEqual(response.content, expected_data)
