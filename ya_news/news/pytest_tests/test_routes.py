from http import HTTPStatus

import pytest
import pytest_lazyfixture
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.mark.parametrize(
    'url_name, args',
    [
        ('news:home', None),
        ('news:detail', 'news_id'),
        ('users:login', None),
        ('users:signup', None),
        ('users:logout', None),
    ]
)
def test_pages_availability_for_anonymous_user(client, news, url_name, args):

    if args == 'news_id':
        url = reverse(url_name, args=(news.id,))
    else:
        url = reverse(url_name)

    if url_name == 'users:logout':
        response = client.post(url)
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)
    else:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (pytest_lazyfixture.lazy_fixture('author_client'), HTTPStatus.OK),
        (
            pytest_lazyfixture.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
    ],
)
@pytest.mark.parametrize(
    'url_name',
    ['news:edit', 'news:delete'],
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, url_name, comment, expected_status
):

    url = reverse(url_name, args=(comment.id,))

    response = parametrized_client.get(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_name',
    ['news:edit', 'news:delete'],
)
def test_redirect_for_anonymous_client(client, url_name, comment, login_url):
    url = reverse(url_name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)

    assertRedirects(response, expected_url)
