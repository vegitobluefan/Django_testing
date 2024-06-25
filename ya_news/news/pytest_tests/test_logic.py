from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_cant_create_comment(
    news_detail,
    client,
):
    client.post(news_detail)
    assert Comment.objects.count() == 0


def test_authorized_user_can_create_comment(
    author,
    news,
    news_detail,
    author_client,
    form_data
):
    author_client.post(news_detail, data=form_data)
    assert Comment.objects.count() == 1
    get_comment = Comment.objects.get()
    assert get_comment.text == form_data['text']
    assert get_comment.author == author
    assert get_comment.news == news


def test_bad_words_filter(news_detail, author_client, comments_before_changes):
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
    assert comments_count == comments_before_changes


def test_author_can_edit_comment(
    comment,
    author,
    news,
    comment_edit,
    news_detail,
    author_client,
    form_data
):
    response = author_client.post(comment_edit, data=form_data)
    assertRedirects(response, f'{news_detail}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_author_can_delete_comment(
    comment,
    comment_delete,
    news_detail,
    author_client,
):
    response = author_client.delete(comment_delete)
    assertRedirects(response, f'{news_detail}#comments')
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_cant_edit_comment(
    comment,
    comment_edit,
    admin_client,
):
    response = admin_client.post(comment_edit)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_user_cant_delete_comment(
    comment,
    comment_delete,
    admin_client,
):
    response = admin_client.delete(comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.id).exists() is True
