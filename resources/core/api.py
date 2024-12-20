import requests
import keyring
import sys
import aiohttp
from tkinter import messagebox
from typing import Literal
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from time import sleep
import zlib
import base64


from ..utils.logger_config_class import YemenIPCCLogger
from ..database.db import DataBase
from ..config.secrets import Env

from ..utils.errors_stack import getStack
from ..utils.get_os_lang import isItArabic

from ..thread_managment.thread_terminator_var import terminate_splash_screen

logger = YemenIPCCLogger().logger
arabic: bool = DataBase.get(["arabic"], [isItArabic()], "app")[0]
username: str = DataBase.get(["username"], ["Unknown"], "account")[0]


public_key_base64 = Env().public_key
public_key_decoded = base64.b64decode(public_key_base64).decode("utf-8")

public_key = public_key_decoded.encode("utf-8")


class API:
    def __init__(self) -> None:
        self.domain = Env().api_domain
        self.secret = Env().secret
        self.public_key = serialization.load_pem_public_key(public_key)
        # with open(f"{getAppDirectory()}/resources/public_key.pem", "rb") as key_file:
        #     self.public_key = serialization.load_pem_public_key(key_file.read())

    def encryptData(self, payload: str):
        try:
            compressed_payload = zlib.compress(payload.encode("utf-8"))
            encryted_data = self.public_key.encrypt(
                compressed_payload,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            return encryted_data.hex()
        except Exception as e:
            logger.error(f"Couldn't encrypt data, error: {e}, stack: {getStack()}")

    async def makeRequest(
        self,
        method: Literal["get", "post"],
        url: str,
        headers: dict[str, str] = None,
        data: dict[str, str] = None,
        json: dict[str, str] = None,
        params: dict[str, str] = None,
        timeout: int = 20,
    ):
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(timeout)
            ) as session:
                async with getattr(session, method)(
                    url, headers=headers, data=data, json=json, params=params
                ) as response:
                    try:
                        json_res: dict = await response.json()
                    except Exception:
                        json_res: dict = {}

                    try:
                        content = await response.read()
                    except Exception:
                        content = None

                    return json_res, response.status, content
        except aiohttp.ClientError as ce:
            logger.error(
                f"Couldn't complete http request, error: {ce}, stacl: {getStack()}"
            )

    def createAccount(
        self, username, email, password, laptop_user, serial_number, ip, region
    ) -> Literal[
        "You cannot create any more accounts",
        "malformed username",
        "malformed email",
        "username is already reserved",
        "email is used for another account",
        "success",
    ]:
        payload = {
            "username": self.encryptData(username),
            "email": self.encryptData(email),
            "password": self.encryptData(password),
            "laptop_user": self.encryptData(laptop_user),
            "serial_number": self.encryptData(serial_number),
            "ip": self.encryptData(ip),
            "region": self.encryptData(region),
            "secret_key": self.encryptData(self.secret),
            "arabic": arabic,
        }

        response = requests.post(
            url=f"{self.domain}/signup",
            json=payload,
            timeout=20,
        )

        if response.status_code != 201:
            error_detail = response.json().get("detail")
            logger.warning(
                f"An error occurred with {username} in the creation of an account, error: {error_detail}"
            )

            return error_detail
        else:
            logger.success(f"Successfully created an account with username: {username}")

            return "success"

    async def login(
        self, username, password, serial_number
    ) -> Literal[
        "invalid credentials",
        "please authenticate your account first",
        "please check you email to confirm your login",
        "success",
    ]:
        payload = {
            "username": self.encryptData(username),
            "password": self.encryptData(password),
            "serial_number": self.encryptData(serial_number),
            "arabic": arabic,
        }


        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

        # json_response, status, _ = await self.makeRequest(
        #     "post", f"{self.domain}/login", headers=headers, data=payload
        # )

        response = requests.post(f"{self.domain}/login", headers=headers, data=payload)

        json_response = response.json()
        status = response.status_code

        if status != 200:
            error_detail = json_response.get("detail")
            logger.warning(
                f"A error occurred in the login proccess, error: {error_detail}"
            )

            return error_detail

        keyring.set_password("yemenipcc", username, json_response.get("access_token"))
        DataBase.add(["username"], [username], "account")
        logger.success("successfully logged in")

        return "success"

    async def genLink(
        self, iPhone_model, iPhone_version, bundle, container
    ) -> Literal["you can't download any more today", "file not found"] | bytes:
        payload = {
            "iPhone_model": iPhone_model,
            "iPhone_version": iPhone_version,
            "bundle": bundle,
            "container": container,
        }
        headers = {
            "Authorization": f'Bearer {keyring.get_password("yemenipcc", username)}',
        }

        # response = requests.get(
        #     url=f"{self.domain}/genlink", params=payload, headers=headers, timeout=20
        # )
        url = f"{self.domain}/genlink"

        # async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(20)) as session:
        #     async with session.get(url, headers=headers, params=payload) as response:
        #         # json_res: dict = await response.json()
        #         status = response.status
        #         try:
        #             json_res: dict = await response.json()
        #         except aiohttp.ContentTypeError:
        #             json_res: dict = {}
        #         content = await response.read()

        json_res, status, content = await self.makeRequest(
            "get", url, headers=headers, params=payload
        )

        if status != 200:
            error_detail = json_res.get("detail")
            logger.warning(
                f"An error occurred in generating a link, error: {error_detail}"
            )

            return error_detail
        else:
            # with open("file.ipcc", "wb") as file:
            #     file.write(response.content)
            logger.debug(f"downloaded {bundle}")

            return content

    async def refreshToken(
        self, token, username
    ) -> Literal["please get a new token", "success"]:
        payload = {"token": token}

        try:
            json_response, status, _ = await self.makeRequest(
                "post", f"{self.domain}/refresh_token", data=payload
            )
            # qst = requests.post(f"https://{self.domain}/refresh_token", data=payload)
            # json_response = qst.json()
            # status = qst.status_code

            if status != 201:
                warning: str = json_response.get("detail")
                logger.warning(
                    f"A warning occurred in login with a token, warning: {warning}"
                )

                return warning
            else:
                keyring.set_password(
                    "yemenipcc", username, json_response.get("access_token")
                )

                return "success"

        except aiohttp.ClientError as e:
            logger.error(f"An error occurred in the api, error: {e}, error stack: {getStack()}")
            terminate_splash_screen.set()
            sleep(1)
            messagebox.showerror(
                "error",
                "something went down, maybe the server is shut, please try again later",
            )
            sys.exit(1)

    async def grabUserInfo(self) -> dict | Literal["user does not exists"]:
        payload = {
            "token": keyring.get_password(
                "yemenipcc", str(DataBase.get(["username"], [False], "account")[0])
            )
        }

        json_response, status, _ = await self.makeRequest(
            "get", f"{self.domain}/users", data=payload
        )

        if status != 200:
            warning: str = json_response.get("detail")
            logger.warning(f"An error occurred in the grab user info, error: {warning}")

            return warning
        else:
            return json_response

    async def resendAccountVerify(
        self, username, password
    ) -> Literal["success", "account does not exists", "account already verified"]:
        payload = {
            "username": self.encryptData(username),
            "password": self.encryptData(password),
            "arabic": arabic,
        }

        json_response, status, _ = await self.makeRequest(
            "post", f"{self.domain}/resend_verify", data=payload
        )

        if status != 200:
            warning: str = json_response.get("detail")
            logger.warning("An error occurred in resending the email verify")

            return warning
        else:
            return json_response
