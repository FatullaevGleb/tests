from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    news_id_for_args,
    form_data
):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    comments_count_before = Comment.objects.count()
    client.post(url, data=form_data)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client,
    author,
    news,
    news_id_for_args,
    form_data
):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    comments_count_before = Comment.objects.count()
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before + 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news_id_for_args):
    """Если комментарий содержит запрещённые слова, он не будет опубликован."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'}
    url = reverse('news:detail', args=news_id_for_args)
    comments_count_before = Comment.objects.count()
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response.context['form'],
        'text',
        errors=WARNING
    )
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, news_id_for_args):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    url_to_comments = reverse(
        'news:detail', args=news_id_for_args
    ) + '#comments'
    comments_count_before = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    comments_count_before = Comment.objects.count()
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client,
    comment,
    news_id_for_args,
    form_data
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    url_to_comments = reverse(
        'news:detail', args=news_id_for_args
    ) + '#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    reader_client,
    comment,
    form_data
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
