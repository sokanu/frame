from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from images.views import ImageUploaderView
from images.views import ImageTestCaseViewer
from images.views import ImageView

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/$', ImageUploaderView.as_view()),
    url(r'^(?P<image_identifier>[^/]+)/$', ImageView.as_view(), name='image'),

    # TODO: serving static assets is an issue for test cases; how do we fix?
    url(r'^test_media/(?P<local_filename>[^/]+)$', ImageTestCaseViewer.as_view(), name='image_test_case_viewer'),
) 

# Serving Locally Stored Media Files
# ----------------------------------
# media files are served from the media directory via dj_static. The configuration
# can be found in frame/wsgi.py
