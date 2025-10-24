import os
import subprocess
import tempfile
from pathlib import Path

_SUPPRESS_PATTERNS = (
    "[DEPRECATION WARNING]",
    "Deprecation warnings can be disabled by setting `deprecation_warnings=False` in ansible.cfg",
    "[WARNING]: Deprecation warnings can be disabled",
)
def motd(ip: str, motd_text: str) -> str:
    STUDENT_ID   = os.getenv("STUDENT_ID", "66070069")
    ROUTER_NAME  = os.getenv("ROUTER_NAME", "CSR1KV")
    PLAYBOOK     = os.getenv("ANSIBLE_MOTD_PLAYBOOK", "ansible/playbook_motd.yaml")

    ansible_user = os.getenv("ANSIBLE_USER", "")
    ansible_pass = os.getenv("ANSIBLE_PASSWORD", "")       # <= สำคัญสำหรับ ASKPASS
    enable_pass  = os.getenv("ANSIBLE_ENABLE_PASSWORD", "")  # ว่างได้ ถ้าไม่ต้อง enable
    ssh_key_path = os.getenv("ANSIBLE_SSH_PRIVATE_KEY", "")  # ว่างได้

    if not ansible_user:
        return "Error: Ansible\nMissing ANSIBLE_USER in environment (.env)"
    if not os.path.exists(PLAYBOOK):
        return f"Error: Playbook not found: {PLAYBOOK}"

    # expand ~ ใน path key (ถ้ากำหนด)
    exp_key = os.path.expanduser(ssh_key_path) if ssh_key_path else ""

    tmpdir = tempfile.TemporaryDirectory()
    vars_path = Path(tmpdir.name) / "extra_vars.json"
    vars_path.write_text(
        '{'
        f'"ip": {repr(ip)}, '
        f'"ansible_user": {repr(ansible_user)}, '
        f'"ansible_password": {repr(ansible_pass)}, '
        f'"enable_password": {repr(enable_pass)}, '
        f'"ssh_private_key_path": {repr(exp_key)}, '
        f'"motd": {repr(motd_text)}'
        '}',
        encoding="utf-8"
    )

    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"]     = "False"
    env["ANSIBLE_DEPRECATION_WARNINGS"]  = "False"
    env["ANSIBLE_DISPLAY_SKIPPED_HOSTS"] = "False"
    env["PYTHONWARNINGS"]                = "ignore"

    cmd = ["ansible-playbook", PLAYBOOK, "-e", f"@{vars_path}"]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=180)
        raw_output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        output = _clean_output(raw_output)
        print(output)

        if proc.returncode == 0 and "failed=0" in raw_output.lower():
            tmpdir.cleanup()
            return "Ok: success"
        else:
            tmpdir.cleanup()
            return "Error: Ansible"
    except Exception:
        tmpdir.cleanup()
        return "Error: Ansible"




def _clean_output(text: str, keep_tail_chars: int = 1500) -> str:
    """กรองบรรทัด warning/deprecation และตัดให้สั้นลง"""
    lines = []
    for line in text.splitlines():
        if any(pat in line for pat in _SUPPRESS_PATTERNS):
            continue
        lines.append(line)
    cleaned = "\n".join(lines)
    if len(cleaned) > keep_tail_chars:
        cleaned = cleaned[-keep_tail_chars:]
    # เก็บบรรทัดว่างให้น้อยลง
    cleaned = "\n".join([ln for ln in cleaned.splitlines() if ln.strip() != "" or True])
    return cleaned

def showrun():
    STUDENT_ID  = os.getenv("STUDENT_ID", "66070069")
    ROUTER_NAME = os.getenv("ROUTER_NAME", "CSR1KV")
    PLAYBOOK    = os.getenv("ANSIBLE_PLAYBOOK", "ansible/playbook_showrun.yaml")

    ansible_user = os.getenv("ANSIBLE_USER", "")
    ansible_pass = os.getenv("ANSIBLE_PASSWORD", "")
    enable_pass  = os.getenv("ANSIBLE_ENABLE_PASSWORD", "")

    if not ansible_user or not ansible_pass:
        return "Error: Ansible\nMissing ANSIBLE_USER/ANSIBLE_PASSWORD in environment (.env)"

    target_ip = "10.0.15.61"
    inv_lines = [
        "[routers]",
        (f"{ROUTER_NAME} ansible_host={target_ip} "
         f"ansible_user={ansible_user} ansible_password={ansible_pass} "
         f"ansible_network_os=ios").strip()
    ]
    if enable_pass:
        inv_lines += [
            "[routers:vars]",
            "ansible_become=True",
            "ansible_become_method=enable",
            f"ansible_become_password={enable_pass}",
        ]
    tmpdir = tempfile.TemporaryDirectory()
    inv_path = Path(tmpdir.name) / "inventory.ini"
    inv_path.write_text("\n".join(inv_lines) + "\n", encoding="utf-8")

    ssh_common_args = (
        "-oKexAlgorithms=+diffie-hellman-group14-sha1 "
        "-oHostKeyAlgorithms=+ssh-rsa "
        "-oPubkeyAcceptedAlgorithms=+ssh-rsa "
        "-oStrictHostKeyChecking=no"
    )

    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"]    = "False"
    env["ANSIBLE_DEPRECATION_WARNINGS"] = "False"
    env["ANSIBLE_DISPLAY_SKIPPED_HOSTS"]= "False"
    env["PYTHONWARNINGS"]               = "ignore"

    extra_vars = f"student_id={STUDENT_ID} router_name={ROUTER_NAME}"

    cmd = [
        "ansible-playbook",
        "-i", str(inv_path),
        "--ssh-common-args", ssh_common_args,
        "-e", "ansible_connection=network_cli",
        "-e", extra_vars,
        PLAYBOOK,
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=180)
        raw_output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        output = _clean_output(raw_output)  # กรอง warning ออก

        print(output)

        if proc.returncode == 0 and "failed=0" in raw_output.lower():
            tmpdir.cleanup()
            return "ok"
        else:
            tmpdir.cleanup()
            return f"Error: Ansible"
    except Exception as e:
        tmpdir.cleanup()
        return f"Error: Ansible"
