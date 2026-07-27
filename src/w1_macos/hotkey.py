"""Global hotkey listener. Two modes, switchable in config:

* push_to_talk — hold the key to talk, release to insert (default; conflict-free since you're
  speaking, not typing, while it's held).
* toggle — double-tap the key to start, double-tap again to stop (double-tap, not single, so an
  ordinary Right-Option keypress during typing never triggers it).

Default key: Right-Option (``<alt_r>``). Never Cmd+M.

The hotkey is persisted as a string and round-trips through ``serialize_key`` / ``parse_key``
so the Settings window can rebind it to whatever key the user presses (press-to-capture).
"""
from __future__ import annotations

import time
from typing import Callable

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

# Human-readable labels for the common modifier keys (used by the Settings window).
# macOS pynput reports left modifiers under their bare name (``alt``/``cmd``/``ctrl``/``shift``)
# and right modifiers with the ``_r`` suffix; both forms are mapped so either round-trips.
_LABELS = {
    "<alt_r>": "Right ⌥",
    "<alt>": "Left ⌥",
    "<alt_l>": "Left ⌥",
    "<cmd_r>": "Right ⌘",
    "<cmd>": "Left ⌘",
    "<cmd_l>": "Left ⌘",
    "<ctrl_r>": "Right ⌃",
    "<ctrl>": "Left ⌃",
    "<ctrl_l>": "Left ⌃",
    "<shift_r>": "Right ⇧",
    "<shift>": "Left ⇧",
    "<shift_l>": "Left ⇧",
    "<fn>": "Fn",
}


def serialize_key(k) -> str:
    """Serialize a pynput key to a stable config string (``"<alt_r>"``, ``"a"``, ``"<vk_96>"``)."""
    if isinstance(k, Key):
        return f"<{k.name}>"
    if isinstance(k, KeyCode):
        if k.char:
            return k.char
        if k.vk is not None:
            return f"<vk_{k.vk}>"
    return "<alt_r>"


def parse_key(s: str):
    """Inverse of :func:`serialize_key`; falls back to Right-Option for anything unrecognised."""
    if s.startswith("<") and s.endswith(">"):
        inner = s[1:-1]
        if inner.startswith("vk_"):
            try:
                return KeyCode.from_vk(int(inner[3:]))
            except ValueError:
                return Key.alt_r
        return getattr(Key, inner, Key.alt_r)
    return KeyCode.from_char(s[0]) if s else Key.alt_r


def key_label(s: str) -> str:
    """A short, human-readable label for a serialized key (for the Settings window chip)."""
    if s in _LABELS:
        return _LABELS[s]
    if s.startswith("<") and s.endswith(">"):
        return s[1:-1].replace("_", " ").title()
    return s.upper()


def capture_once(on_captured: Callable[[str], None]) -> "keyboard.Listener":
    """Start a one-shot global listener; serialize the first key pressed, then stop itself.

    The callback fires on pynput's listener thread — marshal any UI work back to the main
    thread (e.g. via ``AppHelper.callAfter``). Returns the listener so the caller can cancel it.
    """
    listener: keyboard.Listener

    def _on_press(k) -> bool:
        on_captured(serialize_key(k))
        return False  # returning False stops the listener after the first key

    listener = keyboard.Listener(on_press=_on_press)
    listener.start()
    return listener


class HotkeyListener:
    def __init__(
        self,
        *,
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
        mode: str = "push_to_talk",
        key: str = "<alt_r>",
        double_tap_window: float = 0.4,
    ):
        self._on_start = on_start
        self._on_stop = on_stop
        self._mode = mode
        self._key = parse_key(key)
        self._window = double_tap_window
        self._held = False
        self._toggled_on = False
        self._last_press = 0.0
        self._listener: keyboard.Listener | None = None

    def _on_press(self, k) -> None:
        if k != self._key:
            return
        if self._mode == "push_to_talk":
            if not self._held:
                self._held = True
                self._on_start()
        else:  # toggle via double-tap
            now = time.monotonic()
            if now - self._last_press <= self._window:
                self._toggled_on = not self._toggled_on
                (self._on_start if self._toggled_on else self._on_stop)()
                self._last_press = 0.0
            else:
                self._last_press = now

    def _on_release(self, k) -> None:
        if k != self._key:
            return
        if self._mode == "push_to_talk" and self._held:
            self._held = False
            self._on_stop()

    def set_binding(self, *, key: str | None = None, mode: str | None = None) -> None:
        """Rebind the key and/or activation mode live, restarting the listener if running.

        Any in-progress hold/toggle state is cleared so a rebind can never leave the app stuck
        thinking the old key is still down.
        """
        if key is not None:
            self._key = parse_key(key)
        if mode is not None:
            self._mode = mode
        self._held = False
        self._toggled_on = False
        self._last_press = 0.0
        if self._listener is not None:
            self.stop()
            self.start()

    def start(self) -> None:
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
