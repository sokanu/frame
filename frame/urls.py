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
    url(r'^image/(?P<image_identifier>[^/]+)/$', ImageView.as_view(), name='image'),
) 

# apply authentication middleware on everything but the image urls
from urlmiddleware.conf import middleware, mpatterns
middlewarepatterns = mpatterns('',
    middleware(r'^(?!image)', 'django.contrib.sessions.middleware.SessionMiddleware'),
    middleware(r'^(?!image)', 'django.contrib.auth.middleware.AuthenticationMiddleware'),
    middleware(r'^(?!image)', 'django.contrib.auth.middleware.SessionAuthenticationMiddleware'),
)

# Serving Locally Stored Media Files
# ----------------------------------
# media files are served from the media directory via dj_static. The configuration
# can be found in frame/wsgi.py
