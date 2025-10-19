import subprocess
def showrun():
    command = ['ansible-playbook', 'showrun_playbook.yaml']
    result = subprocess.run(command, capture_output=True, text=True)
    result = result.stdout
    if 'failed=0' in result and 'unreachable=0' in result:
        return 'ok'
    else:
        return 'Error: Ansible'
