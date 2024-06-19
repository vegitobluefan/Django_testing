from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.tests.test_routes import User


class TestContent(TestCase):
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
        cls.URL_NOTES_LIST = reverse('notes:list')
        cls.URL_ADD_NOTES = reverse('notes:add')
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_for_users(self):
        users = (
            (self.author_logged, True),
            (self.reader_logged, False),
        )
        for user, status in users:
            with self.subTest():
                response = user.get(self.URL_NOTES_LIST)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, status)

    def test_given_form(self):
        urls = (
            self.URL_ADD_NOTES,
            self.URL_NOTES_EDIT,
        )
        for url in urls:
            with self.subTest():
                response = self.author_logged.get(url)
                self.assertIn('form', response.context)
