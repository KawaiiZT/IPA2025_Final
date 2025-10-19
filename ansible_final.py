# ansible_final.py  (คงรูปแบบเดิมของโค้ด/ฟังก์ชัน showrun)
import os, glob, subprocess, requests
from dotenv import load_dotenv

requests.packages.urllib3.disable_warnings()
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ROOM_ID = os.getenv("roomid")
STUDENT_ID = os.getenv("STUDENT_ID", "66070069")

def showrun():
    cmd = ["ansible-playbook", "-i", "hosts", "playbook_showrun.yaml", "-e", f"student_id={STUDENT_ID}"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")

    ok = ("failed=0" in output) and ("unreachable=0" in output) and (proc.returncode == 0)
    if not ok:
        requests.post(
            "https://webexapis.com/v1/messages",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            data={"roomId": ROOM_ID, "text": "Error: Ansible"},
            verify=False,
        )
        return "Error: Ansible"

    files = sorted(glob.glob(f"show_run_{STUDENT_ID}_*.txt"), key=os.path.getmtime)
    if not files:
        requests.post(
            "https://webexapis.com/v1/messages",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            data={"roomId": ROOM_ID, "text": "Error: Ansible"},
            verify=False,
        )
        return "Error: Ansible"

    for f in files:
        with open(f, "rb") as fh:
            requests.post(
                "https://webexapis.com/v1/messages",
                headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
                data={"roomId": ROOM_ID},  # ส่งไฟล์อย่างเดียว ไม่มีข้อความประกอบ
                files={"files": (os.path.basename(f), fh, "text/plain")},
                verify=False,
            )

    requests.post(
        "https://webexapis.com/v1/messages",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        data={"roomId": ROOM_ID, "text": "show running config"},
        verify=False,
    )
    return "OK"

