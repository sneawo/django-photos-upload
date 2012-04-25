# -*- coding: utf-8 -*-
from django import forms
from apps.photos.models import Album, Photo

class AlbumForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = ['title', 'is_public']

class PhotoUploadForm(forms.ModelForm):

    class Meta:
        model = Photo
        fields = ['photo']