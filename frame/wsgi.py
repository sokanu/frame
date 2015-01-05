"""
WSGI config for frame project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frame.settings")

from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling

# Serve locally stored media files via Django Static
application = Cling(MediaCling(get_wsgi_application()))
