# web-auth-sdk

The web-auth-sdk is an authorization SDK used to build protected Web APIs.
It provides the ability to intercept incoming requests and inject custom logic for authentication and authorization
before the request reaches the view function.

Clients should authenticate by passing credentials or authorizations. For example, a JWT key can be used as follows:
   ```shell
     curl 'http://api.example.com/resources' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
     curl 'http://api.example.com/resources?access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
     curl 'http://api.example.com/resources' --cookie 'access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
   ```

## Requirements
- Python 3.8+
- FastAPI 0.80+ (recommended)
- Flask 2.0+ (optional)

## Installation
   ```shell
   pip install web-auth-sdk
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

2. How to encode permissions?

   Permissions are encoded using a bitmask of length n that is a multiple of 24.
   Each permission is represented by a 1 on the corresponding `bitmask_idx`-th position in the bitmask, indicating that
   the permission is granted.


3. Base64-encoded the bitmask
![](usr/share/img/PermissionBitmask.png)


4. Encoded/Decoded JWT
![](usr/share/img/JWT.png)


## Development
- ### FastAPI

    ```python
    import web_auth
    
  
    web_auth.configure()
    
    @fastapi.get('/tickets')
    @web_auth.permissions('view_ticket') # Iterable[str] are acceptable
    async def list_tickets() -> list[object]: 
        pass
    ```

- ### Flask

    ```python
    import web_auth
    from web_auth.flask import FlaskBridge
    
  
    web_auth.configure(
        bridge_class=FlaskBridge,
    )
    
    @blueprint.route('/tickets', methods=['GET'])
    @web_auth.permissions('view_ticket')
    def list_tickets() -> list[object]: 
        pass
    ```

- ### Use instanced context

    ```python
    import web_auth
    
  
    context = web_auth.build_context()  
    
    @fastapi.get('/tickets')
    @context.permissions('view_ticket')
    async def list_tickets() -> list[object]: 
        pass
    ```

- ### Implement access control & retrieve the consumer info

    ```python
    import fastapi
    import web_auth
    
  
    context = web_auth.build_context()
    
    @fastapi.get('/profile')
    @context.permissions()
    def get_profile(request: fastapi.Request, consumer: web_auth.Consumer) -> web_auth.Consumer:
        # raise `web_auth.AuthException` if the consumer does not have permission
        context.bridge.access_control(
            request=request, 
            permissions={'view_ticket'},
            aggregation_type=web_auth.PermissionAggregationTypeEnum.ALL,
        )
        return consumer

    ```
  
- ### Customization
    1. Permission Storage
    ```python
    from typing import Optional
  
    import fastapi
    import requests
  
    from web_auth import build_context, Storage, PermissionModel, Context
  
  
    class RESTStorage(Storage):
        def __init__(self, ttl: int, url: str, context: Optional[Context] = None):
            self.url = url
            super().__init__(ttl=ttl, context=context)
  
        def _load_permissions(self) -> list[PermissionModel]:
            return [PermissionModel(**r) for r in requests.get(self.url).json()]
    
    my_context = build_context(
        storage_class=RESTStorage,
        storage_params={'ttl': 60, 'url': 'http://api.example.com/permissions?format=json'},
    )
    
    @fastapi.get('/tickets')
    @my_context(['view_ticket', 'change_ticket'])
    def get_tickets() -> list[object]:
        pass
    ```
  
    2. Authentication
    ```python
    import fastapi
    import pydantic
  
    from web_auth import build_context, Config
    from web_auth.fastapi import FastapiBridge
  
  
    class MyConsumer(pydantic.BaseModel):
        user_id: int
  
    class MyFastapiBridge(FastapiBridge):
        consumer_class = MyConsumer
  
        def authenticate(self, request: fastapi.Request) -> tuple[MyConsumer, str]:
            # your authenticate logic
            return MyConsumer(user_id=1), 'JWT'
    
    my_context = build_context(
        bridge_class=MyFastapiBridge,
        storage_class=Config.DEFAULT_STORAGE_CLASS,
        storage_params=Config.DEFAULT_STORAGE_PARAMS,
    )
  
    @fastapi.get('/profile')
    @my_context([])
    def get_profile(consumer: MyConsumer) -> MyConsumer:
        return consumer
    ```
  
    3. Authorization
    ```python
    import fastapi
  
    from web_auth import build_context, Authorization, Consumer, PermissionAggregationTypeEnum
    from web_auth.fastapi import FastapiBridge 
  
  
    class MyAuthorization(Authorization):
        def authorize(
            self,
            consumer: Consumer,
            permissions: set[str],
            aggregation_type: PermissionAggregationTypeEnum,
        ):
            permission_models = self.context.storage.get_permissions()
            # Checks whether the `consumer` has the `permissions` in `permission_models`
  
    class MyFastapiBridge(FastapiBridge):
        authorization_class = MyAuthorization
    
    my_context = build_context(
        bridge_class=MyFastapiBridge,
    )
    
    @fastapi.get('/tickets')
    @my_context(['view_ticket', 'change_ticket'])
    def get_tickets() -> list[object]:
        pass
    ```