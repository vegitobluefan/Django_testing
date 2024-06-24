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
    comment_data,
    comments_before_changes
):
    client.post(news_detail, data=comment_data)
    comments_count = Comment.objects.count()
    assert comments_count == comments_before_changes


def test_authorized_user_can_create_comment(
    comment,
    author,
    news,
    news_detail,
    author_client,
    comment_data,
    comments_before_changes
):
    comments_before_request = comments_before_changes
    author_client.post(news_detail, data=comment_data)
    comments_count = Comment.objects.count()
    get_comment = Comment.objects.get(id=comment.id)
    assert comments_count == comments_before_request + 1
    assert get_comment.text == comment_data['text']
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
    comment_data
):
    response = author_client.post(comment_edit, data=comment_data)
    assertRedirects(response, f'{news_detail}#comments')
    comment.refresh_from_db()
    assert comment.text == comment_data['text']
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
    get_comment = Comment.objects.filter(id=comment.id).exists()
    assert get_comment is False


def test_user_cant_edit_comment(
    comment,
    author,
    news,
    comment_edit,
    admin_client,
    comment_data
):
    comment_text_before = comment.text
    response = admin_client.post(comment_edit, data=comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text_before
    assert comment.author == author
    assert comment.news == news

def test_user_cant_delete_comment(
    comment,
    comment_delete,
    admin_client,
):
    get_comment = Comment.objects.filter(id=comment.id).exists()
    response = admin_client.delete(comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert get_comment is True
