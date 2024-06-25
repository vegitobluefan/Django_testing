from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm
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

    def test_notes_for_author(self):
        response = self.author_logged.get(self.URL_NOTES_LIST)
        self.assertIn(
            self.note,
            response.context['object_list']
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_for_reader(self):
        response = self.reader_logged.get(self.URL_NOTES_LIST)
        self.assertNotIn(
            self.note,
            response.context['object_list']
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_given_form(self):
        urls = (
            self.URL_ADD_NOTES,
            self.URL_NOTES_EDIT,
        )
        for url in urls:
            with self.subTest():
                response = self.author_logged.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
