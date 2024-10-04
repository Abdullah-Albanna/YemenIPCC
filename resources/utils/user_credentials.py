import getpass
import psutil
import requests
import subprocess
import uuid

from utils.get_system import system
from utils.logger_config_class import YemenIPCCLogger

logger = YemenIPCCLogger().logger


class NetworkInterfaces:
    def __init__(self) -> None:
        self.interfaces = self.get_interfaces()

    def get_interfaces(self):
        interfaces = {}
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    interfaces[interface] = {"mac": addr.address}
        return interfaces

    @property
    def wifi(self):
        for interface, details in self.interfaces.items():
            if "wlp" in interface or "wl" in interface:
                return details["mac"]
        return None

    @property
    def lan(self):
        for interface, details in self.interfaces.items():
            if "en" in interface or "enp" in interface:
                return details["mac"]
        return None


class Serial:
    def __init__(self) -> None:
        self.network = NetworkInterfaces()

    @property
    def macaddr(self):
        wifi = self.network.wifi
        lan = self.network.lan
        another_way = ":".join(
            ["{:02x}".format((uuid.getnode() >> i) & 0xFF) for i in range(0, 8 * 6, 8)][
                ::-1
            ]
        )

        if wifi:
            return wifi
        elif lan:
            return lan
        elif another_way:
            return another_way

    @property
    def motherboardSerialNumber(self):
        try:
            if system == "Mac":
                serial_number = [
                    x.split('"')[3]
                    for x in subprocess.check_output(
                        ["ioreg", "-l"], text=True, encoding="utf-8", errors="ignore"
                    ).splitlines()
                    if "IOPlatformSerialNumber" in x
                ]

                return (
                    serial_number[0] if serial_number else "Unknown-Motherboard-Serial"
                )

            elif system == "Windows":
                return (
                    subprocess.check_output(
                        ["wmic", "baseboard", "get", "serialnumber"],
                        creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
                    )
                    .decode()
                    .split("\n")[1]
                    .strip()
                )

            elif system == "Linux":
                return "Unknown-Motherboard-Serial"
        except Exception as e:
            logger.debug(f"unable to get motherboard serial, error {e}")
            return "Unknown-Motherboard-Serial"

    @property
    def getUUID(self):
        try:
            return str(uuid.uuid1())  # Time-based UUID with the machine’s MAC address
        except:
            return "Unknown-UUID"

    @property
    def cpuID(self):
        try:
            if system == "Windows":
                proc_id = (
                    subprocess.check_output(
                        ["wmic", "cpu", "get", "ProcessorId"],
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
                    )
                    .split("\n")[2]
                    .strip()
                )

                return proc_id if proc_id else "Unknown-CPU-ID"

            elif system == "Linux":
                return "Unknown-CPU-ID"

            elif system == "Mac":
                return (
                    subprocess.check_output(
                        ["sysctl", "-n", "machdep.cpu.brand_string"]
                    )
                    .decode()
                    .strip()
                )

        except Exception as e:
            logger.debug(f"unable to get cpu id, error: {e}")
            return "Unknown-CPU-ID"

    @property
    def storageSerialNumber(self):
        try:
            if system == "Windows":
                return (
                    subprocess.check_output(
                        ["wmic", "diskdrive", "get", "serialnumber"],
                        creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
                    )
                    .decode()
                    .split("\n")[1]
                    .strip()
                )
            elif system == "Mac":
                return "Unknown-Disk-Serial"
                # return subprocess.check_output("sudo hdparm -I /dev/sda | grep 'Serial Number'", shell=True).decode().split(':')[1].strip()
            elif system == "Linux":
                output = subprocess.check_output(
                    ["lsblk", "-o", "NAME,SERIAL"],
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                ).splitlines()

                serial = [
                    line.replace(" ", "").removeprefix("sda")
                    for line in output
                    if "sda " in line
                ]

                return serial[0] if serial else "Unknown-Disk-Serial"
        except Exception as e:
            logger.debug(f"unable to get disk serial, error: {e}")
            return "Unknown-Disk-Serial"

        # try:
        #     output = subprocess.check_output(
        #         ["lsblk", "-o", "NAME,SERIAL"],
        #         text=True,
        #         encoding="utf-8",
        #         errors="ignore",
        #     ).splitlines()

        #     serial = [
        #         line.replace(" ", "").removeprefix("sda")
        #         for line in output
        #         if "sda " in line
        #     ]

        #     return serial[0] if serial else self.macaddr

        # except Exception:
        #     return self.macaddr

    @property
    def crossSystemSerial(self):
        cpu_id = self.cpuID
        mac_address = self.macaddr
        motherboard_serial = self.motherboardSerialNumber
        disk_serial = self.storageSerialNumber
        # device_uuid = self.getUUID

        # Concatenate all identifiers
        fingerprint_data = f"{cpu_id}{mac_address}{motherboard_serial}{disk_serial}"

        # Create a SHA-256 hash of the concatenated string
        # fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()

        return fingerprint_data
        # match system:
        #     case "Windows":
        #         return self.cpuID
        #     case "Mac":
        #         return self.motherboardSerialNumber
        #     case "Linux":
        #         return self.storageSerialNumber


class UserCredentials:
    def __init__(self) -> None:
        self.serial = Serial()

    @property
    def ip(self) -> dict:
        try:
            result = requests.get(url="https://ipinfo.io", timeout=10)
            return result.json()
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e}"

    @property
    def user(self):
        return getpass.getuser()
