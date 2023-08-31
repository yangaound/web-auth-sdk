from django.http.response import JsonResponse

from web_auth import AuthException, make_context
from web_auth.django import DjangoBridge

context = make_context(
    bridge_class=DjangoBridge,
)


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthException as e:
            return JsonResponse({'message': e.message, 'code': e.code}, status=403)

    return wrapper


@error_handler
@context('view_ticket')
def list_tickets(request):
    return JsonResponse([], safe=False)


@error_handler
@context('delete_tickettype')
def delete_tickets(request):
    return JsonResponse([], safe=False)
