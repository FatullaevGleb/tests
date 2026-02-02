from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


def test_anonymous_user_cant_create_comment(client, detail_url, form_data):

    comments_count_before = Comment.objects.count()

    client.post(detail_url, data=form_data)

    comments_count_after = Comment.objects.count()

    assert comments_count_after == comments_count_before


def test_user_can_create_comment(
        author_client,
        author,
        news,
        detail_url,
        form_data
):

    comments_count_before = Comment.objects.count()

    response = author_client.post(detail_url, data=form_data)

    comments_count_after = Comment.objects.count()
    assertRedirects(response, f'{detail_url}#comments')
    assert comments_count_after == comments_count_before + 1

    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):

    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'}
    comments_count_before = Comment.objects.count()

    response = author_client.post(detail_url, data=bad_words_data)

    comments_count_after = Comment.objects.count()
    assertFormError(
        response.context['form'],
        'text',
        errors=WARNING
    )
    assert comments_count_after == comments_count_before


def test_author_can_delete_comment(
        author_client,
        comment,
        delete_url,
        detail_url
):

    comments_count_before = Comment.objects.count()

    response = author_client.delete(delete_url)

    comments_count_after = Comment.objects.count()
    assertRedirects(response, f'{detail_url}#comments')
    assert comments_count_after == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(
        reader_client,
        comment,
        delete_url
):

    comments_count_before = Comment.objects.count()

    response = reader_client.delete(delete_url)

    comments_count_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_after == comments_count_before


def test_author_can_edit_comment(
        author_client, comment,
        edit_url,
        detail_url,
        form_data
):

    response = author_client.post(edit_url, data=form_data)

    comment.refresh_from_db()
    assertRedirects(response, f'{detail_url}#comments')
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        comment,
        edit_url,
        form_data
):

    response = reader_client.post(edit_url, data=form_data)

    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text != form_data['text']
