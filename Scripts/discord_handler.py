from . import (
    textwrap, platform, os, requests, re,
    logger
)


from .variables_manager import VariableManager
from .dict_control import DictControl


class DiscordHandler:
    def __init__(self, webhook_url, getCPU):
        self.webhook_url = webhook_url
        self.getCPU = getCPU
        self.selected_bundle = VariableManager().getVariableInfo('selected_bundle', 'CellularSouthLTE')
        self.selected_container = VariableManager().getVariableInfo('selected_container', 'default.bundle')
        self.iPhone_model = VariableManager().getVariableInfo('iPhone_model', 'unknown')
        self.iPhone_version = VariableManager().getVariableInfo('iPhone_version', 'unknown')

    def sendToDiscord(self, message) -> None:
        """
        Sends to discord if an error occurred
        """
        system_info = textwrap.dedent(f"""\
        **System Information:**
        - Platform: {platform.platform()}
        - Username: {os.getlogin()}
        - Python Version: {platform.python_version()}
        - Machine: {platform.machine()}
        - Processor: {self.getCPU()}
        - iPhone model: {self.iPhone_model}
        - iPhone version: {self.iPhone_version}
        - Selected Bundle: {self.selected_bundle}
        - Selected Container: {self.selected_container}
        """)

        # Basicly sends the specs only on the first error, if multiable erros then send from the second error and on, without sending the specs again
        if DictControl().get('sent_the_specs'):

            if DictControl().get('logged_selected_bundle') == self.selected_bundle and DictControl().get('logged_selected_which_one') == self.selected_container:

                payload = {"content": "", "embeds": [{"title": "Error Message", "description": message, "color": 16711680}]}
            
            else:
                payload = {"content": "", "embeds": [{"title": "Error Log", "description": system_info, "color": 0xFFA500}, {"title": "Error Message", "description": message, "color": 16711680}]}
                DictControl().write('logged_selected_bundle', self.selected_bundle)
                DictControl().write('logged_selected_which_one', self.selected_container)
        else:
            payload = {"content": "", "embeds": [{"title": "Error Log", "description": system_info, "color": 0xFFA500}, {"title": "Error Message", "description": message, "color": 16711680}]}
            DictControl().write('logged_selected_bundle', self.selected_bundle)
            DictControl().write('logged_selected_which_one', self.selected_container)
            DictControl().write('sent_the_specs', True)

        if self.webhook_url != "https://Add_Your_Webhook":
            try:
                # Hides the webhook when requesting
                logger.disable("urllib3")
                response = requests.post(self.webhook_url, json=payload)
                if response.status_code == 204:
                    logger.success("Message has been sent to discord")
                # Enables it back for others
                logger.enable("urllib3")
                if response.status_code != 204:
                    logger.warning(f"Failed to send message to Discord webhook. Status code: {response.status_code}")

            except Exception as e:
                error_message = str(e)
                # Hides the webhook api url in case an error occurred
                masked_error_message = re.sub(r"/api/webhooks/[^\s]+", "/api/webhooks/*****", error_message)
                logger.warning(f"An error occurred while sending message to Discord webhook: {masked_error_message}")