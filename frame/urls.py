from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from images.views import ImageUploaderView
from images.views import ImageView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('',
    #url(r'^$', csrf_exempt(ImageUploaderView.as_view())),
    url(r'^$', ImageUploaderView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<image_identifier>[^/]+)/$', ImageView.as_view(), name='image'),
) 

# Serving Locally Stored Media Files
# ----------------------------------
# media files are served from the media directory via dj_static. The configuration
# can be found in frame/wsgi.py
