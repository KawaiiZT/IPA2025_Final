from netmiko import ConnectHandler
from pprint import pprint
import re

username = "admin"
password = "cisco"

def read_motd(ip: str | None = None) -> str:
    device_params = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": username,
        "password": password,
    }
    try:
        with ConnectHandler(**device_params) as ssh:
            out = ssh.send_command("show banner motd", use_textfsm=False).strip()
            if out:
                return out
    except Exception:
        return "Error: No MOTD Configured"

def gigabit_status(ip="10.0.15.61"):
    device_params = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": username,
        "password": password,
    }
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
