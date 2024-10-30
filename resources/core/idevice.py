from pymobiledevice3 import usbmux
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.os_trace import OsTraceService
from pymobiledevice3.exceptions import (
    ConnectionFailedToUsbmuxdError,
    PairingDialogResponsePendingError,
    PairingError,
    AppInstallError,
)
from pymobiledevice3.services.diagnostics import DiagnosticsService
from pymobiledevice3.services.installation_proxy import InstallationProxyService

from utils.logger_config_class import YemenIPCCLogger
from utils.errors_stack import getStack

from typing import Literal, Union
from pathlib import Path
from threading import Event
import os

logger = YemenIPCCLogger().logger


class iDevice:
    def __init__(self) -> None:
        ...

    @staticmethod
    def _get_serial() -> Union[str, None]:
        # gets the first connected device
        # TODO: handle if more than one device is connected

        try:
            return usbmux.list_devices()[0].serial
        except (ConnectionFailedToUsbmuxdError, IndexError):
            return None
        except Exception as e:
            logger.error("Unknown error once got the serial of the connected iPhone, error: {}, stack: {}".format(e, getStack()))
            return None

    @staticmethod
    def isPlugged() -> bool:
        return bool(iDevice._get_serial())

    @staticmethod
    def pair() -> bool:
        try:
            lockdown = create_using_usbmux()

            lockdown.pair(15)

            return True
        except (
            ConnectionFailedToUsbmuxdError,
            PairingDialogResponsePendingError,
            PairingError,
        ) as e:
            logger.error("Couldn't pair connected iPhone, error: {}, stack: {}".format(e, getStack()))
            return False

    @staticmethod
    def unpair() -> bool:
        try:
            lockdown = create_using_usbmux()

            lockdown.unpair()

            return True
        except (
            ConnectionFailedToUsbmuxdError,
            PairingError,
        ) as e:
            logger.error("Couldn't unpair connected iPhone, error: {}, stack: {}".format(e, getStack()))
            return False

    @staticmethod
    def systemActions(action: Literal["shutdown", "restart", "sleep"]) -> bool:
        try:
            lockdown = create_using_usbmux()

            getattr(DiagnosticsService(lockdown), action)()

            return True

        except ConnectionFailedToUsbmuxdError as e:
            logger.error("Couldn't preform actions on the connected iPhone, error: {}, stack: {}".format(e, getStack()))
            return False

    @staticmethod
    def deviceInfo() -> dict:
        try:
            lockdown = create_using_usbmux()
            return lockdown.short_info

        except ConnectionFailedToUsbmuxdError as e:
            logger.error("Couldn't get the info of the connected iPhone, error: {}, stack: {}".format(e, getStack()))
            return {}
        except Exception as e:
            logger.error("Unknown error once got the info of the connected iPhone, error: {}, stack: {}".format(e, getStack()))
            return {}

    @staticmethod
    def install(package: Union[str, Path]) -> bool:
        try:
            lockdown = create_using_usbmux()

            InstallationProxyService(lockdown).install_from_local(package)

            return True
        except (ConnectionFailedToUsbmuxdError, AppInstallError, FileNotFoundError) as e:
            logger.error("Couldn't install the given ipcc file on the connected iPhone, error: {}, stack: {}".format(e, getStack()))
            return False

    def liveSysLog(log_queue: list, stop_event: Event):
        try:
            lockdown = create_using_usbmux()

            for entry in OsTraceService(lockdown).syslog():
                if stop_event.is_set():
                    break

                if os.path.basename(entry.filename) != "CommCenter":
                    continue

                log_queue.append(entry.message)

        except ConnectionFailedToUsbmuxdError:
            return False
