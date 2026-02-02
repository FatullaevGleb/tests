import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


def test_news_count(many_news, client, home_url):

    response = client.get(home_url)

    object_list = response.context['object_list']
    news_count = object_list.count()

    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(many_news, client, home_url):

    response = client.get(home_url)

    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


def test_comments_order(many_comments, client, detail_url, news):

    response = client.get(detail_url)

    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)

    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url):

    response = client.get(detail_url)

    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):

    response = author_client.get(detail_url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
