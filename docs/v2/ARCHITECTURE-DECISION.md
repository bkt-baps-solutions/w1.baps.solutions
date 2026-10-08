# W1 Architecture Decision

## 1. THE DECISION

Keep the existing Python/PyObjC app as the host process and add a WKWebView window that renders a Vite-built React SPA carrying tracker's Tailwind 4 tokens and shadcn primitives, served over a custom `app://` scheme, with every native surface (menu bar, floating widget, hotkey, focus detection, paste injection, login item) left byte-for-byte unchanged. Do not adopt Tauri, do not rewrite the shell in Swift, and fix distribution (Developer ID, inside-out signing, notarization, Sparkle) as a separate workstream that is independent of the UI choice.

## 2. WHY

**All three judges ranked the same option first, and the margins were not close.** Shipping/release-engineering scored it 8 against 5 (Swift) and 3 (Tauri). Design-system fidelity scored it 9 against 5 (Tauri) and 3 (Swift). Execution risk scored it 9 against 4 (Swift) and 3 (Tauri). No lens produced a reason to prefer a rewrite. When the shipping judge, the design judge and the risk judge independently pick the same answer, the remaining argument is aesthetic, not technical.

**The design-system win is host-independent, which collapses the decision to cost.** The Tauri proposal said this outright: "this UI win is NOT Tauri-specific, it accrues identically to Electron or to a WKWebView hosted by a native Swift/PyObjC shell." I verified the underlying fact myself: all 13 files in `tracker.baps.solutions/src/components/ui/` contain zero `next/*` imports. Their entire import surface is `@/lib/utils`, `lucide-react`, `class-variance-authority`, `react` and Radix. So every webview host produces an identical design outcome, and the host must therefore be chosen purely on native-capability preservation and toolchain cost, where the incumbent wins by construction because it preserves everything and adds one dependency.

**The Swift proposal's central argument is factually wrong, and the design judge caught it.** It claims zero tracker React survives in any approach because tracker cannot be statically exported, and therefore "that fork is identical work whether the host is WKWebView or SwiftUI." That conflates two unrelated things. Nobody proposed exporting tracker's Next app. The reusable unit is 13 self-contained primitive files, and copying them into a Vite app is a file copy plus a font fix, versus 1,200 to 1,500 LOC of net-new untested SwiftUI by the proposal's own estimate. SwiftUI also permanently severs the shadcn registry, and W1's six screens need Tabs, Tooltip, Popover, Command, Progress, Toast and charts that tracker's 13 primitives do not contain.

**The WKWebView proposal's own flagship dealbreaker is false, which slightly damages its credibility but not its ranking.** It asserted, under a "verified" confidence label, that the shipped bundle probably cannot transcribe because MLX is absent. I checked: `/Applications/W1.app/Contents/Resources/lib/python3.12/mlx/lib/` contains `mlx.metallib` at 157,748,008 bytes, `libmlx.dylib` at 21,653,808 bytes and `libjaccl.dylib`, and `mlx_whisper` is present. py2app's modulegraph collected both despite their absence from `OPTIONS["packages"]`. This matters in the winner's favour: the hardest thing to re-derive, a working MLX/Metal payload, already works under the current pipeline, and both rewrites propose discarding that pipeline for an unvalidated one (PyInstaller onedir, or python-build-standalone plus `pip --target`).

**Where the judges disagreed, and how I broke it.** The design judge ranked Tauri second; the shipping and risk judges ranked Swift second. This does not change the winner, only the fallback. I resolve it toward Swift: the design judge placed Tauri second on a fidelity tie, but since fidelity is host-independent (above), second place must be decided on native capability and toolchain, where Tauri fails hard. Tauri's global-shortcut plugin structurally cannot express bare Right-Option push-to-talk, and `tauri-nspanel`, which carries the entire floating-widget requirement, returns 404 on crates.io, so it is a git-only single-maintainer dependency and a flat SOR-2 violation. Swift is a bad choice for now, Tauri is a bad choice permanently.

**Corrections to the record that everyone got wrong.** The Team ID is `JBXT67LFNK`, not `WALY2J97BF`. Every proposal and the distribution research treated the parenthesised value in the Apple Development certificate CN as the Team ID. `codesign -dvvv /Applications/W1.app` reports `Authority=Apple Development: jayhpateluk@icloud.com (WALY2J97BF)` and `TeamIdentifier=JBXT67LFNK`. The Team ID is the value that matters for notarization, TCC designated requirements and Sparkle signature matching. Separately, the nested Mach-O signing surface is 185 files in the shipped bundle, not 335, 336 or 700 to 1,000. And the bundle is 537 MB, not 400 to 450 MB.

## 3. WHAT IT LOOKS LIKE

### Process topology

One process. The `W1.app` Python process remains the host, exactly as today: `LSUIElement: True`, bundle ID `health.baps.w1`, rumps status item, PyObjC panels, MLX inference in-process. WKWebView renders in a separate WebContent XPC process managed by the system, so a GIL-blocked engine does not stutter the UI, but that is a WebKit implementation detail, not an architecture Jay owns.

### Where the React UI lives

New sibling directory `app-ui/`, not the existing `web/`. I confirmed `web/` is the Vercel marketing site on `@pikoloo/darwin-ui` plus framer-motion, a different design system entirely. Two proposals cited `web/` as a ready-made frontend harness. It is not one.

```
app-ui/
  index.html
  vite.config.ts            # @tailwindcss/vite, default Vite output, no base override
  package.json              # exact pins copied from tracker, not re-resolved
  public/fonts/             # self-hosted Onest + JetBrains Mono woff2
  src/
    tokens.css              # GENERATED from tracker globals.css, do not hand-edit
    lib/utils.ts            # cn() = clsx + tailwind-merge, copied verbatim
    components/ui/*.tsx     # 13 primitives copied verbatim from tracker
    screens/                # NET NEW: Dashboard, History, Glossary, Meetings, Insights, Settings
    bridge.ts               # typed wrapper over window.webkit.messageHandlers.w1
```

### How the React UI talks to the Python engine

Assets are served by a `WKURLSchemeHandler` on `app://`, reading from `resource_dir() / "web"`. `file://` is not an option: the research verified experimentally, four ways, that Vite's ES-module output does not execute under `loadFileURL:allowingReadAccessToURL:`, `fetch()` is blocked, and with Vite's default `crossorigin` attribute the CSS does not apply either. I did not re-run those probes, but the finding is specific, reproducible and consistent with WebKit's origin rules. Treat it as mandatory, not preferential. The custom scheme is also strictly better than a localhost HTTP server: no port allocation, no startup race, no open socket contradicting the on-device promise.

JS to Python goes through `WKScriptMessageHandler` on the `WKUserContentController`, so `window.webkit.messageHandlers.w1` is injected regardless of page origin and the bridge works identically against the Vite dev server. Python to JS goes through `evaluateJavaScript`. `src/w1_core/config.py` is already a pydantic `BaseModel`, so `model_dump_json()` and `model_validate()` give a typed, validated wire format for free. Validate every inbound payload through pydantic: JS numbers are doubles, so integers arrive as floats.

Dev loop: `W1_DEV_UI=1` loads `http://localhost:5173` for Vite HMR and React Fast Refresh against the live Python engine, otherwise `app://w1/index.html`. `wv.setInspectable_(True)` attaches the full Safari Web Inspector.

### Which surfaces stay native AppKit, and why

These are frozen. This is an architectural constraint, not a phase.

| File | Surface | Why it stays |
|---|---|---|
| `src/w1_macos/widget.py` | Floating pill | Borderless non-activating NSPanel at level 1000, `CanJoinAllSpaces \| Stationary`, `ignoresMouseEvents`, NSVisualEffectView. A webview cannot be non-activating, click-through and above fullscreen apps. A webview pill also costs 30 to 50 MB and real compositing for an 86x26 image view. |
| `src/w1_macos/app.py` | Menu bar | rumps NSStatusItem works. Nothing to gain. |
| `src/w1_macos/hotkey.py` | Right-Option push-to-talk | pynput sits on CGEventTap. Carbon `RegisterEventHotKey` cannot bind a bare modifier, and macOS 15+ rejects Option-only registrations. There is no better path in any language. |
| `src/w1_macos/focus.py` | AX focus detection | Its deliberately conservative fail-to-editable contract encodes field experience. |
| `src/w1_macos/inject.py` | Paste injection | Working, TCC-debugged. |
| `src/w1_macos/paste_panel.py` | Fallback panel | Same NSPanel pattern. |
| `src/w1_macos/login_item.py` | Launch at login | Works. |

Write this into `docs/UI-PLAN.md` as the resolution of Conflict 1: the webview is for the dashboard only, the widget and status item are native permanently.

### Tracker reuse: what is copied, what is generated, what is written from scratch

**Copied verbatim:** the 13 files in `src/components/ui/`, and `src/lib/utils.ts`.

**Generated, not copied:** the design tokens. Do not paste `globals.css` in once and let it rot. Add `packaging/sync_tokens.py` that parses tracker's `:root` and `.dark` blocks into `app-ui/src/tokens.css`, run it in CI, and fail the build if the generated file is dirty. This converts a one-time copy into a maintained, drift-detecting link. This is the single best idea in the entire research set and it came from the losing Swift proposal.

**Rewritten:** the two font variables. Tracker binds `--font-sans: var(--font-onest)` and `--font-mono: var(--font-jetbrains-mono)`, injected by `next/font/google` in `layout.tsx`. Self-host both as `@font-face` from `app-ui/public/fonts/`. There is precedent in this repo: `ui/index.html` already self-hosts Ubuntu Sans Mono. Hitting fonts.googleapis.com would fail under `app://` and would contradict the privacy promise.

**Net new:** all six screens. Nothing above the primitives ports, because tracker's board, gantt, calendar, table-view, inbox, hub and rail are bound to Next App Router, Prisma and next-auth. But the screens are not starting from zero either: `ui/index.html` is a 306-line working prototype of all six screens with sidebar, topbar, mode chip, cards, mic control and privacy footer. The job is re-expressing that anatomy in tracker's primitives, which is materially cheaper than starting blank. Note that the prototype's visual language (saffron gradient, Ubuntu Sans Mono) is not tracker's (neutral base, Onest), so adopting tracker is a deliberate in-app rebrand. Confirm that is intended.

### Files that change in `/Users/jaypatel/Vault/baps.solutions/w1.baps.solutions`

New:
- `src/w1_macos/dashboard.py` NSWindow plus WKWebView plus `WKURLSchemeHandler`
- `src/w1_macos/bridge.py` `WKScriptMessageHandler`, pydantic validation of inbound payloads
- `src/w1_core/insights.py` SQLite store, counts only, path injected by the macOS layer so the import-linter contract stays green
- `packaging/sign_bundle.sh` inside-out signing over all 185 nested Mach-O files
- `packaging/sync_tokens.py` token generator with CI dirty check
- `app-ui/` the whole Vite tree

Modified:
- `packaging/setup_app.py` add `str(ROOT / "app-ui" / "dist")` to `OPTIONS["resources"]` (currently `[str(ROOT / "assets")]`, which already proves nested-tree bundling works), add the WebKit PyObjC framework to `includes`, and investigate the EXCLUDES leak below
- `packaging/build.sh` add `npm ci && npm run build` before py2app, replace `codesign --force --deep` with the inside-out loop, add `--timestamp`, add notarize and staple. Keep the existing `ditto --norsrc --noextattr --noacl` iCloud xattr workaround, it is load-bearing because the repo lives under `~/Vault`
- `packaging/w1.entitlements` drop `com.apple.security.cs.allow-jit`, keep `allow-unsigned-executable-memory`, test dropping `disable-library-validation`
- `pyproject.toml` add `pyobjc-framework-webkit==12.2.1` pinned exactly. SOR-2: published 2026-06-19, about 8 weeks old, passes the gate, same maintainer and version family as the 5 pyobjc packages already in `docs/SUPPLY_CHAIN.md`, so zero new vendors. Version 12.2.2 shipped 2026-08-11 and fails the gate, so the pin must be explicit or uv will pull it transitively
- `src/w1_macos/app.py` one menu item to open the dashboard
- `src/w1_macos/settings_window.py` retained until the React Settings screen is proven, then deleted
- `docs/UI-PLAN.md` record Conflict 1 as resolved
- `README.md` privacy wording, see section 6

Unchanged: everything in `src/w1_core/` except the new insights module, and every native file listed in the table above.

### The bundle-size finding nobody reported

`packaging/setup_app.py` lists `numba` and `llvmlite` in `EXCLUDES`, yet the shipped bundle contains both: llvmlite at 97 MB and numba at 17 MB. Also present: scipy 79 MB, sympy 41 MB, numpy 24 MB, mlx 178 MB. The torch exclusion did take effect. The numba and llvmlite exclusion did not, and nobody noticed because the only verification ever performed was that the app launches. sympy at 41 MB is a genuine torch orphan and is safely prunable. numba and scipy are direct declared dependencies of `mlx-whisper==0.4.3`, so removing them requires proving the inference path (word-timestamp DTW uses numba) never touches them. This is worth more real user-visible improvement than any shell choice, and it improves notarization upload time and Sparkle delta economics on every release.

## 4. GRAFTS

**From the Swift proposal:**

1. **Split the entitlements by binary.** Sign `allow-unsigned-executable-memory` and `disable-library-validation` onto the Python/MLX payload only, and give the outer app the minimal set. Today `w1.entitlements` grants all three to the entire bundle. This costs nothing extra once a per-binary signing loop exists, and it is the best security idea in the set.
2. **Core Audio Process Taps, not ScreenCaptureKit, for meeting capture.** ScreenCaptureKit binds audio to an `SCStream` that needs a display, window or app target, so audio-only capture still triggers the full Screen Recording prompt. Process taps (macOS 14.4+) use `NSAudioCaptureUsageDescription`, a separate and much narrower TCC category. Asking a clinician for Screen Recording permission to transcribe a meeting is a conversation to avoid. Corollary trap: taps key their TCC record off a stable signing identity, so unsigned dev builds never show the prompt and it will read as a code bug.
3. **Sparkle from the first tester build, not from release six.** With delta updates configured from day one. The Python payload is nearly static between releases while the UI churns, so deltas should be small. Without them testers re-download hundreds of megabytes per patch and stop updating. Pin `2.9.4` (published 2026-07-03, 41 days, passes SOR-2), not `2.9.5` (2026-08-02, 11 days, fails). Remember Sparkle's XPC services and `Autoupdate.app` join the inside-out signing loop.
4. **The CI-enforced token generator**, already folded into section 3.
5. **Build the signing and notarization pipeline before any new features.** That is where the unknown-unknowns live, and discovering a notarization blocker after building Insights is the expensive ordering.
6. **The clipboard-free injection path.** `focus.py` already calls `AXUIElementIsAttributeSettable(_, kAXValueAttribute)` and discards the result. Where the element reports settable, `AXUIElementSetAttributeValue` avoids clobbering the user's clipboard for 600 ms. This is a real user-visible improvement and it is one line away in the existing PyObjC, no Swift required.

**From the Tauri proposal:**

7. **Measure the signing surface on the bundle, not the venv.** Tauri was the only proposal that counted correctly (185). Adopt that discipline for `sign_bundle.sh`.
8. **Prune the orphaned payload.** Tauri flagged roughly 234 MB of llvmlite, scipy, sympy and numba. My check refines this: sympy at 41 MB is safely prunable, the rest are declared mlx-whisper dependencies, and numba plus llvmlite at 114 MB are currently shipping despite being excluded, which is a bug worth chasing.
9. **Never let a framework's updater signature substitute for Apple signing.** Sparkle's EdDSA key is additive to Developer ID and notarization, not a replacement.
10. **The host-independence framing** belongs verbatim in the decision record, because it is the argument that decided this.
11. **No self-extracting single-file freeze, ever.** A 157 MB metallib extracting to `/var/folders` on every cold launch is disqualifying on startup time and on placing code outside the sealed bundle.

## 5. DISTRIBUTION PLAN

### The blocker

`security find-identity -v -p codesigning` returns exactly one identity, `Apple Development: jayhpateluk@icloud.com (WALY2J97BF)`, and `spctl -a -vvv -t exec /Applications/W1.app` returns `rejected`. An Apple Development certificate cannot be notarized. On macOS 15 and later Apple removed the right-click then Open bypass, so on Jay's own macOS 26.0.1 a tester's only path is System Settings, Privacy and Security, Open Anyway, with an admin authentication. Stacking that on top of Microphone, Accessibility and Input Monitoring prompts will cost testers.

### Three defects in the current pipeline, all verified

1. `packaging/build.sh` has no `--timestamp`. A secure timestamp is a hard notarization requirement. Every submission fails without it.
2. `--deep` signed exactly one of the 185 nested Mach-O files (`Contents/Frameworks/libpython3.12.dylib`). The other 184 remain adhoc linker-signed with `TeamIdentifier=not set`, because `--deep` does not re-sign code that already carries a signature and linker-signed counts as one. The first submission will bounce on 184 files at once. Operationally this is fine, one `find -exec` loop fixes all of them, but it means `codesign --verify --deep --strict` is a false green here: it reports valid on disk. Only `spctl -a -t exec` exposes the real state. Do not use `codesign --verify` as the pre-notarization gate.
3. The entitlements set both `allow-jit` and `allow-unsigned-executable-memory`. Apple DTS is explicit that each is a superset of its predecessor and only one should be set. W1 needs `allow-unsigned-executable-memory`: sounddevice drives PortAudio callbacks through CFFI `ffi.callback()`, which allocates libffi write-plus-execute closures that `allow-jit`'s MAP_JIT pattern does not cover. MLX does not add a JIT requirement, its `mlx.metallib` is a precompiled Metal library loaded as data, which I confirmed on disk.

### The correct sequence

1. Build with py2app from a framework Python, per `docs/PACKAGING.md`.
2. `ditto --norsrc --noextattr --noacl` out of the iCloud-synced tree.
3. Sign every nested Mach-O inside-out: `codesign --force --timestamp --options runtime --sign "Developer ID Application: ... (JBXT67LFNK)"` per file, no entitlements, no `--identifier`.
4. Sign the outer `.app` last with `--entitlements packaging/w1.entitlements --identifier health.baps.w1 --timestamp --options runtime`.
5. Verify with `spctl -a -vvv -t exec`, not `codesign --verify`.
6. `ditto -c -k --sequesterRsrc --keepParent dist/W1.app W1.zip`. Plain `zip` mangles framework symlinks.
7. `xcrun notarytool submit W1.zip -p w1-notary --wait`. On failure, `xcrun notarytool log <id> -p w1-notary` names the specific files.
8. `xcrun stapler staple dist/W1.app`.
9. Build the DMG from the stapled app, then notarize and staple the DMG too. The ticket stapled to a DMG does not travel with the extracted app.
10. Verify with the network disconnected.

### Model weights

Not bundled, deliberately. `whisper-large-v3-turbo` is about 1.5 GB and downloads on first run to `~/.cache/huggingface`. Bundling pushes releases past 2 GB, makes every notarization submission a 2 GB upload against a 75-per-day cap, and makes Sparkle re-push unchanged weights on every release. What must be built instead, and the webview makes this easy: a first-run screen with real progress, resumable download, checksum verification, a clear one-time 1.5 GB warning before it starts, a graceful failure path, and a documented way for Jay to hand a tester a pre-seeded cache directory.

### Updates

Sparkle 2.9.4 driven from PyObjC via `objc.loadBundle('Sparkle', ...)` then `SPUStandardUpdaterController` (not the deprecated `SUUpdater`). `SUFeedURL` over HTTPS and `SUPublicEDKey` in the py2app `PLIST` dict. EdDSA keypair from `bin/generate_keys`, private key in the login Keychain and backed up offline. Delta updates configured from the first release. The app is not sandboxed, which avoids Sparkle's XPC sandboxing complexity entirely, and sandboxing is impossible anyway given Accessibility and Input Monitoring.

Channel: a notarized DMG behind an HTTPS link. Optionally a private Homebrew tap (`brew tap bkt-baps-solutions/tap`) for technical testers as a supplement, never a replacement. Official homebrew-cask is out (75 stars, 30 forks, 30 watchers minimum, or 225/90/90 self-submitted). TestFlight is structurally unavailable: it requires a sandboxed Mac App Store build, and the sandbox is incompatible with Accessibility paste injection and Input Monitoring.

### What a tester actually experiences

Download the DMG, drag W1 to Applications, double-click. With a stapled notarization ticket there is no Gatekeeper warning. Then, in order: a Microphone prompt (automatic, driven by `NSMicrophoneUsageDescription`), an Accessibility request (no entitlement or plist key exists, it is a manual System Settings toggle, so call `AXIsProcessTrustedWithOptions` with `kAXTrustedCheckOptionPrompt` to surface the nudge), an Input Monitoring request (again manual, use `IOHIDRequestAccess(kIOHIDRequestTypeListenEvent)` so it prompts rather than silently receiving no events), and then the 1.5 GB model download. Later, if meeting capture ships, a separate system-audio prompt via `NSAudioCaptureUsageDescription`, which must be typed into Info.plist manually because Xcode does not offer it in the dropdown.

### Prerequisites Jay needs

1. Confirm whether team `JBXT67LFNK` is on a paid Apple Developer Program membership or a free personal team. **Unverified, and unverifiable from the shell.** A free personal team cannot issue a Developer ID certificate at all. Check developer.apple.com/account.
2. Apple Developer Program enrollment if not active. Individual enrollment needs no D-U-N-S and is fastest, but puts Jay's personal legal name in Gatekeeper dialogs. Organization enrollment puts BAPS Solutions there and requires a D-U-N-S.
3. Account Holder role on the team, which Apple requires to generate a Developer ID certificate.
4. A Developer ID Application certificate, valid five years. Optionally a Developer ID Installer certificate too.
5. An offline `.p12` backup of the Developer ID private key, stored outside the Mac and outside iCloud. Apple limits Developer ID certificates per account.
6. An App Store Connect API key for notarytool: the `.p8` (downloadable exactly once), Key ID and Issuer ID, then `xcrun notarytool store-credentials "w1-notary" --key ... --key-id ... --issuer ... --validate`. Currently `xcrun notarytool history` fails with "Must provide credentials". Prefer the API key over an app-specific password: scoped, revocable, and the only sane option if notarization moves to CI.
7. A Sparkle EdDSA keypair, with the private key backed up out of the login Keychain. Losing it means no tester can ever receive another update.
8. HTTPS hosting for the DMG and `appcast.xml` at a URL that will never change, because `SUFeedURL` is baked into every shipped build.
9. A decision to freeze the bundle identifier `health.baps.w1` permanently.

## 6. THE PRIVACY LINE

The README currently says: "Nothing, no audio, no text, ever leaves your computer. No cloud, no account, no subscription."

That is already not literally true, because first run downloads 1.5 GB from Hugging Face. That part is benign and easily worded. The planned features are not.

**The options:**

**A. Local model only.** Ship a small local LLM for Polish, Formal and Street. Keeps the promise intact word for word. Costs multiple GB of additional download on top of 1.5 GB of Whisper weights, and a small local model will not do Prompt Engineer credibly. Meeting summarisation with task generation is borderline. A bot joining Teams, Meet or Zoom is impossible under this option: there is no macOS API for it, the standard implementation is a server-side headless participant, and that means other people's meeting audio transits Jay's infrastructure.

**B. Optional cloud with explicit per-mode consent.** Every LLM mode is off by default. Turning one on shows exactly what will be sent and to which provider before anything is sent. A global "Strict local" toggle hard-fails outbound requests rather than degrading silently. A visible indicator (menu bar icon change) whenever text leaves the Mac.

**C. Revised promise only.** Soften the README to "privacy-first" and handle the rest in a privacy policy. Cheapest, and the worst option: it dilutes the differentiator against Wispr Flow without buying any capability.

**Recommendation: B, with A as the default configuration.** Dictation stays 100 percent local and that claim stays absolute, because it is the claim that actually sells the product. The LLM modes become explicitly opt-in surfaces with per-mode disclosure. Strict local is the switch that makes the promise enforceable rather than declarative. This matters more than usual here: Jay is a clinician, early testers will likely be clinicians dictating patient material, and an unannounced network path in that context is an information-governance incident, not a marketing quibble. A blanket "100 percent on-device" claim while a shipped feature calls out is also straightforwardly misleading advertising.

**Exact README change.** Replace the current blockquote with:

> **Is my voice private?** Dictation runs entirely on your Mac. W1 transcribes with OpenAI's Whisper via Apple MLX, and your audio and your transcripts never leave your computer. No account, no subscription.
>
> **What does leave your Mac, and when.** On first launch W1 downloads the speech model (about 1.5 GB) from Hugging Face. No audio, no text and no personal data are sent. In the default configuration that is the only network access W1 ever makes.
>
> **Optional AI modes** (Prompt Engineer, Polish, meeting summaries) are off by default. If you turn one on, W1 tells you exactly what will be sent and to which provider before it sends anything, and the menu bar icon changes whenever text leaves your Mac. Turn on **Strict local** in Settings to block every outbound request, including the model download once the model is cached.

Keep the existing `NSMicrophoneUsageDescription` in `packaging/setup_app.py`, which asserts audio never leaves the computer. That statement is about audio specifically and remains true under option B.

Two things the meeting bot needs before it is scoped, neither of which was researched: the terms of service position of Teams, Google Meet and Zoom on automated participants, and two-party consent recording law in the jurisdictions Jay's testers are in. **Unverified.**

## 7. MIGRATION PATH

Each step leaves the app working and shippable.

**0. Rebuild the environment.** `.venv/lib/python3.12/site-packages` currently contains nine empty `.dist-info` directories and nothing else. iCloud's fileprovider has evicted the virtualenv. `.venv_old_w4k` is intact with 165 packages and `/Applications/W1.app` is a complete 537 MB reference bundle, so there is a working reference to measure against. Consider whether a tree carrying a 500 MB Python payload belongs under an iCloud-synced path at all. Fully reversible.

**1. Fix the payload leak and prove transcription in the frozen bundle.** Investigate why numba and llvmlite ship despite being in `EXCLUDES`. Drop sympy. Then run a real transcription from inside the built bundle, not just a launch check. Fully reversible.

**2. Rewrite signing, still with the Apple Development identity.** Add `--timestamp`, replace `--deep` with the inside-out loop over all 185 nested Mach-O files, apply entitlements and `--identifier` only to the outer app, drop `allow-jit`, test dropping `disable-library-validation`. Verify with `spctl`, not `codesign --verify`. Fully reversible: the identity has not changed, so no TCC state moves.

**3. Obtain the Developer ID certificate, re-sign, notarize, staple, and install on a second Mac.** **This is the first step that is hard to reverse.** TCC grants are keyed to the app's designated requirement, which encodes the signing identity, so switching from Apple Development to Developer ID resets every Accessibility, Input Monitoring and Microphone grant. Worse, stale entries often remain visible and toggled on in System Settings while being non-functional, so the fix is to select each entry, press minus, and re-add. Do this before a single tester build ships. Migrating testers later means walking each of them through a manual TCC repair.

**4. Scaffold `app-ui/`.** Vite, Tailwind 4, `sync_tokens.py`, the 13 primitives, self-hosted fonts, one throwaway screen. No Python changes yet. Fully reversible: delete the directory.

**5. Add `dashboard.py` and `bridge.py` behind a new menu item.** Native Settings stays. Prove `app://` in the frozen bundle, prove `NSApp.activateIgnoringOtherApps_(True)` gives the window keyboard focus under `LSUIElement` (verified in the research probes as necessary: without it `isKeyWindow` stays False and typing goes nowhere), prove the pyobjc WebKit framework freezes correctly under py2app. Fully reversible: delete two files and one menu item.

**6. Port the six screens, Settings last.** Delete `settings_window.py` only after its React replacement is proven in a frozen, signed bundle. Reversible via git.

**7. Add Sparkle 2.9.4 with deltas and publish the first appcast.** **Partially irreversible:** `SUFeedURL` and `SUPublicEDKey` are baked into every shipped build, so once testers have a build you cannot move the feed or rotate the key without a manual reinstall. Pick the URL as though it is permanent.

**8. Insights, opt-in and local.** SQLite at `~/Library/Application Support/health.baps.w1/insights.db`, explicitly not under `~/Documents` or `~/Desktop`, both of which are iCloud-synced on Jay's setup and would push usage data off-device by accident. Store counts, never transcript text. Derive streaks at query time from stored UTC timestamps plus timezone offsets, never store a running counter. Give the user a visible row count, per-app delete and a delete-all that actually VACUUMs.

**9. LLM modes with per-mode consent and the Strict local toggle.** Ship the README change with this step, not after it.

**10. Meeting capture via Core Audio process taps.** Its own epic. Decide the bot question before designing its UI, because it changes what the UI must disclose.

## 8. WHAT I AM STILL UNSURE ABOUT

**Apple Developer Program tier for team `JBXT67LFNK`.** Unverified. No shell command exposes it, and a free personal team cannot issue a Developer ID certificate at all, which would put an unknown lead time in front of the entire distribution plan. Resolved by logging into developer.apple.com/account.

**Why numba and llvmlite ship despite being in `EXCLUDES`.** I verified they ship (17 MB and 97 MB). The mechanism is unknown. Resolved by a verbose py2app build log, checking whether a py2app recipe or a dependency re-adds them, and by checking whether mlx-whisper's inference path (word-timestamp DTW) actually needs numba.

**Whether `disable-library-validation` can be dropped.** Unverified. Once every nested binary carries Jay's own Developer ID and Team ID, library validation should be satisfied, but this fails only at runtime in a signed build. Resolved by signing without it and running a real transcription.

**Whether removing `allow-jit` is safe in W1's actual runtime.** The CFFI and libffi reasoning is sound and the Apple DTS guidance is explicit, but it was not tested against this app. Resolved by the same signed-build transcription smoke test, with the sounddevice callback active.

**Tailwind version skew.** Tracker pins `tailwindcss 4.1.4` with `@tailwindcss/postcss`; `w1/web` uses 4.2.4 with `@tailwindcss/vite`. A 371-line token file built on `@theme inline` and `@custom-variant` across a minor bump should be verified, not assumed, as should the claim that the Vite and PostCSS plugins behave identically. Resolved by building `app-ui` at 4.1.4 first, confirming visual parity, then bumping deliberately.

**Whether `pyobjc-framework-WebKit` freezes correctly under py2app.** Unverified. It is not installed anywhere in the tree today (the project venv is destroyed and it is absent from both `.venv_old_w4k` and the shipped bundle), so it is a genuinely new dependency with a new packaging step. Resolved at migration step 5 by opening the dashboard from the frozen bundle.

**Whether quantized Whisper is viable.** 4-bit and 8-bit mlx-community variants would cut the 1.5 GB download substantially, but Gujarati and code-switched input is exactly where quantization damage shows first. Resolved by running the existing accuracy harness in `scripts/` rather than assuming.

**Whether tracker's visual language is the right in-app look.** The existing `ui/index.html` prototype is saffron gradient and Ubuntu Sans Mono; tracker is neutral base with Onest. Adopting tracker is a deliberate rebrand of the app's interior, not a neutral retheme. This is a product call, not a technical one.

**The Insights schema.** My recommendation, not a verified design. The privacy-critical part (counts only, never text, and the Application Support location rather than iCloud-synced Documents) is solid; the specific columns and the WPM definitions are a starting point.

**Crash reporting.** Developer ID apps get nothing automatically, since App Store Connect crash reports exist only for App Store and TestFlight builds. Crash logs land in the tester's `~/Library/Logs/DiagnosticReports/`. A local handler plus an explicit opt-in "Send diagnostics" flow that shows the full payload before transmitting is the privacy-consistent design, but it is unbuilt and unspecified. Bolting on Sentry with defaults would quietly ship stack traces and file paths containing the user's name off-device.