from enum import auto, Flag


class ErrorCodes(Flag):
    SUCCESS = auto()
    FILE_NOT_FOUND = auto()
    INVALID_INPUT = auto()
    NETWORK_ERROR = auto()
    PERMISSION_DENIED = auto()
    TIMEOUT = auto()
    PROCESS_ERROR = auto()
    UNKNOWN_ERROR = auto()
