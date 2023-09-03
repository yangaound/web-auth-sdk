# web-auth-sdk
<img src="https://img.shields.io/github/actions/workflow/status/yangaound/web-auth-sdk/makefile-ci.yml?branch=main" /><img src="https://img.shields.io/pypi/v/web-auth-sdk" />
<img src="https://img.shields.io/badge/license-MIT-green.svg" />
<img src="https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg" />

The web-auth-sdk is an authorization SDK that is used to build protected Web APIs.
It provides the ability to intercept incoming requests and inject custom logic for authentication and authorization
before the request reaches the view function.

In addition, it supports Google OAuth2 for logging in and session logging in.

To access protected APIs, clients should authenticate by passing authorizations. For example, a JWT key can be used as follows:
   ```shell
     curl 'http://api.example.com/resources' -H 'Authorization: Bearer eyJ1c2VyX2lkIjoxLCJwZXJtaXNzaW9uX2JpdG'
     curl 'http://api.example.com/resources?access_token=eyJ1c2VyX2lkIjoxLCJwZXJtaXNzaW9uX2JpdG'
     curl 'http://api.example.com/resources' --cookie 'access_token=eyJ1c2VyX2lkIjoxLCJwZXJtaXNzaW9uX2JpdG'
   ```
>  **_TIP:_**
> When utilizing FastAPI, click the lock symbol on Swagger UI to include your JWT.
> Run `make startup` for a quick preview.
![img.png](usr/share/img/IncludeJWT.png)

## Requirements
- Python 3.8+
- FastAPI 0.80+ (recommended)
- Django 4.0+ (optional)
- Flask 2.0+ (optional)

## Installation
   ```shell
   pip install web-auth-sdk
   ```
or
   ```shell
   git clone https://github.com/yangaound/web-auth-sdk
   cd web-auth-sdk && poetry install
   ```

## Permission Representation
1. Permission list, located at `usr/etc/permissions.json` file:
    ```python
    permissions = [
        {'bitmask_idx': 0, 'codename': 'add_order', 'name': 'Can add order', 'service': 'order'},
        {'bitmask_idx': 1, 'codename': 'change_order', 'name': 'Can change order', 'service': 'order'},
        {'bitmask_idx': 2, 'codename': 'delete_order', 'name': 'Can delete order', 'service': 'order'},
        {'bitmask_idx': 3, 'codename': 'view_order', 'name': 'Can view order', 'service': 'order'},
        {'bitmask_idx': 4, 'codename': 'add_tickettype', 'name': 'Can add ticket type', 'service': 'order'},
        {'bitmask_idx': 5, 'codename': 'change_tickettype', 'name': 'Can change ticket type', 'service': 'order'},
        {'bitmask_idx': 6, 'codename': 'view_tickettype', 'name': 'Can view ticket type', 'service': 'order'},
        {'bitmask_idx': 7, 'codename': 'delete_tickettype', 'name': 'Can delete ticket type', 'service': 'order'},
    ]
    ```

2. How to grant permissions?

   Permissions are encoded using a bitmask of length n that is a multiple of 24.
   Each permission is represented by a 1 on the corresponding `bitmask_idx`-th position in the bitmask, indicating that
   the permission is granted.


3. Base64-encoded the bitmask
    
    | Bitmask                                          | Base64-encoded |
    |--------------------------------------------------|----------------|
    | 111111111111111111111111111111110111111101111111 | /////39/       |

4. Decoded/Encoded JWT
    ```json
    {
      "user_id": 1,
      "permission_bitmask": "/////39/",
      "iat": 1678798980,
      "exp": 1678800187
    }
    ```
    ```text
    eyJ1c2VyX2lkIjoxLCJwZXJtaXNzaW9uX2JpdG1hc2siOiIvLy8vLzM5LyIsImlhdCI6MTY3ODc5ODk4MCwiZXhwIjoxNjc4ODAwMTg3fQ
    ```
   

## Development
- ### FastAPI

    ```python
    import web_auth
    
      
    @fastapi.get('/tickets')
    @web_auth.permissions('view_ticket') # Iterable[str] are acceptable
    async def list_tickets() -> list: 
        return []
    ```
  
- ### Django

    ```python
    import web_auth
    from web_auth.django import DjangoBridge
    
  
    web_auth.configure(bridge_class=DjangoBridge)
    
    @web_auth.permissions('view_ticket')
    def list_tickets(request): 
        pass
  
    urlpatterns = [django.urls.path('list-tickets', list_tickets)]
    ```

- ### Flask

    ```python
    import web_auth
    from web_auth.flask import FlaskBridge
    
  
    web_auth.configure(bridge_class=FlaskBridge)
    
    @flask.route('/tickets', methods=['GET'])
    @web_auth.permissions('view_ticket')
    def list_tickets() -> list: 
        return []
    ```

- ### Use instanced context

    ```python
    import web_auth
    
  
    context = web_auth.make_context(bridge_class='web_auth.fastapi.FastapiBridge')
    
    @fastapi.get('/tickets')
    @context.permissions('view_ticket')
    async def list_tickets() -> list: 
        return []
    ```

- ### Retrieve the consumer

    ```python
    import fastapi
    import web_auth
    
  
    @fastapi.get('/profile')
    @web_auth.permissions(['view_directory'])
    def get_profile(consumer: web_auth.Consumer) -> dict:
        return {
            'user': consumer.user.dict(),
            'directories': 'get_directories(consumer.user.user_id)',
        }
    ```
  
- ### Implement Fine-Grained Permission Control

    ```python
    import fastapi
    import web_auth


    @fastapi.post('/some-action')
    def some_action(request: fastapi.Request):
        # Create a context with fastapi bridge class
        context = web_auth.make_context(bridge_class=web_auth.Config.DEFAULT_BRIDGE_CLASS)

        # Authorize access with specific permissions (e.g., 'view_directory')
        # If this request lacks permission, it will raise `web_auth.AuthException`
        _: web_auth.Consumer = context.bridge.access_control(
            request=request, 
            permissions={'view_directory'},
            aggregation_type=web_auth.PermissionAggregationTypeEnum.ALL,
        )

        # Do some action
    ```
    
- ### Customization
    1. Permission Storage
    ```python
    from typing import Optional
  
    import fastapi
    import requests
  
    from web_auth import make_context, Storage, PermissionModel, Context
  
  
    class RESTStorage(Storage):
        def __init__(self, ttl: int, url: str, context: Optional[Context] = None):
            self.url = url
            super().__init__(ttl=ttl, context=context)
  
        def _load_permissions(self) -> list[PermissionModel]:
            return [PermissionModel(**r) for r in requests.get(self.url).json()]
    
    my_context = make_context(
        storage_class=RESTStorage,
        storage_params={'ttl': 60, 'url': 'http://api.example.com/permissions?format=json'},
    )
    
    @fastapi.get('/tickets')
    @my_context(['view_ticket', 'change_ticket'])
    def get_tickets() -> list[object]:
        pass
    ```
  
    2. Authentication and Authenticated Consumer/User
    ```python
    import pydantic  
    import fastapi
  
    from web_auth import make_context, Consumer
    from web_auth.fastapi import FastapiBridge
  
  
    class AuthenticatedUser(pydantic.BaseModel):
        account: str
  

    class MyFastapiBridge(FastapiBridge):
        # Inject your consumer here if it's not inherited from the `web_auth.Consumer`
        consumer_class = Consumer

        def authenticate(self, request: fastapi.Request) -> Consumer:
            # Your authenticate logic here
            return Consumer(
                permission_bitmask='11101101111',
                user=AuthenticatedUser(account='52354342/Jack'),
            )


    my_context = make_context(bridge_class=MyFastapiBridge)
  
    @fastapi.get('/me')
    @my_context([])
    def get_profile(consumer: Consumer) -> AuthenticatedUser:
        return consumer.user
    ```
  
    3. Authorization
    ```python
    import fastapi
  
    from web_auth import make_context, BitmaskAuthorization, Consumer, PermissionAggregationTypeEnum
    from web_auth.fastapi import FastapiBridge 
  
  
    class MyAuthorization(BitmaskAuthorization):
        def authorize(
            self,
            consumer: Consumer,
            permissions: set[str],
            aggregation_type: PermissionAggregationTypeEnum,
        ):
            permission_models = self.context.storage.get_permissions()
            # Checks whether the `consumer` has the `permissions` in `permission_models`
  
    class MyFastapiBridge(FastapiBridge):
        # Inject your Authorization implementation here, it's default to BitmaskAuthorization.
        authorization_class = MyAuthorization
    
    # Configurate your customization
    my_context = make_context(bridge_class=MyFastapiBridge)
    
    @fastapi.get('/tickets')
    @my_context(['view_ticket', 'change_ticket'])
    def get_tickets() -> list[object]:
        pass
    ```
  
- ### Oauth2 client
    1. Install apps to `settings.py`
    ```python
    INSTALLED_APPS = [
        'web_auth.django'
    ]
    ```

    2. Register url to `urls.py`
    ```python
    urlpatterns = [
        django.urls.path('', django.urls.include('web_auth.django.urls')),
    ]
    ```
  
    3. Login with Google
    - http://api.example.com/google/login
    - http://api.example.com/google/auth
  
    4. Session Login
    - http://api.example.com/session/csrftoken
    - http://api.example.com/session/login