import json
import logging

import jwt
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import QueryDict
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from requests_oauthlib import OAuth2Session


def csrf_token(request):
    csrftoken = get_token(request)
    res = JsonResponse({settings.CSRF_COOKIE_NAME: csrftoken})
    res.set_cookie(settings.CSRF_COOKIE_NAME, csrftoken)
    return res


@transaction.atomic
def session_login(request):
    try:
        if request.content_type == 'application/json':
            data = json.load(request)
        else:
            data = QueryDict(request.POST.urlencode())
    except Exception as e:
        logging.warning(str(e))
        raise PermissionDenied

    qs = User.objects.filter(username=data.get('username'))
    if not qs.exists():
        msg = 'The user {username} does not exist.'.format(username=data.get('username'))
        logging.warning(msg)
        raise PermissionDenied

    user = qs.first()
    if not user.check_password(data.get('password')):
        msg = 'Incorrect password entered for user {username}.'.format(username=data.get('username'))
        logging.warning(msg)
        raise PermissionDenied

    login(
        request,
        user,
        backend='django.contrib.auth.backends.ModelBackend',
    )
    return HttpResponse()


def google_login(req):
    conf = settings.OAUTH2['google']
    oauth = OAuth2Session(
        conf['client_id'],
        redirect_uri=conf['redirect_uri'],
        scope=conf['scope'],
        state=req.GET.get('next', settings.LOGIN_REDIRECT_URL),
    )
    authorization_url, _ = oauth.authorization_url(
        conf['auth_uri'],
        req.GET.get('next', ''),
        access_type='offline',
        prompt='consent',
    )
    return HttpResponseRedirect(authorization_url)


@transaction.atomic
def google_auth_cb(request):
    conf = settings.OAUTH2['google']

    if not request.GET.get('code'):
        return JsonResponse({'error': request.GET.get('error', None)}, 400)

    try:
        oauth = OAuth2Session(conf['client_id'], redirect_uri=conf['redirect_uri'])
        idp_resp = oauth.fetch_token(
            conf['token_uri'],
            code=request.GET.get('code'),
            client_secret=conf['client_secret'],
        )

        id_token = idp_resp['id_token']
        state = request.GET.get('state')
        open_info = jwt.decode(id_token, options={'verify_signature': False})

        try:
            user = User.objects.get(email=open_info['email'])
        except User.DoesNotExist:  # pylint: disable=no-member
            user = User(
                username=open_info['email'],
                first_name=open_info['given_name'],
                last_name=open_info['family_name'],
                email=open_info['email'],
            )
            user.save()

        login(
            request,
            user,
            backend='django.contrib.auth.backends.ModelBackend',
        )
        resp = HttpResponseRedirect(state)
    except Exception as e:
        resp = JsonResponse({'error': str(e)}, status=500)

    return resp
