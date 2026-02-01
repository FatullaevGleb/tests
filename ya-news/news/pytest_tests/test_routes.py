from http import HTTPStatus

import pytest
import pytest_lazyfixture
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    """Главная страница доступна анонимному пользователю."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_availability_for_anonymous_user(client, news_id_for_args):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup', 'users:logout')
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name):
    """
    Страницы регистрации, входа и выхода
    доступны анонимным пользователям.
    """
    url = reverse(name)

    if name == 'users:logout':
        response = client.post(url)
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)
    else:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest_lazyfixture.lazy_fixture('author_client'), HTTPStatus.OK),
        (
            pytest_lazyfixture.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(
    parametrized_client, name, comment, expected_status
):
    """
    Страницы редактирования и удаления комментария
    доступны только автору.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, name, comment):
    """
    Анонимный пользователь перенаправляется на логин
    при доступе к редактированию/удалению.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
