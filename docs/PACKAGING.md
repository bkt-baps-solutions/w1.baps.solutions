# Packaging W1 as a macOS app

W1 ships two ways. For developers, `./install.sh` + `./w1 app` is the tested path. To hand a
double-clickable app to non-technical users, build a `.app` bundle with py2app.

## Local build (your Mac + a few trusted people)

This is the supported "gold-standard" build for personal use and sharing with a few trusted
people. It signs with your **Apple Development** identity (already in your keychain), so the app
runs on your Mac and TCC permission grants persist across rebuilds (stable bundle id
`health.baps.w1`). Recipients who aren't on your developer team open it once via **right-click ▸
Open**. (For warning-free distribution to anyone, you'd need a *Developer ID Application* cert +
notarization — see below.)

```bash
# 1. One-time: a FRAMEWORK Python build venv (uv's standalone CPython can't run py2app).
brew install python@3.12 poppler
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv-build
.venv-build/bin/pip install -e '.[mlx,macos,build]'

# 2. Build + sign + (optionally) make a .dmg. build.sh auto-detects your "Apple Development"
#    identity and signs with it; W1_BUILD_PYTHON points the build at the framework venv.
W1_BUILD_PYTHON="$PWD/.venv-build/bin/python" packaging/build.sh --dmg

# 3. Install: drag dist/W1.app to /Applications, launch it, and grant Microphone,
#    Accessibility, and Input Monitoring (System Settings ▸ Privacy & Security).
```

The Whisper model is **not** bundled — it downloads once on first run to `~/.cache/huggingface`.
Run the app from `/Applications`, not the iCloud-synced repo copy (iCloud xattrs can invalidate
the signature; `build.sh` already works around this for the build itself).

## Build

> **Build-environment requirement (important).** py2app needs a **framework** Python. The
> default `./install.sh` venv uses uv's *standalone* CPython, whose frozen stdlib modules lack
> `__file__`; py2app 0.28.8 aborts on it with `module 'zlib' has no attribute '__file__'` after
> producing only a partial bundle. Build from a framework Python instead:
>
> ```bash
> brew install python@3.12                      # framework build of 3.12
> /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv-build
> .venv-build/bin/pip install -e '.[mlx,macos,build]'
> .venv-build/bin/python packaging/setup_app.py py2app
> ```
>
> (python.org's 3.12 installer works too.) The recipe already excludes torch — an mlx-whisper
> *weight-conversion* dep never needed at MLX-inference runtime — to keep the module graph
> tractable. After building, **launch the bundle and test mic capture + the three TCC grants
> on-device** before sharing; py2app freezing can miss a lazily-imported module (add it to
> `OPTIONS["includes"]`).

```bash
packaging/build.sh            # -> dist/W1.app   (point .venv at a framework Python first)
packaging/build.sh --dmg      # -> dist/W1.app + dist/W1.dmg
```

The bundle is **menu-bar only** (`LSUIElement`) and does **not** embed the Whisper model — it
downloads once on first run to `~/.cache/huggingface`. This keeps the app small and avoids
redistributing model weights.

## Permissions

The app needs three TCC permissions, prompted on first use:

- **Microphone** — declared via `NSMicrophoneUsageDescription` (prompts automatically).
- **Accessibility** — to paste into the focused app.
- **Input Monitoring** — for the global Right-Option hotkey.

A stable bundle identifier (`health.baps.w1`) matters here: macOS keys granted permissions to
the bundle ID, so re-signed rebuilds keep their grants.

## Signing & notarization

| Audience | What to do |
|----------|------------|
| **Yourself / a few trusted people** | Ship the **unsigned** `.app`. First launch: right-click ▸ **Open** to bypass Gatekeeper once. |
| **Wider distribution** | Sign + notarize with an Apple **Developer ID** ($99/yr). No right-click dance, no "unidentified developer" warning. |

Signed build outline (Developer ID Application certificate in the keychain):

```bash
codesign --deep --force --options runtime \
  --entitlements packaging/w1.entitlements \
  --sign "Developer ID Application: YOUR NAME (TEAMID)" \
  dist/w1.app

xcrun notarytool submit dist/w1.dmg \
  --apple-id you@example.com --team-id TEAMID --password APP_SPECIFIC_PW --wait
xcrun stapler staple dist/w1.app
```

The entitlements in `packaging/w1.entitlements` allow the bundled Python/MLX runtime to JIT and
`dlopen` Metal libraries under the hardened runtime (required for notarization).

## Notes / gotchas

- `argv_emulation` is **off** — it breaks pynput's global key handling and AppKit's run loop.
- If you bundle the MLX backend, expect a large `.app`; the recipe keeps `mlx_whisper`/`mlx` out
  of `packages` by default since they download + Metal-link fine from the bundled site-packages.
- Verify the frozen bundle actually launches and records before sharing — py2app freezing can
  miss a lazily-imported module; add it to `OPTIONS["includes"]` in `packaging/setup_app.py`.
