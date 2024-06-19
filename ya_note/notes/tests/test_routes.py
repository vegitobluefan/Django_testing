from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_logged = Client()
        cls.reader_logged = Client()
        cls.author_logged.force_login(cls.author)
        cls.reader_logged.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author,
        )
        cls.LOGIN_URL = reverse('users:login')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.REGISTRATION_URL = reverse('users:signup')
        cls.HOME_URL = reverse('notes:home')
        cls.URL_NOTES_LIST = reverse('notes:list')
        cls.URL_ADD_NOTES = reverse('notes:add')
        cls.URL_ADD_NOTES_SUCCESS = reverse('notes:success')
        cls.URL_NOTES_DETAIL = reverse('notes:detail', args=(cls.note.slug,))
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URL_NOTES_DELETE = reverse('notes:delete', args=(cls.note.slug,))

    def test_home_page(self):
        urls = (
            self.HOME_URL,
            self.LOGIN_URL,
            self.LOGOUT_URL,
            self.REGISTRATION_URL,
        )
        for url in urls:
            with self.subTest():
                response = self.reader_logged.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_different_users(self):
        users = (
            (self.author_logged, HTTPStatus.OK),
            (self.reader_logged, HTTPStatus.NOT_FOUND),
        )
        for client, status in users:
            for url in (
                self.URL_NOTES_EDIT,
                self.URL_NOTES_DELETE,
                self.URL_NOTES_DETAIL,
            ):
                with self.subTest():
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_auth_users(self):
        urls = (
            self.URL_NOTES_LIST,
            self.URL_ADD_NOTES,
            self.URL_ADD_NOTES_SUCCESS,
        )
        for url in urls:
            with self.subTest():
                response = self.reader_logged.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.URL_NOTES_LIST,
            self.URL_ADD_NOTES_SUCCESS,
            self.URL_ADD_NOTES,
            self.URL_NOTES_EDIT,
            self.URL_NOTES_DELETE,
            self.URL_NOTES_DETAIL,
        )
        for url in urls:
            with self.subTest():
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
