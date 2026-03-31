import subprocess
import os
import logging

log = logging.getLogger(__name__)

ANSIBLE_DIR = os.path.join(os.path.dirname(__file__), '..', 'ansible')

def run_playbook(playbook: str, target_host: str, extra_vars: dict = None) -> tuple:
    """
    Execute an Ansible playbook via subprocess.
    Returns (stdout, return_code).
    """
    if not playbook:
        log.info(f"No playbook for this fault type — skipping.")
        return "No playbook required.", 0

    playbook_path = os.path.join(ANSIBLE_DIR, 'playbooks', f'{playbook}.yml')

    cmd = [
        'ansible-playbook',
        playbook_path,
        '-e', f'target_host={target_host}',
    ]

    if extra_vars:
        for k, v in extra_vars.items():
            cmd += ['-e', f'{k}={v}']

    log.info(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=ANSIBLE_DIR,
            timeout=120
        )
        log.info(f"Playbook rc={result.returncode}")
        return result.stdout + result.stderr, result.returncode

    except subprocess.TimeoutExpired:
        log.error("Playbook timed out after 120 seconds")
        return "Playbook timed out.", 1
    except Exception as e:
        log.error(f"Playbook execution error: {e}")
        return str(e), 1
