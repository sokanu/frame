from django.test import Client
from django.test import TestCase

# Create your tests here.

class ImageViewTestCase(TestCase):
    def test_request(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(response.content, 'bok')
