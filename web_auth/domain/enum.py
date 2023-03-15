from enum import Enum, unique


@unique
class PermissionAggregationTypeEnum(str, Enum):
    ALL = 'all'
    ANY = 'any'


@unique
class ErrorCode(str, Enum):
    UNAUTHORIZED = 4010
    BAD_JWT = 4011
    BAD_BASE64_ENCODED = 4030
    BAD_BITMASK = 4031
    PERMISSION_DENIED = 4032
