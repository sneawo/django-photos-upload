# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from apps.photos.views import *

urlpatterns = patterns('',
    url(r'^$', AlbumListView.as_view(), name='photos-album-list'),
    url(r'^add/$', AlbumCreateView.as_view(), name='photos-album-add'),
    url(r'^(?P<pk>\d+)/$', PhotoListView.as_view(), name='photos-photo-list'),
    url(r'^(?P<pk>\d+)/add/$', PhotoCreateView.as_view(), name='photos-photo-add'),
    url(r'^(?P<album_pk>\d+)/(?P<pk>\d+)/$', PhotoDetailView.as_view(), name='photos-photo'),
    url(r'^(?P<album_pk>\d+)/(?P<pk>\d+)/delete/$', PhotoDeleteView.as_view(), name='photos-photo-delete'),
)