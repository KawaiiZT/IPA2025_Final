from ncclient import manager
import xmltodict

USERNAME = "admin"
PASSWORD = "cisco"
PORT     = 830
IF_NAME  = "Loopback66070069"
IF_DESC  = "Router ID"
IF_IP    = "172.0.69.1"
IF_MASK  = "255.255.255.0"

def _connect(ip: str):

    return manager.connect(
        host=ip,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
        timeout=30
    )

def _get_iface_cfg(ip: str):
    flt = f"""
<filter>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>{IF_NAME}</name>
      <enabled/>
    </interface>
  </interfaces>
</filter>""".strip()
    with _connect(ip) as m:
        reply = m.get_config(source="running", filter=flt)
    return reply

def _iface_exists(ip: str) -> bool:
    reply = _get_iface_cfg(ip)
    return IF_NAME in reply.xml

def _is_enabled(ip: str) -> bool | None:
    reply = _get_iface_cfg(ip)
    d = xmltodict.parse(reply.xml)
    try:
        data = d["rpc-reply"]["data"]["interfaces"]["interface"]
        if isinstance(data, list):
            data = data[0]
        enabled = data.get("enabled")
        if enabled is None:
            return True
        return True if str(enabled).lower() == "true" else False
    except Exception:
        return None
    
def create(ip: str, sid: str) -> str:
    if _iface_exists(ip):
        return f"Cannot create: Interface loopback {IF_NAME.replace('Loopback','')}"

    config = f"""
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>{IF_NAME}</name>
      <description>{IF_DESC}</description>
      <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
      <enabled>false</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>{IF_IP}</ip>
          <netmask>{IF_MASK}</netmask>
        </address>
      </ipv4>
    </interface>
  </interfaces>
</config>""".strip()

    with _connect(ip) as m:
        r = m.edit_config(target="running", config=config)
    return (f"Interface loopback {IF_NAME.replace('Loopback','')} "
            f"is created successfully using Netconf") if "<ok/>" in r.xml \
           else "Cannot create: Interface loopback 66070069"



def delete(ip: str) -> str:
    if not _iface_exists(ip):
        return "Cannot delete: Interface loopback 66070069"

    config = f"""
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface operation="delete">
      <name>{IF_NAME}</name>
    </interface>
  </interfaces>
</config>""".strip()

    with _connect(ip) as m:
        r = m.edit_config(target="running", config=config)
    return "Interface loopback 66070069 is deleted successfully using Netconf" \
        if "<ok/>" in r.xml else "Cannot delete: Interface loopback 66070069"


def enable(ip: str) -> str:
    if not _iface_exists(ip):
        return "No Interface loopback 66070069 (checked by Netconf)"

    cur = _is_enabled(ip)
    if cur is True:
        return "Cannot enable: Interface loopback 66070069"

    config = f"""
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>{IF_NAME}</name>
      <enabled>true</enabled>
    </interface>
  </interfaces>
</config>""".strip()

    with _connect(ip) as m:
        r = m.edit_config(target="running", config=config)
    return "Interface loopback 66070069 is enabled successfully using Netconf" \
        if "<ok/>" in r.xml else "Cannot enable: Interface loopback 66070069"

def disable(ip: str) -> str:
    if not _iface_exists(ip):
        return "No Interface loopback 66070069 (checked by Netconf)"

    cur = _is_enabled(ip)
    if cur is False:
        return "Cannot shutdown: Interface loopback 66070069 (checked by Netconf)"

    config = f"""
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>{IF_NAME}</name>
      <enabled>false</enabled>
    </interface>
  </interfaces>
</config>""".strip()

    with _connect(ip) as m:
        r = m.edit_config(target="running", config=config)
    return "Interface loopback 66070069 is now disabled using Netconf" \
        if "<ok/>" in r.xml else "Cannot disable: Interface loopback 66070069"

def status(ip: str) -> str:
    if not _iface_exists(ip):
        return "No Interface loopback 66070069 (checked by Netconf)"

    cur = _is_enabled(ip)
    if cur is True:
        return "Interface loopback 66070069 is enabled (checked by Netconf)"
    elif cur is False:
        return "Interface loopback 66070069 is disabled (checked by Netconf)"
    else:
        return "Status unknown (checked by Netconf)"
