import abc
import base64

from .enum import ErrorCode, PermissionAggregationTypeEnum
from .exception import AuthException
from .model import Consumer, PermissionModel


class Authorization(abc.ABC):
    def __init__(self, context):
        self.context = context

    @abc.abstractmethod
    def authorize(
        self,
        consumer: Consumer,
        permissions: set[str],
        aggregation_type: PermissionAggregationTypeEnum,
    ):
        """Checks whether the `consumer` has the `permissions` to access a protected resource.

        :param consumer: the consumer of returning from Authentication
        :param permissions: the permissions the users required
        :param aggregation_type: aggregate method of applying permissions; all permissions are needed or just any.
        """
        raise NotImplementedError


class JWTAuthorization(Authorization):
    """Authorize access to resources based on a JSON Web Token (JWT).

    If the user does not have the required permissions, an `AuthException` is raised with the
    appropriate error code defined in `ErrorCode`.
    """

    def authorize(
        self,
        consumer: Consumer,
        permissions: set[str],
        aggregation_type: PermissionAggregationTypeEnum,
    ):
        permission_bitmask = self.convert_base64encoded_to_bitmask(consumer.permission_bitmask)
        return self.check_permissions(
            permissions,
            aggregation_type,
            permission_bitmask,
            self.context.storage.get_permissions(permissions),
        )

    @staticmethod
    def convert_base64encoded_to_bitmask(base64_permissions: str) -> str:
        try:
            decoded_bytes = base64.b64decode(base64_permissions)
        except Exception:
            raise AuthException(f'Bad base64-encoded `{base64_permissions}`', ErrorCode.BAD_BASE64_ENCODED)

        permission_bitmask = ''.join(['{:08b}'.format(v) for v in decoded_bytes])
        return permission_bitmask

    @staticmethod
    def check_permissions(
        permissions: set[str],
        aggregation_type: PermissionAggregationTypeEnum,
        permission_bitmask: str,
        permission_models: list[PermissionModel],
    ):
        permission_codename_bitmap = {p.codename: p.bitmask_idx for p in permission_models}
        permission_bitmask_len = len(permission_bitmask)
        for codename in permissions:
            bitmask_idx = permission_codename_bitmap.get(codename)
            if bitmask_idx is None or not 0 <= bitmask_idx < permission_bitmask_len:
                raise AuthException(f'Bad permission bitmask `{permission_bitmask}`', ErrorCode.BAD_BITMASK)

            bit_chat = permission_bitmask[permission_bitmask_len - bitmask_idx - 1]
            if bit_chat == '0' and aggregation_type == PermissionAggregationTypeEnum.ALL:
                raise AuthException('Permission denied', ErrorCode.PERMISSION_DENIED)
            if bit_chat == '1' and aggregation_type == PermissionAggregationTypeEnum.ANY:
                return None
