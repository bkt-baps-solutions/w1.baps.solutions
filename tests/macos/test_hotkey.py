"""Hotkey serialization / labelling round-trips (pure logic; no listener started)."""
import pytest
from pynput.keyboard import Key, KeyCode

from w1_macos import hotkey as hk

pytestmark = pytest.mark.macos


@pytest.mark.parametrize(
    "key",
    [
        Key.alt_r, Key.alt_l, Key.cmd_r, Key.cmd_l, Key.ctrl_r, Key.ctrl_l,
        Key.shift_r, KeyCode.from_char("a"), KeyCode.from_vk(96),
    ],
)
def test_serialize_parse_round_trip(key):
    assert hk.parse_key(hk.serialize_key(key)) == key


def test_parse_falls_back_to_right_option():
    assert hk.parse_key("") == Key.alt_r
    assert hk.parse_key("<vk_bad>") == Key.alt_r
    assert hk.parse_key("<not_a_real_key>") == Key.alt_r


def test_serialize_unknown_object_falls_back():
    assert hk.serialize_key(object()) == "<alt_r>"


def test_key_labels_match_what_macos_delivers():
    assert hk.key_label(hk.serialize_key(Key.alt_r)) == "Right ⌥"
    assert hk.key_label(hk.serialize_key(Key.alt_l)) == "Left ⌥"
    assert hk.key_label(hk.serialize_key(Key.cmd_r)) == "Right ⌘"
    assert hk.key_label("a") == "A"
    assert hk.key_label("<f13>") == "F13"


def test_set_binding_clears_held_state():
    listener = hk.HotkeyListener(on_start=lambda: None, on_stop=lambda: None)
    listener._held = True
    listener.set_binding(key="<cmd_r>", mode="toggle")  # listener not started -> no restart
    assert listener._held is False
    assert listener._key == Key.cmd_r
    assert listener._mode == "toggle"
