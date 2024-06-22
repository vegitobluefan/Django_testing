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


    def test_availability_for_users(self):
        pages_users_statuses = (
            (self.URL_NOTES_DETAIL, self.author_logged, HTTPStatus.OK),
            (self.URL_NOTES_EDIT, self.author_logged, HTTPStatus.OK),
            (self.URL_NOTES_DELETE, self.author_logged, HTTPStatus.OK),
            (self.HOME_URL, self.client, HTTPStatus.OK),
            (self.REGISTRATION_URL, self.client, HTTPStatus.OK),
            (self.LOGIN_URL, self.client, HTTPStatus.OK),
            (self.LOGOUT_URL, self.client, HTTPStatus.OK),
            (self.URL_NOTES_DETAIL, self.reader_logged, HTTPStatus.NOT_FOUND),
            (self.URL_NOTES_EDIT, self.reader_logged, HTTPStatus.NOT_FOUND),
            (self.URL_NOTES_DELETE, self.reader_logged, HTTPStatus.NOT_FOUND),
        )
        for page, user, status in pages_users_statuses:
            with self.subTest(page=page, user=user, status=status):
                self.assertEqual(user.get(page).status_code, status)

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
