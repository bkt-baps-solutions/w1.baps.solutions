"""Launch-at-login via a per-user LaunchAgent that opens the W1.app bundle at login.

We launch the ``.app`` bundle (``open -g``) rather than the raw dev script so the started
process inherits the app bundle's permission identity (Microphone / Accessibility / Input
Monitoring) — the same identity the user grants on first run. All operations are best-effort:
a failed ``launchctl`` call still leaves the plist in the right state for the next login.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

_LABEL = "solutions.baps.w1.login"
_APP = "/Applications/W1.app"

_PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>            <string>{label}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/open</string>
    <string>-g</string>
    <string>{app}</string>
  </array>
  <key>RunAtLoad</key>        <true/>
</dict>
</plist>
"""


def plist_path() -> Path:
    """Absolute path to the W1 login LaunchAgent plist."""
    return Path.home() / "Library" / "LaunchAgents" / f"{_LABEL}.plist"


def is_enabled() -> bool:
    """True when the login LaunchAgent is installed."""
    return plist_path().exists()


def set_enabled(enabled: bool) -> None:
    """Install (and load) or remove (and unload) the login LaunchAgent."""
    path = plist_path()
    if enabled:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_PLIST.format(label=_LABEL, app=_APP), encoding="utf-8")
        subprocess.run(
            ["/bin/launchctl", "load", "-w", str(path)], check=False, capture_output=True
        )
    elif path.exists():
        subprocess.run(
            ["/bin/launchctl", "unload", "-w", str(path)], check=False, capture_output=True
        )
        path.unlink(missing_ok=True)
