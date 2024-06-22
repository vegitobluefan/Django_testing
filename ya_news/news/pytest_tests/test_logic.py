from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from django.contrib.auth import get_user_model

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


User = get_user_model()


@pytest.mark.django_db
def test_anonymous_cant_create_comment(
    news_detail,
    client,
    comment_data,
    comments_before_changes
):
    client.post(news_detail, data=comment_data)
    comments_count = Comment.objects.count()
    assert comments_count == comments_before_changes


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    news_detail,
    author_client,
    comment_data,
    comments_before_changes
):
    comments_before_request = comments_before_changes
    author_client.post(news_detail, data=comment_data)
    comments_count = Comment.objects.count()
    assert comments_count == comments_before_request + 1


@pytest.mark.django_db
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


@pytest.mark.django_db
def test_author_can_edit_comment(
    comment_edit,
    news_detail,
    comment,
    author_client,
    comment_data
):
    response = author_client.post(comment_edit, data=comment_data)
    assertRedirects(response, f'{news_detail}#comments')
    comment.refresh_from_db()
    assert comment.text == comment_data['text']
    assert comment.news == comment_data['news']
    assert comment.author == comment_data['author']


@pytest.mark.django_db
def test_author_can_delete_comment(
    get_comment_id,
    comment_delete,
    news_detail,
    author_client,
    comments_before_changes,
):
    comments_before_request = comments_before_changes
    get_comment = Comment.objects.get(id=get_comment_id)
    response = author_client.delete(comment_delete)
    assertRedirects(response, f'{news_detail}#comments')
    assert Comment.objects.count() == comments_before_request - 1
    assert get_comment not in Comment.objects.all()


@pytest.mark.django_db
def test_user_cant_edit_comment(
    comment_edit,
    comment,
    admin_client,
    comment_data
):
    response = admin_client.post(comment_edit, data=comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_data['text']
    assert comment.news == comment_data['news']
    assert comment.author == comment_data['author']


@pytest.mark.django_db
def test_user_cant_delete_comment(
    comment_delete,
    get_comment_id,
    admin_client,
    comments_before_changes
):
    comments_before_request = comments_before_changes
    get_comment = Comment.objects.get(id=get_comment_id)
    response = admin_client.delete(comment_delete, args=get_comment_id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before_request
    assert get_comment in Comment.objects.all()
