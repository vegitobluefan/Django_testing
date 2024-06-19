from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.NOTES_BEFORE_CHANGES = Note.objects.count()
        cls.URL_USERS_LOGIN = reverse('users:login')
        cls.URL_ADD_NOTES = reverse('notes:add')
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URL_NOTES_DELETE = reverse('notes:delete', args=(cls.note.slug,))
        cls.URL_ADD_NOTES_SUCCESS = reverse('notes:success')


    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.URL_ADD_NOTES, data=self.form_data)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_CHANGES)

    def test_user_can_create_note(self):
        response = self.author_logged.post(
            self.URL_ADD_NOTES,
            data=self.form_data
        )
        self.assertRedirects(response, self.URL_ADD_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_CHANGES + 1)
        note = Note.objects.order_by('id').last()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_same_slugs(self):
        self.form_data['slug'] = self.note.slug
        response = self.author_logged.post(
            self.URL_ADD_NOTES,
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_CHANGES)

    def test_author_can_edit_note(self):
        response = self.author_logged.post(
            self.URL_NOTES_EDIT,
            data=self.form_data
        )
        self.assertRedirects(response, self.URL_ADD_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_CHANGES)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_author_can_delete_note(self):
        response = self.author_logged.post(self.URL_NOTES_DELETE)
        self.assertRedirects(response, self.URL_ADD_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_CHANGES - 1)

    def test_user_cant_edit_note(self):
        response = self.reader_logged.post(
            self.URL_NOTES_EDIT,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_user_cant_delete_note(self):
        response = self.reader_logged.post(self.URL_NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_CHANGES)
