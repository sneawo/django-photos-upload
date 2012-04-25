from datetime import date, timedelta
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_any import any_model
from photos.models import *

class PhotosTestCase(TestCase):

    def setUp(self):
        self.user = any_model(User, is_active=True)
        self.user.set_password('test')
        self.user.save()

        result_login = self.client.login(username=self.user.username, password='test')
        self.assertTrue(result_login)

class AlbumsViewTestCase(PhotosTestCase):

    def test_list(self):
        any_model(Album, user__is_active=True)
        any_model(Album, user__is_active=True)
        any_model(Album, user__is_active=False)

        response = self.client.get(reverse('photos-album-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['album_list']), 2)

    def test_add(self):
        data = {'title': 'test'}
        response = self.client.post(reverse('photos-album-add'), data, follow=True)

        self.assertRedirects(response, reverse('photos-album-list'))
        self.assertTrue('test' in [album.title for album in response.context['album_list']])

        album = Album.objects.get(title=data['title'])
        self.assertEqual(album.created.date(), date.today())
        self.assertEqual(album.user, self.user)

class PhotosViewTestCase(PhotosTestCase):

    def test_list(self):
        album = any_model(Album, user__is_active=True)
        Photo.objects.create(user=album.user, album=album)
        Photo.objects.create(user=album.user, album=album)
        response = self.client.get(reverse('photos-photo-list', args=[album.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['album'], album)
        self.assertEqual(len(response.context['photo_list']), 2)

    def test_detail(self):
        album = any_model(Album, user__is_active=True)
        photo = Photo.objects.create(user=album.user, album=album)
        response = self.client.get(reverse('photos-photo', args=[album.id, photo.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['photo'], photo)

class PhotosDeleteViewTestCase(PhotosTestCase):

    def test_permission_error(self):
        album = any_model(Album, user__is_active=True)
        photo = Photo.objects.create(user=album.user, album=album)
        response = self.client.get(reverse('photos-photo-delete', args=[album.id, photo.id]))

        self.assertEqual(response.status_code, 403)

class PhotosCreateViewTestCase(PhotosTestCase):

    def test_permission_non_public_error(self):
        album = any_model(Album, user__is_active=True, is_public=False)
        response = self.client.get(reverse('photos-photo-add', args=[album.id]))

        self.assertEqual(response.status_code, 403)

    def test_permission_public_success(self):
        album = any_model(Album, user__is_active=True, is_public=True)
        response = self.client.get(reverse('photos-photo-add', args=[album.id]))

        self.assertEqual(response.status_code, 200)

    def test_permission_own_success(self):
        album = any_model(Album, user=self.user, is_public=False)
        response = self.client.get(reverse('photos-photo-add', args=[album.id]))

        self.assertEqual(response.status_code, 200)
