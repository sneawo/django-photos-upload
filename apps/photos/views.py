# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from sorl.thumbnail.shortcuts import get_thumbnail
from pure_pagination.mixins import PaginationMixin
from apps.photos.models import Album, Photo
from apps.photos.forms import AlbumForm, PhotoUploadForm
from apps.photos.settings import PHOTO_PAGINATE_BY

def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

class LoginRequiredMixin(object):
    """ View mixin which verifies that the user has authenticated. """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

class AlbumListView(LoginRequiredMixin, ListView):
    model = Album
    context_object_name = "album_list"
    queryset = Album.objects.filter(user__is_active=True)

class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm

    def get_success_url(self):
       return reverse('photos-album-list')

    def form_valid(self, form):
        messages.success(self.request, _("Album added."))
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.created = datetime.now()
        return super(AlbumCreateView, self).form_valid(form)

class PhotoListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = Photo
    context_object_name = "photo_list"
    paginate_by = PHOTO_PAGINATE_BY

    def get_queryset(self):
        self.album = get_object_or_404(Album, pk=self.kwargs['pk'])
        return Photo.objects.filter(album=self.album, user__is_active=True)

    def get_context_data(self, **kwargs):
      context = super(PhotoListView, self).get_context_data(**kwargs)
      context['album'] = self.album
      return context

class PhotoDetailView(DetailView):
    model = Photo

    def get_context_data(self, **kwargs):
      context = super(PhotoDetailView, self).get_context_data(**kwargs)
      context['album'] = self.object.album
      return context

class PhotoCreateView(LoginRequiredMixin, CreateView):
    """ View for upload with jQuery File Upload Plugin """

    model = Photo
    form_class = PhotoUploadForm

    def get_context_data(self, **kwargs):
      context = super(PhotoCreateView, self).get_context_data(**kwargs)
      context['album'] = self.album
      return context

    def form_valid(self, form):
        """ Returns json response instead redirect """
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.album = self.album
        self.object.save()
        f = self.request.FILES.get('photo')
        thumbnail = get_thumbnail(self.object.photo, "100x100")
        data = [{'name': f.name,
                 'url': self.object.photo.url,
                 'thumbnail_url': thumbnail.url,
                 'delete_url': reverse('photos-photo-delete', args=[self.album.pk, self.object.id]),
                 'delete_type': "DELETE"}]
        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def dispatch(self, request, *args, **kwargs):
        self.album = get_object_or_404(Album, pk=kwargs['pk'])
        if self.album.is_public or self.album.user == request.user:
            return super(PhotoCreateView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

class PhotoDeleteView(LoginRequiredMixin, DeleteView):
    model = Photo

    def get_success_url(self):
        return reverse('photos-photo-list', args=[self.kwargs['album_pk']])

    def get(self, *args, **kwargs):
        """ Skip confirmation page """
        return self.delete(self.request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user != request.user:
            raise PermissionDenied
        self.object.delete()
        if request.is_ajax():
            response = JSONResponse(True, {}, response_mimetype(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect(self.get_success_url())

class JSONResponse(HttpResponse):
    """ JSON response class. """

    def __init__(self,obj='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = simplejson.dumps(obj,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)