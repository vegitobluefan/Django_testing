import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_pagination(news_on_page, news_home, client):
    response = client.get(news_home)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorting(news_home, client):
    response = client.get(news_home)
    object_list = response.context['object_list']
    news_dates = [news.date for news in object_list]
    sorted_news = sorted(news_dates, reverse=True)
    assert news_dates == sorted_news


@pytest.mark.django_db
def test_comments_sorting(news_detail, client):
    response = client.get(news_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_unavailable_form_for_anonymous(news_detail, client):
    response = client.get(news_detail)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_available_form_for_authorized_users(news_detail, author_client):
    response = author_client.get(news_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
