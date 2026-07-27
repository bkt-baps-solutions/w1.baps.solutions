"""Launch-at-login LaunchAgent install/remove (launchctl stubbed out)."""
import subprocess

import pytest

from w1_macos import login_item as li

pytestmark = pytest.mark.macos


@pytest.fixture
def agent(tmp_path, monkeypatch):
    path = tmp_path / "login.plist"
    monkeypatch.setattr(li, "plist_path", lambda: path)
    monkeypatch.setattr(
        li.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0)
    )
    return path


def test_disabled_by_default(agent):
    assert li.is_enabled() is False


def test_enable_writes_plist_pointing_at_the_app(agent):
    li.set_enabled(True)
    assert agent.exists()
    assert li.is_enabled() is True
    assert "/Applications/W1.app" in agent.read_text()


def test_disable_removes_plist(agent):
    li.set_enabled(True)
    li.set_enabled(False)
    assert not agent.exists()
    assert li.is_enabled() is False
