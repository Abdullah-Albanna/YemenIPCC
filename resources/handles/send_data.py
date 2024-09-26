import requests
from typing import Optional


from ..utils.logger_config_class import YemenIPCCLogger
from ..database.dict_control import DictControl
from ..config.secrets import Env

from ..checkers.check_for_internet import checkInternetConnection
from ..utils.errors_stack import getStack

logger = YemenIPCCLogger().logger

API_KEY = Env().api_key


def getDomain() -> str:
    """
    Gets my domain from the "current_domain.txt" in the repo.

    It might be changed later on, so that's why
    """

    if DictControl().get("domain") is not None:
        return DictControl().get("domain")

    url = (
        f"https://raw.githubusercontent.com/{Env().repo}/app-source/current_domain.txt"
    )

    # connector = aiohttp.TCPConnector(force_close=True)
    # with aiohttp.ClientSession(connector=connector) as session:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.text
            data = data.replace(" ", "").replace("\n", "")
            DictControl().write("domain", data)

            return data

        else:
            logger.error(
                f"Failed to retrieve data from {url}. Status code: {response.status_code}, stack: {getStack()}"
            )
    except requests.ConnectionError as e:
        logger.warning(f"Error fetching data: {e}")


def sendData(
    event: str,
    device: Optional[str] = None,
    success: Optional[bool] = None,
    active: Optional[bool] = None,
    uid: Optional[str] = None,
) -> None:
    """
    Sends activity data to the server

    """
    if not checkInternetConnection():
        return

    if DictControl().get("enough_errors", num=True) >= 2:
        return

    if "hidden" not in API_KEY:
        domain = getDomain()

        if domain is None:
            return

        url = f"https://app.{domain}/track"  ##
        headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
        payload = {"event": event, "data": {}}

        if event == "injection":
            if device is not None and success is not None:
                payload["data"]["device"] = device
                payload["data"]["success"] = success
            else:
                logger.warning(
                    "Device and success status are required for 'injection' event."
                )

        elif event == "app opens":
            # No specific data needed for 'app opens' event
            pass

        elif event == "active":
            if active is not None:
                if uid is None:
                    logger.warning("UUID is required for 'active' event.")
                payload["data"]["active"] = active
                payload["data"]["id"] = uid
            else:
                logger.warning("Active status is required for 'active' event.")

        else:
            logger.warning(f"Unsupported event type: {event}")

        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                if DictControl().runTwice("logged_sent_data"):
                    DictControl().write("logged_webserver_down", False)
            else:
                if (
                    "Bad gateway" in response.text
                    or "Argo Tunnel error" in response.text
                ):
                    if DictControl().shouldRun("logged_webserver_down"):
                        logger.warning("The webserver is currently down")
                        DictControl().write("logged_sent_data", False)
                else:
                    DictControl().write(
                        "enough_errors", DictControl().get("enough_errors") + 1
                    )
                    logger.error(
                        f"Failed to send {event} data: {response.status_code}, stack: {getStack()}"
                    )
        except requests.ConnectionError as e:
            logger.error(f"Error sending {event} data: {str(e)}, stack: {getStack()}")
    else:
        if DictControl().shouldRun("logged_user_using_source_c}ode"):
            logger.info("User is running the source code")
# async def sendData(
#     event: str,
#     device: Optional[str] = None,
#     success: Optional[bool] = None,
#     active: Optional[bool] = None,
#     uid: Optional[str] = None,
# ) -> None:
#     """
#     Sends activity data to the server

#     """
#     if not checkInternetConnection():
#         return

#     if DictControl().get("enough_errors", num=True) >= 2:
#         return

#     if "hidden" not in API_KEY:
#         domain = await getDomain()

#         if domain is None:
#             return

#         url = f"https://app.{domain}/track"  ##
#         headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
#         payload = {"event": event, "data": {}}

#         if event == "injection":
#             if device is not None and success is not None:
#                 payload["data"]["device"] = device
#                 payload["data"]["success"] = success
#             else:
#                 logger.warning(
#                     "Device and success status are required for 'injection' event."
#                 )

#         elif event == "app opens":
#             # No specific data needed for 'app opens' event
#             pass

#         elif event == "active":
#             if active is not None:
#                 if uid is None:
#                     logger.warning("UID is required for 'active' event.")
#                 payload["data"]["active"] = active
#                 payload["data"]["id"] = uid
#             else:
#                 logger.warning("Active status is required for 'active' event.")

#         else:
#             logger.warning(f"Unsupported event type: {event}")

#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.post(url, headers=headers, json=payload) as response:
#                     if response.status == 200:
#                         if DictControl().runTwice("logged_sent_data"):
#                             DictControl().write("logged_webserver_down", False)
#                     else:
#                         if (
#                             "Bad gateway" in await response.text()
#                             or "Argo Tunnel error" in await response.text()
#                         ):
#                             if DictControl().shouldRun("logged_webserver_down"):
#                                 logger.warning("The webserver is currently down")
#                                 DictControl().write("logged_sent_data", False)
#                         else:
#                             DictControl().write(
#                                 "enough_errors", DictControl().get("enough_errors") + 1
#                             )
#                             logger.error(
#                                 f"Failed to send {event} data: {response.status}, stack: {getStack()}"
#                             )
#         except aiohttp.ClientError as e:
#             logger.error(f"Error sending {event} data: {str(e)}, stack: {getStack()}")
#     else:
#         if DictControl().shouldRun("logged_user_using_source_c}ode"):
#             logger.info("User is running the source code")
