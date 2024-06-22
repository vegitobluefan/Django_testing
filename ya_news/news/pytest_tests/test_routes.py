from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


client = pytest.lazy_fixture('client')
author = pytest.lazy_fixture('author_client')
reader = pytest.lazy_fixture('not_author_client')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('news_home'), client, HTTPStatus.OK),
        (pytest.lazy_fixture('user_login'), client, HTTPStatus.OK),
        (pytest.lazy_fixture('user_logout'), client, HTTPStatus.OK),
        (pytest.lazy_fixture('user_signup'), client, HTTPStatus.OK),
        (pytest.lazy_fixture('news_detail'), client, HTTPStatus.OK),
        (pytest.lazy_fixture('comment_edit'), author, HTTPStatus.OK),
        (pytest.lazy_fixture('comment_delete'), author, HTTPStatus.OK),
        (pytest.lazy_fixture('comment_edit'), reader, HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('comment_delete'), reader, HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.django_db
def test_pages_availability(url, parametrized_client, expected_status):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('comment_delete'),
        pytest.lazy_fixture('comment_edit'),
    )
)
@pytest.mark.django_db
def test_redirects(url, user_login, client):
    expected_url = f'{user_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
