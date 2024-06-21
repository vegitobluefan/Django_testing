import pytest
from django.test.client import Client
from django.urls import reverse
from django.conf import settings

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )
    return news


@pytest.fixture
def news_on_page():
    all_news = [
        News(title=f'Новость {index}', text='Просто текст.')
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        author=author,
        news=news,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def edit_comment(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_comment(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def user_login():
    return reverse('users:login')


@pytest.fixture
def user_logout():
    return reverse('users:logout')


@pytest.fixture
def user_signup():
    return reverse('users:signup')


@pytest.fixture
def news_home():
    return reverse('news:home')


@pytest.fixture
def news_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def comment_edit(comment):
    return reverse('news:edit', args=(comment.id,))
