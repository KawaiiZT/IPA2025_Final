import json
import requests
import os
from dotenv import load_dotenv
requests.packages.urllib3.disable_warnings()
load_dotenv()
ip = os.getenv("ip")
# Router IP Address is 10.0.15.61-65
api_url = "https://{ip}/restconf/data/ietf-interfaces:interfaces/interface=Loopback66070069"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = ("admin", "cisco")


def create():
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": "Loopback0",
            "description": "Router ID",
            "type": "iana-if-type:softwareLoopback",
            "enabled": False,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": "172.0.69.1",
                        "netmask": "255.255.255.0"
                    }
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

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface Loopback 66070069 is created successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Error: Interface Loopback 66070069 cannot be create"


def delete():
    resp = requests.delete(
        api_url,
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface Loopback 66070069 is deleted"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Error: Interface Loopback 66070069 cannot be delete"


def enable():
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": "Loopback0",
            "description": "Router ID",
            "type": "iana-if-type:softwareLoopback",
            "enabled": False,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": "172.0.69.1",
                        "netmask": "255.255.255.0"
                    }
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

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface Loopback 66070069 is now enabled"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Error: Interface Loopback 66070069 cannot be enable"


def disable():
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": "Loopback0",
            "description": "Router ID",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": "172.0.69.1",
                        "netmask": "255.255.255.0"
                    }
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

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface Loopback 66070069 is now disable"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return "Error: Interface Loopback 66070069 cannot be disable"


def status():
    api_url_status = "https://10.0.15.61/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback66070069="

    resp = requests.get(api_url_status, auth=basicauth, headers=headers, verify=False)

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
        oper_status = response_json["ietf-interfaces:interface"]["oper_status"]
        if admin_status == 'up' and oper_status == 'up':
            return "Interface Loopback 66070069 is enabled"
        elif admin_status == 'down' and oper_status == 'down':
            return "Interface Loopback 66070069 is disabled"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return "Error: No Interface Loopback 66070069"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
