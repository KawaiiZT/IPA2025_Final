import os, glob, subprocess
from dotenv import load_dotenv

load_dotenv()
STUDENT_ID = os.getenv("STUDENT_ID", "66070069")

def showrun():
    cmd = [
        "ansible-playbook",
        "-i", "ansible/hosts",
        "ansible/playbook_showrun.yaml",
        "-e", f"student_id={STUDENT_ID}",
    ]
    env = os.environ.copy()
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    output = (proc.stdout or "") + (proc.stderr or "")
    print("Ansible error output:\n", output) if proc.returncode else None

    if proc.returncode != 0:
        return "Error: Ansible"

    files = sorted(glob.glob(f"show_run_{STUDENT_ID}_*.txt"), key=os.path.getmtime)
    if not files:
        return "Error: Ansible"

    latest = files[-1]
    target = f"show_run_{STUDENT_ID}_CSR1000V.txt"
    os.replace(latest, target)
    return "ok"
