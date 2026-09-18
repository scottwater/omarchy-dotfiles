#!/usr/bin/env python3
"""Capture a read-only inventory. Never install, enable, remove, or apply anything."""

import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()


def run(*args, allow_empty=False):
    result = subprocess.run(
        args, text=True, cwd=HOME, timeout=60, capture_output=True,
        env={**os.environ, "LC_ALL": "C", "NO_COLOR": "1"},
    )
    # pacman uses exit 1 for a query with no matching packages.
    if allow_empty and result.returncode == 1 and not result.stdout.strip() and not result.stderr.strip():
        return ""
    result.check_returncode()
    return result.stdout.strip()


def lines(value):
    return "\n".join(sorted(set(value.splitlines()))) + "\n" if value else ""


def formatted(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def collect():
    if not shutil.which("pacman"):
        raise RuntimeError("This inventory is for an Arch/Omarchy machine (pacman missing).")
    records = {
        "packages-explicit-native.txt": lines(run("pacman", "-Qqen", allow_empty=True)),
        "packages-explicit-foreign.txt": lines(run("pacman", "-Qqem", allow_empty=True)),
        "packages-all-versions.txt": lines(run("pacman", "-Q")),
        "omarchy-version.txt": run("pacman", "-Q", "omarchy") + "\n",
    }
    if shutil.which("mise"):
        installed = json.loads(run("mise", "ls", "--json"))
        records["mise-tools.json"] = formatted({
            tool: sorted([
                {key: entry[key] for key in
                 ("version", "requested_version", "installed", "active") if key in entry}
                for entry in entries
            ], key=lambda entry: entry.get("version", ""))
            for tool, entries in installed.items()
        })
    for scope in ("system", "user"):
        flags = ("--user",) if scope == "user" else ()
        records[f"services-enabled-{scope}.txt"] = lines(run(
            "systemctl", *flags, "list-unit-files", "--state=enabled",
            "--no-legend", "--no-pager",
        ))
    if shutil.which("flatpak"):
        records["flatpak-apps.txt"] = lines(run(
            "flatpak", "list", "--app", "--columns=application,origin,branch,installation",
        ))
    records["theme.txt"] = run("omarchy", "theme", "current") + "\n"
    plugin = HOME / ".config/omarchy/plugins/sh.lerd.glance"
    if (plugin / ".git").exists():
        url = run("git", "-C", str(plugin), "remote", "get-url", "origin")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise RuntimeError("Plugin origin is not a plain HTTPS URL; review before recording it.")
        records["shell-plugin.json"] = formatted({
            "path": ".config/omarchy/plugins/sh.lerd.glance",
            "url": url,
            "commit": run("git", "-C", str(plugin), "rev-parse", "HEAD"),
            "dirty": bool(run("git", "-C", str(plugin), "status", "--porcelain")),
        })
    return records


def main():
    host = socket.gethostname()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", host):
        raise RuntimeError("Unsafe hostname for inventory directory.")
    # Gather everything before updating any files. A failed query preserves the old inventory.
    records = collect()
    target = ROOT / "inventory" / host
    target.mkdir(parents=True, exist_ok=True)
    changed = 0
    for name, content in records.items():
        path = target / name
        if path.exists() and path.read_text() == content:
            continue
        with tempfile.NamedTemporaryFile(mode="w", dir=target, delete=False) as output:
            output.write(content)
            tmp = Path(output.name)
        tmp.replace(path)
        changed += 1
    print(f"Inventory: {target} ({changed} files changed)")
    print("These are observations, not a package installation or service-enablement manifest.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Inventory failed: {exc}", file=sys.stderr)
        sys.exit(1)
