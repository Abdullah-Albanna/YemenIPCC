from loguru import logger
import os
import subprocess
import sys
import argparse
from datetime import datetime
from pathlib import Path
from tempfile import gettempdir


from ..handles.discord_handler import DiscordHandler
from ..database.dict_control import DictControl

from .get_app_dir import getExecutablePath

from .get_system import system
from ..config.version import CURRENT_VERSION

if system == "Windows":
    from colorama import init  # type: ignore


class YemenIPCCLogger:
    def __init__(self):
        self.tempdir = self.getTempdir()
        # self.enable = self.setDiscordVariables()[1]
        # self.custom_url = self.setDiscordVariables()[2]
        # self.DISCORD_WEBHOOK_URL = self.setDiscordVariables()[0]
        self.is_debug_on = {"result": False}
        self.logger = logger.patch(self.sendToDiscord)
        self.logs_path = getExecutablePath() / "logs.txt"

    def getTempdir(self) -> str:
        """
        Returns the temporary folder
        """
        return (
            gettempdir()
            if system == "Windows"
            else Path("~/.cache").expanduser().resolve()
        )

    # def getDiscordInfo(self) -> dict:
    #     """
    #     Gets the "discord" file content and return a dict out of it
    #     """
    #     discord_var = {}
    #     try:
    #         with open(
    #             (
    #                 "discord"
    #                 if os.path.exists("discord")
    #                 else os.path.join(getAppDirectory(), "discord")
    #             ),
    #             "r",
    #         ) as file:
    #             for line in file:
    #                 # Using regex to ensure proper parsing and handle possible whitespace issues
    #                 match = re.match(r"^\s*(\w+)\s*:\s*(.+)\s*$", line)
    #                 if match:
    #                     variable_name, variable_value = match.groups()
    #                     # Convert to boolean if the value is 'true' or 'false', otherwise keep it as a string
    #                     if variable_value.lower() == "true":
    #                         discord_var[variable_name] = True
    #                     elif variable_value.lower() == "false":
    #                         discord_var[variable_name] = False
    #                     else:
    #                         discord_var[variable_name] = variable_value.strip()
    #     except FileNotFoundError:
    #         if DictControl().shouldRun("logged_discord_file_not_found_message"):
    #             logger.warning('The "discord" file is not found')

    #     return discord_var

    # def isDiscordEnabled(self, discord_info: dict) -> bool:
    #     """
    #     Checks if the discord feature is enabled from the file and returns a boolean
    #     """
    #     enable_value = discord_info.get("enable")
    #     return str(enable_value).lower() in [
    #         "true",
    #         "1",
    #         "yes",
    #     ]  # Implementation of isDiscordEnabled() function

    # def getCustomURL(self, discord_info: dict) -> str:
    #     """
    #     Checks if the discord custom url feature is enabled from the file and returns a string
    #     """
    #     custom_url = discord_info.get("custom_url", "")

    #     # Makes sure it is actually a webhook url, if not use default url
    #     if "https://discord.com/api/webhooks" in custom_url:
    #         return custom_url
    #     return ""

    # def setDiscordVariables(self, debug=None) -> tuple[str | None, bool, str]:
    #     """
    #     adjusts the variables in here according to there
    #     """
    #     discord_path = os.path.join(".", "discord")
    #     # discord_info = self.getDiscordInfo()

    #     # Determine the Discord webhook URL based on the extracted values
    #     if os.path.exists(discord_path):
    #         if self.isDiscordEnabled(discord_info):
    #             custom_url = self.getCustomURL(discord_info)
    #         else:
    #             custom_url = ""
    #         enable = self.isDiscordEnabled(discord_info)
    #     else:
    #         enable = True
    #         custom_url = ""

    #     if enable:
    #         if custom_url.strip() == "":
    #             self.DISCORD_WEBHOOK_URL = Env().discord_webhook_url
    #         else:
    #             self.DISCORD_WEBHOOK_URL = custom_url
    #             if debug:
    #                 if DictControl().shouldRun("logged_custom_url_message"):
    #                     logger.debug(
    #                         f"Using custom Discord Webhook: {self.DISCORD_WEBHOOK_URL}"
    #                     )
    #     else:
    #         if debug:
    #             if DictControl().shouldRun("logged_discord_disabled_message"):
    #                 logger.info("Discord integration is disabled.")

    #         self.DISCORD_WEBHOOK_URL = None
    #         custom_url = ""
    #         enable = False

    #     return self.DISCORD_WEBHOOK_URL, enable, custom_url

    def getCPU(self) -> str:
        """
        Gets the cpu name so it would be sent to discord
        """
        if system == "Linux":
            try:
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.readlines()
                for line in cpuinfo:
                    if "model name" in line:
                        processor_name = line.split(":")[-1].strip()
                        return processor_name
                return "Unknown"
            except Exception:
                return "Unknown"
        elif system == "Mac":
            try:
                output = subprocess.check_output(
                    ["sysctl", "-n", "machdep.cpu.brand_string"]
                ).strip()
                processor_name = output.decode("utf-8")
                return processor_name
            except Exception:
                return "Unknown"
        elif system == "Windows":
            try:
                output = subprocess.check_output(
                    [
                        "wmic",
                        "cpu",
                        "get",
                        "Name,Manufacturer,NumberOfCores,NumberOfLogicalProcessors",
                        "/format:csv",
                    ],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                ).strip()
                lines = output.decode("utf-8").split("\n")
                if len(lines) > 1:
                    # Skip the header line and split the first line of actual data by commas
                    data = lines[1].split(",")
                    processor_name = f"{data[1]} {data[2]} (Cores: {data[3]}, Logical Processors: {data[4]})"
                    return processor_name
                return "Unknown"
            except Exception:
                return "Unknown"
        else:
            return "Unknown"

    def sendToDiscord(self, record) -> None:
        """
        Sends the message to discord if the log is on error or critical
        """

        # Every log message goes to here, and only the errors and the criticals are picked up
        if record["level"].name == "ERROR" or record["level"].name == "CRITICAL":
            message = record["message"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = record["file"].name
            lineno = record["line"]
            message = (
                f"[{timestamp}] {record['message']} (File: {filename}, Line: {lineno})"
            )
            # if self.DISCORD_WEBHOOK_URL is not None:
            DiscordHandler(self.getCPU).sendToDiscord(message)

    def setupLogging(self, debug, file_logging) -> None:
        """
        Sets up logger settings and formation
        """
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        self.logger.remove()  # Remove any previously configured handlers
        self.logger.add(
            sys.stdout, format=log_format, level="DEBUG" if debug else "ERROR"
        )

        if file_logging:
    
            if not self.logs_path.exists():
                self.logs_path.touch
                
            self.logger.add(
                self.logs_path,
                mode="w",
                format=log_format,
                level="DEBUG" if debug else "ERROR",
            )

        if DictControl().shouldRun("logged_first_log"):
            self.logger.debug(
                "Logging is set up. Debug mode: {}, Log file: {}".format(
                    debug, file_logging
                )
            )

    def parseArgs(self) -> argparse.ArgumentParser.parse_args:
        """
        Sets up the app arguments
        """
        
        parser = argparse.ArgumentParser(
            description="Yemen IPCC - An application to inject the network configuration files (.ipcc) to the iPhone devices",
            usage="%(prog)s [options]",
        )
        
        
        parser.add_argument(
            "-d", "--debug", action="store_true", help="Enable debug mode"
        )
        parser.add_argument(
            "-f",
            "--file",
            action="store_true",
            help=f"Saves the debug logs to a file in {self.logs_path} (Must be used with -d)",
        )
        parser.add_argument(
            "-v", "--version", action="version", version=f"%(prog)s {CURRENT_VERSION}"
        )
        args = parser.parse_args()

        if args.file and not args.debug:
            parser.error("--file (-f) must be used with --debug (-d)")
        return args

    def run(self) -> None:
        """
        Initiates the logger
        """
        args = self.parseArgs()
        if system == "Windows":
            init()
        # self.setDiscordVariables(args.debug)
        self.setupLogging(args.debug, args.file)
