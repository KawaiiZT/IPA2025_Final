import json
import requests
import os
from dotenv import load_dotenv

requests.packages.urllib3.disable_warnings()
load_dotenv()

basicauth = ("admin", "cisco")

METHOD = None
api_url = None

def set_url(ip: str):
    """ตั้งค่า api_url ตาม IP ที่รับมา"""
    global api_url
    api_url = f"https://{ip}/restconf/data/ietf-interfaces:interfaces/interface=Loopback66070069"

headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

def command(cmd: str) -> str:
    """พาร์เซอร์แบบง่าย: /<sid> restconf | /<sid> netconf | /<sid> <ip> create"""
    global METHOD

    parts = cmd.strip().split()
    if not parts:
        return "Error: No command found."

    first = parts[0]
    if not first.startswith("/") or len(first) < 2:
        return "Error: No command found."
    sid = first[1:]

    if len(parts) == 2:
        token = parts[1].lower()
        if token == "restconf":
            METHOD = "restconf"
            return "Ok: Restconf"
        if token == "netconf":
            METHOD = "netconf"
            return "Ok: Netconf"
        if token == "create":
            if METHOD is None:
                return "Error: No method specified"
            return "Error: No IP specified"
        return "Error: No command found."

    if len(parts) == 3:
        ip, action = parts[1], parts[2].lower()
        if action != "create":
            return "Error: No command found."
        if METHOD is None:
            return "Error: No method specified"

        if METHOD == "restconf":
            set_url(ip)
            return create(ip, sid)
        elif METHOD == "netconf":
            return f"Interface loopback {sid} is created successfully using Netconf"

    return "Error: No command found."

def create(ip: str, sid: str) -> str:
    """สร้าง Loopback66070069 ด้วย RESTCONF ที่อุปกรณ์ IP = ip"""
    if not api_url:
        set_url(ip)

    check = requests.get(api_url, auth=basicauth, headers=headers, verify=False)
    if 200 <= check.status_code <= 299:
        return f"Cannot create: Interface loopback {sid}"
    elif check.status_code not in (404,):
        print(f"Pre-check error. Status Code: {check.status_code}")
        print("Detail:", check.text)

    yangConfig = {
        "ietf-interfaces:interface": {
            "name": "Loopback66070069",
            "description": "Router ID",
            "type": "iana-if-type:softwareLoopback",
            "enabled": False,
            "ietf-ip:ipv4": {
                "address": [
                    {"ip": "172.0.69.1", "netmask": "255.255.255.0"}
                ]
            }
        }
    }

    resp = requests.put(
        api_url,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if 200 <= resp.status_code <= 299:
        return f"Interface loopback {sid} is created successfully using Restconf"
    else:
        print('Error. Status Code:', resp.status_code)
        print('Detail:', resp.text)
        return "Error: Interface Loopback 66070069 cannot be create"
def delete():
    if not api_url:
        return "Error: No IP specified"
    check = requests.get(api_url, auth=basicauth, headers=headers, verify=False)
    if check.status_code == 404:
        return "Error: No Interface Loopback 66070069"
    elif not (200 <= check.status_code <= 299):
        print(f"Pre-check error. Status Code: {check.status_code}")
        print("Detail:", check.text)
        return "Error: Interface Loopback 66070069 cannot be delete"
    
    resp = requests.delete(api_url, auth=basicauth, headers=headers, verify=False)
    if 200 <= resp.status_code <= 299:
        return "Interface Loopback 66070069 is deleted"
    else:
        print('Error. Status Code:', resp.status_code)
        return "Error: Interface Loopback 66070069 cannot be delete"

def enable():
    if not api_url:
        return "Error: No IP specified"
    check = requests.get(api_url, auth=basicauth, headers=headers, verify=False)
    if check.status_code == 404:
        return "Error: No Interface Loopback 66070069"
    elif not (200 <= check.status_code <= 299):
        print(f"Pre-check error. Status Code: {check.status_code}")
        print("Detail:", check.text)
        return "Error: Interface Loopback 66070069 cannot be enable"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": "Loopback66070069",
            "description": "Router ID",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {"ip": "172.0.69.1", "netmask": "255.255.255.0"}
                ]
            }
        }
    }

    resp = requests.put(api_url, data=json.dumps(yangConfig),
                        auth=basicauth, headers=headers, verify=False)
    if 200 <= resp.status_code <= 299:
        return "Interface Loopback 66070069 is now enabled"
    else:
        print('Error. Status Code:', resp.status_code)
        return "Error: Interface Loopback 66070069 cannot be enable"

def disable():
    if not api_url:
        return "Error: No IP specified"
    check = requests.get(api_url, auth=basicauth, headers=headers, verify=False)
    if check.status_code == 404:
        return "Error: No Interface Loopback 66070069"
    elif not (200 <= check.status_code <= 299):
        print(f"Pre-check error. Status Code: {check.status_code}")
        print("Detail:", check.text)
        return "Error: Interface Loopback 66070069 cannot be disable"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": "Loopback66070069",
            "description": "Router ID",
            "type": "iana-if-type:softwareLoopback",
            "enabled": False,
            "ietf-ip:ipv4": {
                "address": [
                    {"ip": "172.0.69.1", "netmask": "255.255.255.0"}
                ]
            }
        }
    }

    resp = requests.put(api_url, data=json.dumps(yangConfig),
                        auth=basicauth, headers=headers, verify=False)
    if 200 <= resp.status_code <= 299:
        return "Interface Loopback 66070069 is now disable"
    else:
        print('Error. Status Code:', resp.status_code)
        return "Error: Interface Loopback 66070069 cannot be disable"

def status(ip: str):
    """แก้ URL ให้ถูก และรับ ip มาด้วย"""
    url = f"https://{ip}/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback66070069"
    resp = requests.get(url, auth=basicauth, headers=headers, verify=False)

    if 200 <= resp.status_code <= 299:
        try:
            data = resp.json().get("ietf-interfaces:interface")
            iface = data[0] if isinstance(data, list) and data else data
            admin_status = iface.get("admin-status")
            oper_status  = iface.get("oper-status")
            if admin_status == 'up' and oper_status == 'up':
                return "Interface Loopback 66070069 is enabled"
            elif admin_status == 'down' and oper_status == 'down':
                return "Interface Loopback 66070069 is disabled"
            else:
                return f"Interface Loopback 66070069 -> admin:{admin_status}, oper:{oper_status}"
        except Exception:
            return "Error: Unexpected response format"
    elif resp.status_code == 404:
        return "Error: No Interface Loopback 66070069"
    else:
        print('Error. Status Code:', resp.status_code, 'Detail:', resp.text)
        return "Error: Cannot get status"
