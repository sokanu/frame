from django.conf.urls import patterns, include, url
from django.contrib import admin
from images.views import ImageView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'frame.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', ImageView.as_view())
)
