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

## Permission Representation
1. Permission list, located at `usr/etc/permissions.json` file:
    ```python
    [
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
    import fastapi
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
    from web_auth.web_bridge.flask import FlaskBridge
    
    web_auth.configure(
        web_bridge_class=FlaskBridge,
    )
    
    @blueprint.route('/tickets', methods=['GET'])
    @web_auth.permissions('view_ticket')
    def list_tickets() -> list[object]: 
        pass

    ```

- ### Use instanced context

    ```python
    import fastapi
    import web_auth
    from web_auth.web_bridge.fastapi import FastapiBridge
    from web_auth.storage.file import FileStorage
    
    context = web_auth.build_context(
        web_bridge_class=FastapiBridge,
        storage_class=FileStorage,
        storage_params=web_auth.Config.DEFAULT_STORAGE_PARAMS,
    )  
    
    @fastapi.get('/tickets')
    @context('view_ticket')
    async def list_tickets() -> list[object]: 
        pass

    ```

- ### Implement access control & retrieve the consumer info
    ```python
    import fastapi
    import web_auth
    from web_auth.web_bridge.fastapi import FastapiBridge
    from web_auth.storage.file import FileStorage
    
    context = web_auth.build_context(
        web_bridge_class=FastapiBridge,
        storage_class=FileStorage,
        storage_params=web_auth.Config.DEFAULT_STORAGE_PARAMS,
    )
    
    @fastapi.get('/profile')
    def get_profile(request: fastapi.Request, consumer_info: web_auth.ConsumerInfo) -> web_auth.ConsumerInfo:
        # raise `web_auth.AuthException` if the consumer does not have permission
        context.web_bridge.access_control(
            request=request, 
            permissions={'view_ticket'},
            aggregation_type=web_auth.PermissionAggregationTypeEnum.ALL,
        )
        return consumer_info

    ```
