"""Native Settings window for the W1 menu-bar app (PyObjC / AppKit).

A small, premium dark panel — "Make W1 yours". It edits the live ``W1Config`` in place and
persists every change immediately, applying it to the running app (rebinds the global hotkey,
switches correction mode, toggles launch-at-login) so nothing requires a relaunch.

UI work happens on the main thread only; the press-to-capture rebind marshals its result back
via ``AppHelper.callAfter``.
"""
from __future__ import annotations

import objc
from AppKit import (
    NSApp,
    NSBackingStoreBuffered,
    NSBox,
    NSButton,
    NSButtonTypeSwitch,
    NSColor,
    NSFont,
    NSSegmentedControl,
    NSSegmentSwitchTrackingSelectOne,
    NSTextField,
    NSView,
    NSVisualEffectBlendingModeBehindWindow,
    NSVisualEffectMaterialSidebar,
    NSVisualEffectStateActive,
    NSVisualEffectView,
    NSWindow,
    NSWindowStyleMaskClosable,
    NSWindowStyleMaskTitled,
)
from Foundation import NSObject
from PyObjCTools import AppHelper

from w1_core.config import HotkeyMode
from w1_macos import login_item
from w1_macos.hotkey import capture_once, key_label

_W, _H = 520.0, 336.0
_SAFFRON = NSColor.colorWithSRGBRed_green_blue_alpha_(0.91, 0.53, 0.05, 1.0)
_MUTED = NSColor.secondaryLabelColor()


def _flipped(frame):
    view = _FlippedView.alloc().initWithFrame_(frame)
    return view


class _FlippedView(NSView):
    """Top-left origin so the layout below reads top-to-bottom."""

    def isFlipped(self) -> bool:  # noqa: N802 (AppKit selector)
        return True


def _label(text, frame, *, size=13.0, bold=False, color=None):
    f = NSTextField.alloc().initWithFrame_(frame)
    f.setStringValue_(text)
    f.setBezeled_(False)
    f.setDrawsBackground_(False)
    f.setEditable_(False)
    f.setSelectable_(False)
    f.setFont_(NSFont.boldSystemFontOfSize_(size) if bold else NSFont.systemFontOfSize_(size))
    if color is not None:
        f.setTextColor_(color)
    return f


def _divider(y):
    box = NSBox.alloc().initWithFrame_(((28, y), (_W - 56, 1)))
    box.setBoxType_(2)  # NSBoxSeparator
    return box


class SettingsWindow(NSObject):
    """Owns the NSWindow and is the action target for its controls."""

    def initWithApp_(self, app):  # noqa: N802 (AppKit selector)
        self = objc.super(SettingsWindow, self).init()
        if self is None:
            return None
        self._app = app
        self._capture = None
        self._build()
        return self

    # -- construction ---------------------------------------------------------
    def _build(self) -> None:
        style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
        win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            ((0, 0), (_W, _H)), style, NSBackingStoreBuffered, False
        )
        win.setTitle_("W1 Settings")
        win.setReleasedWhenClosed_(False)
        try:
            from AppKit import NSAppearance, NSAppearanceNameVibrantDark

            win.setAppearance_(NSAppearance.appearanceNamed_(NSAppearanceNameVibrantDark))
        except Exception:  # pragma: no cover - cosmetic only
            pass

        bg = NSVisualEffectView.alloc().initWithFrame_(((0, 0), (_W, _H)))
        bg.setMaterial_(NSVisualEffectMaterialSidebar)
        bg.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
        bg.setState_(NSVisualEffectStateActive)

        content = _flipped(((0, 0), (_W, _H)))

        cfg = self._app.config

        # Header
        content.addSubview_(_label("Settings", ((28, 22), (300, 30)), size=22, bold=True))
        content.addSubview_(
            _label("Make W1 yours", ((28, 52), (300, 18)), size=13, color=_MUTED)
        )

        # -- Hotkey row --
        y = 92.0
        content.addSubview_(_label("Hotkey", ((28, y), (200, 18)), size=14, bold=True))
        self._keychip = _label(
            f"Hold {key_label(cfg.hotkey)} to talk", ((28, y + 22), (300, 16)),
            size=12, color=_MUTED,
        )
        content.addSubview_(self._keychip)
        self._rebind = NSButton.alloc().initWithFrame_(((_W - 140, y - 2), (110, 30)))
        self._rebind.setTitle_("Rebind")
        self._rebind.setBezelStyle_(1)  # rounded
        self._rebind.setTarget_(self)
        self._rebind.setAction_("rebind:")
        content.addSubview_(self._rebind)
        content.addSubview_(_divider(y + 52))

        # -- Activation row --
        y = 168.0
        content.addSubview_(_label("Activation", ((28, y), (220, 18)), size=14, bold=True))
        content.addSubview_(
            _label("How the hotkey triggers", ((28, y + 22), (260, 16)), size=12, color=_MUTED)
        )
        seg = NSSegmentedControl.segmentedControlWithLabels_trackingMode_target_action_(
            ["Hold to talk", "Double-tap"],
            NSSegmentSwitchTrackingSelectOne,
            self,
            "activationChanged:",
        )
        seg.setFrame_(((_W - 230, y - 2), (200, 28)))
        seg.setSelectedSegment_(0 if cfg.hotkey_mode is HotkeyMode.push_to_talk else 1)
        self._seg = seg
        content.addSubview_(seg)
        content.addSubview_(_divider(y + 52))

        # -- Launch at login row --
        y = 244.0
        content.addSubview_(_label("Launch at login", ((28, y), (240, 18)), size=14, bold=True))
        content.addSubview_(
            _label("Start W1 when you log in", ((28, y + 22), (260, 16)), size=12, color=_MUTED)
        )
        cb = NSButton.alloc().initWithFrame_(((_W - 80, y), (50, 22)))
        cb.setButtonType_(NSButtonTypeSwitch)
        cb.setTitle_("")
        cb.setState_(1 if login_item.is_enabled() else 0)
        cb.setTarget_(self)
        cb.setAction_("loginChanged:")
        content.addSubview_(cb)

        # -- Privacy footer --
        footer = _label(
            "100% on-device. No audio or transcript is stored unless you choose to.",
            ((28, _H - 34), (_W - 56, 18)),
            size=11,
            color=_SAFFRON,
        )
        content.addSubview_(footer)

        bg.addSubview_(content)
        win.setContentView_(bg)
        self._window = win

    # -- actions --------------------------------------------------------------
    def rebind_(self, sender) -> None:  # noqa: N802
        sender.setEnabled_(False)
        sender.setTitle_("Press a key…")

        def _captured(key_str: str) -> None:
            AppHelper.callAfter(self._apply_hotkey, key_str)

        self._capture = capture_once(_captured)

    def _apply_hotkey(self, key_str: str) -> None:
        self._app.config.hotkey = key_str
        self._app.hotkey.set_binding(key=key_str)
        self._app.save_settings()
        self._keychip.setStringValue_(f"Hold {key_label(key_str)} to talk")
        self._rebind.setTitle_("Rebind")
        self._rebind.setEnabled_(True)
        self._capture = None

    def activationChanged_(self, sender) -> None:  # noqa: N802
        mode = HotkeyMode.push_to_talk if sender.selectedSegment() == 0 else HotkeyMode.toggle
        self._app.config.hotkey_mode = mode
        self._app.hotkey.set_binding(mode=mode.value)
        self._app.save_settings()
        verb = "Hold" if mode is HotkeyMode.push_to_talk else "Double-tap"
        self._keychip.setStringValue_(f"{verb} {key_label(self._app.config.hotkey)} to talk")

    def loginChanged_(self, sender) -> None:  # noqa: N802
        login_item.set_enabled(bool(sender.state()))

    # -- presentation ---------------------------------------------------------
    def show(self) -> None:
        self._window.center()
        self._window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)
