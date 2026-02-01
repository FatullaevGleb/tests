from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок автора',
            text='Текст заметки автора',
            slug='author-note',
            author=cls.author
        )
        Note.objects.create(
            title='Заголовок читателя',
            text='Текст заметки читателя',
            slug='reader-note',
            author=cls.reader
        )

    def test_notes_list_for_author(self):
        """В списке заметок автора есть только его заметки."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertEqual(object_list.count(), 1)

    def test_notes_list_for_reader(self):
        """В списке заметок читателя есть только его заметки."""
        self.client.force_login(self.reader)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)
        self.assertEqual(object_list.count(), 1)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def test_note_in_list_for_author(self):
        """Отдельная заметка передаётся в список заметок автора."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)


class TestFormPages(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def test_add_page_contains_form(self):
        """На страницу добавления заметки передаётся форма."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_contains_form(self):
        """На страницу редактирования заметки передаётся форма."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
