# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.photos.settings import PHOTO_UPLOAD_TO

class Album(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    user = models.ForeignKey(User, verbose_name=_('User'))
    created = models.DateTimeField(_('Created'))
    is_public = models.BooleanField(_('Public'), default=False, help_text=_('Anyone can add photos.'))

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'photos-photo-list', [self.pk]

    class Meta:
        ordering = ['-created']

def photo_upload_to(instance, filename):
    return '%s/%s/%s/%s' % (PHOTO_UPLOAD_TO, instance.user.id, instance.album.id, filename)

class Photo(models.Model):
    photo = models.ImageField(_('Photo'), upload_to=photo_upload_to)
    album = models.ForeignKey(Album, verbose_name=_('Album'))
    user = models.ForeignKey(User, verbose_name=_('User'))
    date = models.DateTimeField(_('Date'), auto_now_add=True)
    description = models.TextField(_('Description'), blank=True)

    @models.permalink
    def get_absolute_url(self):
        return 'photos-photo', [self.album.pk, self.pk]

    def delete(self, using=None):
        self.photo.delete()
        Comment.objects.filter(content_type=ContentType.objects.get_for_model(self), object_pk=self.pk).delete()
        super(Photo, self).delete(using)

    class Meta:
        ordering = ['date']


