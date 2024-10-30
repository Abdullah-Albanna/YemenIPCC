import textwrap
import platform
import os
import requests
import re

from database.dict_control import DictControl
from database.db import DataBase
from config.secrets import Env

from loguru import logger


class DiscordHandler:
    def __init__(self, get_cpu):
        url = DataBase().get(["custom_url"], [""], table="discord")[0]
        if not url == "":
            self.webhook_url = url
            self.custom_discord_url: bool = True

        else:
            self.webhook_url = Env().discord_webhook_url
            self.custom_discord_url: bool = False

        self.get_cpu = get_cpu
        self.selected_bundle = DataBase.get(
            ["selected_bundle"], ["CellularSouthLTE"], table="bundle"
        )[0]
        self.selected_container = DataBase.get(
            ["selected_container"], ["default.bundle"], table="bundle"
        )[0]
        self.iPhone_model = DataBase.get(["iPhone_model"], ["unknown"], table="iphone")[
            0
        ]
        self.iPhone_version = DataBase.get(
            ["iPhone_version"], ["unknown"], table="iphone"
        )[0]

    def sendToDiscord(self, message) -> None:
        """
        Sends to discord if an error occurred
        """
        system_info = textwrap.dedent(
            f"""\
        **System Information:**
        - Platform: {platform.platform()}
        - Username: {os.getlogin()}
        - Python Version: {platform.python_version()}
        - Machine: {platform.machine()}
        - Processor: {self.get_cpu()}
        - iPhone model: {self.iPhone_model}
        - iPhone version: {self.iPhone_version}
        - Selected Bundle: {self.selected_bundle}
        - Selected Container: {self.selected_container}
        """
        )

        # One error message is allowed to be sent, if the exact is sent again, no no
        # if str(message) == str(DictControl().get("sent_errors")):
        #     return

        if not DataBase().get(["enable"], [True], table="discord")[0]:
            return

        # Basicly sends the specs only on the first error, if multiable erros then send from the second error and on, without sending the specs again
        if DictControl().get("sent_the_specs"):
            if (
                DictControl().get("logged_selected_bundle") == self.selected_bundle and
                DictControl().get("logged_selected_which_one") == self.selected_container
            ):
                payload = {
                    "content": "",
                    "embeds": [
                        {
                            "title": "Error Message",
                            "description": message,
                            "color": 16711680,
                        }
                    ],
                }

            else:
                payload = {
                    "content": "",
                    "embeds": [
                        {
                            "title": "Error Log",
                            "description": system_info,
                            "color": 0xFFA500,
                        },
                        {
                            "title": "Error Message",
                            "description": message,
                            "color": 16711680,
                        },
                    ],
                }
                DictControl().write("logged_selected_bundle", self.selected_bundle)
                DictControl().write(
                    "logged_selected_which_one", self.selected_container
                )
        else:
            payload = {
                "content": "",
                "embeds": [
                    {
                        "title": "Error Log",
                        "description": system_info,
                        "color": 0xFFA500,
                    },
                    {
                        "title": "Error Message",
                        "description": message,
                        "color": 16711680,
                    },
                ],
            }
            DictControl().write("logged_selected_bundle", self.selected_bundle)
            DictControl().write("logged_selected_which_one", self.selected_container)
            DictControl().write("sent_the_specs", True)

        if re.match(r"^https://discord.com/api/webhooks*", self.webhook_url):
            try:
                # Hides the webhook when requesting
                logger.disable("urllib3")
                response = requests.post(self.webhook_url, json=payload)

                if response.status_code == 204:
                    logger.success("Message has been sent to discord")

                # Enables it back for others
                logger.enable("urllib3")

                if response.status_code != 204:
                    logger.warning(
                        f"Failed to send message to Discord webhook. Status code: {response.status_code}"
                    )

            except Exception as e:
                error_message = str(e)
                # Hides the webhook api url in case an error occurred
                masked_error_message = re.sub(
                    r"/api/webhooks/\S+", "/api/webhooks/*****", error_message
                )
                logger.warning(
                    f"An error occurred while sending message to Discord webhook: {masked_error_message}"
                )
