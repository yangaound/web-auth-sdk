from django.urls import path

from .views import csrf_token, google_auth_cb, google_login, session_login

urlpatterns = [
    path('session/csrftoken', csrf_token),
    path('session/login', session_login),
    path('google/login', google_login),
    path('google/auth', google_auth_cb),
]
