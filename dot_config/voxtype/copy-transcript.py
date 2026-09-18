#!/usr/bin/python3
"""Copy a transcript as a backup, then return it for Voxtype's normal typing."""
import subprocess
import sys

text = sys.stdin.buffer.read()
try:
    subprocess.run(
        ["wl-copy", "--type", "text/plain;charset=utf-8"],
        input=text,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=2,
        check=False,
    )
except (OSError, subprocess.TimeoutExpired):
    pass
sys.stdout.buffer.write(text)
