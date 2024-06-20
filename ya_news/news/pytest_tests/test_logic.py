from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from django.contrib.auth import get_user_model

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


User = get_user_model()
form_data = {'text': 'Текст'}


def comments_before_changes():
    return Comment.objects.count()


@pytest.mark.django_db
def test_anonymous_cant_create_comment(news_detail, client):
    client.post(news_detail, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == comments_before_changes()


@pytest.mark.django_db
def test_authorized_user_can_create_comment(news_detail, author_client):
    comments_before_request = comments_before_changes()
    response = author_client.post(news_detail, data=form_data)
    assertRedirects(response, f'{news_detail}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == comments_before_request + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_bad_words_filter(news_detail, author_client):
    bad_words_data = {
        'text': f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'
    }
    response = author_client.post(news_detail, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == comments_before_changes()


@pytest.mark.django_db
def test_author_can_edit_comment(
    comment_edit,
    news_detail,
    comment,
    author_client
):
    response = author_client.post(comment_edit, data=form_data)
    assertRedirects(response, f'{news_detail}#comments')
    comment.refresh_from_db()
    assert comment.text == 'Текст'


@pytest.mark.django_db
def test_author_can_delete_comment(
    comment_delete,
    news_detail,
    author_client
):
    comments_before_request = comments_before_changes()
    response = author_client.delete(comment_delete)
    assertRedirects(response, f'{news_detail}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == comments_before_request - 1


@pytest.mark.django_db
def test_user_cant_edit_comment(
    comment_edit,
    comment,
    admin_client
):
    response = admin_client.post(comment_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


@pytest.mark.django_db
def test_user_cant_delete_comment(
    comment_delete,
    admin_client
):
    comments_before_request = comments_before_changes()
    response = admin_client.delete(comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == comments_before_request
