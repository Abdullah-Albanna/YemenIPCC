from .projectimports import (logging, argparse, os, gettempdir, platform, requests, subprocess, Path, sleep)
from .variables_manager import VariableManager
from .thread_starter import startThread
from logging import Handler, LogRecord
import textwrap
from cryptography.fernet import Fernet

# Sets the temporary directory to save the also temporary file, which contains the changing variables
tempdir = gettempdir() if platform.system() == "Windows" else os.path.join(os.path.expanduser("~/.cache"))

def decrypt(key):
    try:
        if not os.path.exists(os.path.join(".", "discord_webhook")):
            if os.path.exists(os.path.join(".", "discord_webhook_encrypted")):
                cipher_suite = Fernet(key)
                with open(os.path.join(".", "discord_webhook_encrypted"), "rb") as file:
                    encrypted_data = file.read()

                decrypted_data = cipher_suite.decrypt(encrypted_data)

                decrypted_data_str = decrypted_data.decode('utf-8')
                return decrypted_data_str
            else:
    
                return None

        elif os.path.exists(os.path.join(".", "discord_webhook")):
            with open(os.path.join(".", "discord_webhook"), "r") as discord_webhook:
                discord_webhook_data = discord_webhook.read()
                return discord_webhook_data

    except Exception as e:
        logging.error(f"logging_config.py - An error occurred in the decryption of the webhook, error: {e}")


# I am hiding my Discord webhook for obvious reasons. If you want to use your own,
# create a new file in the project root named "discord_webhook" and put your webhook in it.
# I use the Discord webhook to receive any errors occurring in the app, which helps in developing the app better.

# If you don't like idea of me receving information of the errors and some other infos, all you have to do is delete the "discord_webhook_encrypted" file from the compiled app.
DISCORD_WEBHOOK_URL: str = decrypt("~ThisIsMyOwnPrivateDiscordWebhook,ThisKeyIsWrong,PleaseAdjustForYoursOrCreateTheFile~") if os.path.exists(os.path.join(".", "discord_webhook_encrypted")) or os.path.exists(os.path.join(".", "discord_webhook")) else None

temp_variables = VariableManager().loadTempVariables()
selected_bundle = temp_variables.get('selected_bundle', 'CellularSouthLTE')
selected_which_one = temp_variables.get('selected_which_one', 'Default.bundle')
iPhone_model = temp_variables.get('iPhone_model', 'unknown')
iPhone_version = temp_variables.get('iPhone_version', 'unknown')
is_debug_on = False

def getCPU():
    if platform.system() == "Linux":
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.readlines()
            for line in cpuinfo:
                if 'model name' in line:
                    processor_name = line.split(':')[-1].strip()
                    return processor_name
            return "Unknown"
        except Exception as e:
            return "Unknown"
    elif platform.system() == "Darwin":
        try:
            output = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).strip()
            processor_name = output.decode('utf-8')
            return processor_name
        except Exception as e:
            return "Unknown"
    else:
        try:
            processor_name = os.environ.get('PROCESSOR_IDENTIFIER', 'Unknown')
            return processor_name
        except Exception as e:
            return "Unknown"

class DiscordHandler(Handler):
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url
        self.sent_the_specs = False
        self.logged_selected_bundle: str = ""
        self.logged_selected_which_one: str = ""

    def emit(self, record: LogRecord):
        if record.levelno == logging.ERROR:
            message = self.format(record)
            system_info = textwrap.dedent(f"""\
            **System Information:**
            - Platform: {platform.platform()}
            - Username: {os.getlogin()}
            - Python Version: {platform.python_version()}
            - Machine: {platform.machine()}
            - Processor: {getCPU()}
            - iPhone model: {iPhone_model}
            - iPhone version: {iPhone_version}
            - Selected Bundle: {selected_bundle}
            - Selected Container: {selected_which_one}
            """)
            if self.sent_the_specs:
                if self.logged_selected_bundle == selected_bundle or self.logged_selected_which_one == selected_which_one:
                    payload = {"content": "", "embeds": [{"title": "Error Message", "description": message, "color": 16711680}]}
                    print( self.logged_selected_bundle, selected_bundle)
                else:
                    payload = {"content": "", "embeds": [{"title": "Error Log", "description": system_info, "color": 0xFFA500}, {"title": "Error Message", "description": message, "color": 16711680}]}
            else:
                payload = {"content": "", "embeds": [{"title": "Error Log", "description": system_info, "color": 0xFFA500}, {"title": "Error Message", "description": message, "color": 16711680}]}
                self.logged_selected_bundle = selected_bundle
                self.logged_selected_which_one = selected_which_one
                self.sent_the_specs = True
            try:
                response = requests.post(self.webhook_url, json=payload)
                if response.status_code != 204:
                    print(f"Failed to send message to Discord webhook. Status code: {response.status_code}")
            except Exception as e:
                print(f"An error occurred while sending message to Discord webhook: {e}")

def setupLogging(debug, file_logging):
    global is_debug_on
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    log_level = logging.DEBUG if debug else logging.ERROR
    
    handlers = [logging.StreamHandler()]
    
    if file_logging:
        if not os.path.exists(tempdir):
            logging.info("The temporary directory does not exists, making one")
            Path(tempdir).mkdir(parents=True, exist_ok=True)

        if not os.path.exists(os.path.join(tempdir, "yemenipcc_logs.txt")):
            Path(os.path.join(tempdir, "yemenipcc_logs.txt")).touch()
            logging.info("Made the cache file with pathlib")

        log_file_path = os.path.join(tempdir, "yemenipcc_logs.txt")
            
        handlers.append(logging.FileHandler(log_file_path, mode='w'))
    
    if DISCORD_WEBHOOK_URL:
        handlers.append(DiscordHandler(webhook_url=DISCORD_WEBHOOK_URL))

    logging.basicConfig(level=log_level, format=log_format, handlers=handlers)
    if debug:
        if not is_debug_on:
            logging.debug("Logging is set up. Debug mode: {}, Log file: {}".format(debug, file_logging))
            is_debug_on = True


def parseArgs():
    parser = argparse.ArgumentParser(
        description="Yemen IPCC - An application for managing IPCC settings",
        usage="%(prog)s [options]"
    )
    tempath = os.path.join(tempdir, "yemenipcc_logs.txt")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('-f', '--file', action='store_true', help=f"Saves the debug logs to a file in {tempath} (Must be used with -d)")
    args = parser.parse_args()
    
    if args.file and not args.debug:
        parser.error("--file (-f) must be used with --debug (-d)")
    return args


args = parseArgs()
setupLogging(args.debug, args.file)