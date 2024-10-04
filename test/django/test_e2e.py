import pytest
from django.test import Client

from web_auth import ErrorCode

client = Client()


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
