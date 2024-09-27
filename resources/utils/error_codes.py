from enum import Enum


class ErrorCodes(Enum):
    SUCCESS = 0
    FILE_NOT_FOUND = 1
    INVALID_INPUT = 2
    NETWORK_ERROR = 3
    PERMISSION_DENIED = 4
    UNKNOWN_ERROR = 99