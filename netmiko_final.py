from netmiko import ConnectHandler
from pprint import pprint
from dotenv import load_dotenv
import os
load_dotenv
device_ip = os.getenv("ip")
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
}


def gigabit_status():
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        result = ssh.send_command("show ip int brief", use_textfsm=True)
        parts = []
        for status in result:
            if status["interface"].startswith("Gigabit"):
                intf = status["interface"]
                state = status["status"]
                parts.append(f"{intf} {state}")
                if state == "up":
                    up += 1
                elif state == "down":
                    down += 1
                elif state == "administratively down":
                    admin_down += 1

        ans = ", ".join(parts) + f" -> {up} up, {down}  down, {admin_down} administratively down"
        pprint(ans)
        return ans
