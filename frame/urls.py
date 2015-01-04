from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from images.views import ImageUploaderView
from images.views import ImageView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'frame.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/$', ImageUploaderView.as_view()),
    url(r'^(?P<image_identifier>[^/]+)/$', ImageView.as_view(), name='image')
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
