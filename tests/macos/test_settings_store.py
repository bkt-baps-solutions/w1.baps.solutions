"""Config persistence: round-trip, defaults when absent, defaults when corrupt."""
import pytest

from w1_core.config import HotkeyMode, W1Config
from w1_macos import settings_store as ss

pytestmark = pytest.mark.macos


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(ss, "_APP_SUPPORT", tmp_path)
    return ss


def test_load_returns_defaults_when_no_file(store):
    assert store.load_config() == W1Config()


def test_save_then_load_round_trips(store):
    cfg = W1Config(hotkey="<cmd_r>", hotkey_mode=HotkeyMode.toggle)
    store.save_config(cfg)
    got = store.load_config()
    assert got.hotkey == "<cmd_r>"
    assert got.hotkey_mode is HotkeyMode.toggle


def test_corrupt_file_falls_back_to_defaults(store):
    store.config_path().parent.mkdir(parents=True, exist_ok=True)
    store.config_path().write_text("{ not valid json", encoding="utf-8")
    assert store.load_config() == W1Config()
