from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('news_home'),
        pytest.lazy_fixture('user_login'),
        pytest.lazy_fixture('user_logout'),
        pytest.lazy_fixture('user_signup'),
    )
)
@pytest.mark.django_db
def test_pages_availability_for_all_users(client, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_news_availability_for_all_users(client, news_detail):
    response = client.get(news_detail)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('comment_edit'),
        pytest.lazy_fixture('comment_delete'),
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, url, expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('comment_edit'),
        pytest.lazy_fixture('comment_delete'),
    ),
)
@pytest.mark.django_db
def test_redirects(url, user_login, client):
    expected_url = f'{user_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
