import pytest
from django.contrib.auth.models import User
from django.test import Client

from web_auth import ErrorCode

client = Client()


def test_session_csrftoken():
    c = Client()
    assert c.cookies.get('csrftoken') is None

    resp = c.get('/session/csrftoken')
    assert resp.status_code == 200
    assert c.cookies['csrftoken'] is not None
    assert resp.json()['csrftoken'] is not None


@pytest.mark.django_db
def test_session_login():
    user = User(username='yangaound@gmail.com', email='yangaound@gmail.com')
    user.set_password('cwb+123')
    user.save()

    csrf_resp = client.get('/session/csrftoken')
    resp = client.post(
        '/session/login',
        {'username': 'yangaound@gmail.com', 'password': 'cwb+123'},
        X_CSRFTOKEN=csrf_resp.json()['csrftoken'],
    )
    assert resp.status_code == 200


def test_list_tickets(bearer_jwt_token):
    resp = client.get('/list-tickets', HTTP_AUTHORIZATION=bearer_jwt_token)
    assert resp.status_code == 200

    resp = client.get('/list-tickets', HTTP_AUTHORIZATION='')
    assert resp.status_code == 403
    assert resp.json()['code'] == ErrorCode.UNAUTHORIZED


@pytest.mark.django_db
def test_delete_tickets(bearer_jwt_token):
    resp = client.delete('/delete-tickets', HTTP_AUTHORIZATION=bearer_jwt_token)
    assert resp.status_code == 403
    assert resp.json()['code'] == ErrorCode.PERMISSION_DENIED
