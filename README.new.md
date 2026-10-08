<h1 align="center">w1</h1>

<p align="center"><em>A Mac dictation tool that types what you say, in the vocabulary you actually use.</em></p>

<p align="center"><a href="https://w1.osx.earth">w1.osx.earth</a></p>

One dictation key for clinic notes, investor updates, mandir work and everything else you write.

Hold a key, speak, and the text appears in whatever app is in front of you. Transcription runs
on your Mac: Whisper executes locally through Apple MLX, so the audio of what you said is turned
into text on the machine. On top of that, w1 runs a deterministic correction pass that snaps
specialist vocabulary onto its canonical spelling, so the words a general dictionary always gets
wrong come out right.

```
   speak  ──▶  Whisper (MLX, on-device)  ──▶  confidence gate  ──▶  canonical-spelling pass  ──▶  inserted into the focused app
```

## Status

This README separates what runs today from what is planned. Anything under
[Planned](#planned) is not implemented and is not in the source tree.

**Built and working:** push-to-talk and toggle dictation, on-device Whisper via MLX, insertion
into the focused app, a confidence gate, the glossary correction engine, the menu-bar app with a
floating widget and settings window, the CLI, and a py2app `.app` bundle.

**Version:** 1.1.0. macOS 13 or later, Apple Silicon.

## Privacy, stated precisely

Transcription is on-device. Whisper runs locally through Apple MLX and the audio does not need
to be sent anywhere to become text. The correction pass is deterministic string logic over local
JSON data, also on-device. The core pipeline performs no network calls, writes no transcripts to
disk, and logs no transcript content.

The one network access in normal use is the first-run model download from Hugging Face, roughly
1.5 GB, cached locally and never repeated.

Planned features that rewrite or summarise text are a second layer on top of the transcript, and
some of them will need a language model that may not run on your machine. Those are marked as
planned below and none of them ship today. When they do, each will state which layer it uses
before it runs. Plain transcription will always work on its own, offline, with nothing else in
the loop.

## Quickstart for testers

Download `w1.dmg` from the [Releases page](https://github.com/osx-earth/w1.osx.earth/releases),
drag `w1.app` to `/Applications`, and launch it. It is a menu-bar app, so it has no Dock icon;
look for the icon in the menu bar.

> **Gatekeeper today.** The current build is signed with an Apple Development identity and is
> not yet notarized, so the first launch needs **right-click ▸ Open** once. A Developer ID
> signed and notarized build that opens without that step is planned. Run it from
> `/Applications`, not from an iCloud-synced folder, because iCloud extended attributes can
> invalidate the signature.

Then grant three permissions in **System Settings ▸ Privacy & Security**:

| Permission | Why it is needed | Without it |
|---|---|---|
| **Microphone** | to hear you | prompted automatically on first use |
| **Accessibility** | to insert text into the focused app | text is transcribed but never pasted |
| **Input Monitoring** | for the global hotkey | the app runs but never hears the key |

Open the panes directly:

```bash
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent"
```

Hold **Right-Option** and speak. The hotkey and the activation style are rebindable in
**Settings**.

> Meeting capture, when it ships, will additionally need **Screen & System Audio Recording**,
> because capturing incoming system audio goes through a different macOS permission from the
> microphone. That permission is not requested by the current build.

## Quickstart for developers

Apple Silicon Mac with [uv](https://docs.astral.sh/uv/) installed:

```bash
git clone https://github.com/osx-earth/w1.osx.earth.git w1 && cd w1
./install.sh          # venv + deps + model download + permission links
./w1 app              # launch the menu-bar app + floating widget
```

`install.sh` creates a Python 3.12 virtualenv, installs the MLX and macOS extras, pre-downloads
`mlx-community/whisper-large-v3-turbo`, runs `./w1 doctor`, and prints the permission links. On
non-Apple-Silicon hardware it installs the `faster-whisper` fallback instead and skips the model
prefetch.

When running from source, the three permissions are granted to **your terminal app**, not to
`w1.app`. The packaged bundle carries its own identity and needs its own grants.

## How it works

- **Hotkey.** Hold Right-Option to talk (push-to-talk), or switch to double-tap toggle in
  Settings. Rebindable by press-to-capture. Text is inserted into whatever app is focused.
- **Transcription.** `mlx-community/whisper-large-v3-turbo` on Apple MLX, swappable in one
  config line. A `faster-whisper` backend and a `mock` backend exist for non-Apple-Silicon and
  for tests; backend selection is `auto` by default.
- **Bias prompt.** Before transcription, a budgeted list of glossary terms is fed to Whisper as
  its initial prompt, so specialist vocabulary is steered toward correct forms during decoding
  rather than only patched afterwards.
- **Confidence gate.** If Whisper's own per-segment confidences say the audio was probably not
  real speech, nothing is inserted and the widget flashes a reject cue instead of pasting noise.
  A separate check drops known Whisper hallucinations into silence, such as "Thanks for
  watching!".
- **Correction pass.** Deterministic, in a load-bearing order: light disfluency cleanup, then
  masking of protected terms, then a conservative fuzzy snap of out-of-vocabulary near-misses
  onto their canonical spelling, then unmasking. Every transformation is logged.
- **No word substitution.** Ordinary English is verbatim. "temple" stays "temple", "saint" stays
  "saint". The only change to wording is fixing the spelling of specialist terms you actually
  said, for example `vachanamrit` becomes `Vachanamrut`. Self-correction rewriting
  ("X, I mean Y") is implemented but off by default, because it changes your words.
- **Paste panel.** If text is produced with nothing editable focused, a floating panel holds it
  and `⌘⇧V` pastes it into whatever you click into next, so text is never dropped.
- **Settings.** Hotkey rebind, activation style, and launch at login, persisted to
  `~/Library/Application Support/W1/config.json`. A corrupt or version-skewed file falls back to
  defaults rather than refusing to launch.

## The glossary system

w1's correction engine takes a vocabulary and enforces canonical spellings on the transcript.
This is a dictionary layer with canonicalisation rules, not a short "custom words" box.

It ships with a large hand-built glossary of BAPS Gujarati terminology, which is the hard case
the engine was proven against: hundreds of terms, canonical spellings that no mainstream tool
gets right, and a strict orthographic rule set. Solving that properly is what produced the
general machinery, and the same machinery takes any vocabulary you give it.

What ships today:

| Data file | Entries | Role |
|---|---|---|
| `master_glossary.json` | 948 | canonical term list, the fuzzy snap targets and known-word set |
| `glossary.json` | 201 | core terms with aliases and definitions |
| `bias_seed.json` | 74 | terms fed to Whisper as decoding bias |
| `protected_terms.json` | 20 | never altered by any stage |
| `diacritics.json` | 12 | diacritic handling |

The master list is ingested from the BAPS Master Glossary PDF via
`scripts/ingest_glossary_pdf.py`. Source attribution is preserved in the data and should stay
that way. No word-substitution rules are derived from any of it.

**Orthographic rule.** Roman transliteration of Gujarati uses the long-a macron `ā` and strips
every other diacritic, so `ā` (U+0101) is the only non-ASCII letter that ever appears in output.
A deterministic Gujarati-script to Roman transliterator implementing that rule lives in
`src/w1_core/correction/transliterate.py`. It is written and tested as a module but is **not yet
wired into the dictation pipeline**.

Adding your own vocabulary currently means editing the JSON data files. A user-facing glossary
editor is planned.

## Planned

None of the following is implemented. It is listed so the scope is legible, not to describe the
current build.

- **Text modes.** Prompt Engineer (turns a spoken thought into a structured prompt), Polish
  (clearer, in your voice), Formal (lightly formalises, punctuates, capitalises), Street (keeps
  colloquial terms, no capitalisation). These reshape text rather than transcribe it, and they
  are the layer that may reach beyond the device.
- **Language menu.** English default, with Gujarati and Mixed options. English output will
  always be provided with transliterations. Gujarati accuracy work has not been done; treat it
  as unproven until training data lands.
- **Meeting mode.** Capture the microphone plus incoming system audio, with a live transcript
  and speaker labels. Needs the system audio recording permission noted above.
- **Join meeting.** Join Teams, Google Meet and Zoom meetings.
- **Post-meeting summarisation.** Route notes to one of three contexts (`jay@osx.earth`,
  `baps.solutions`, `sapio.health`), use that context to update existing notes, contextualise
  the summary, and generate tasks.
- **Insights dashboard.** Words per minute, total words dictated, fixes made, per-app usage
  breakdown, streaks and a contribution heatmap.
- **Glossary editor** in the app, and Developer ID signing plus notarization.

## CLI

| Command | What it does |
|---------|--------------|
| `./w1 app` | Launch the menu-bar app + floating widget |
| `./w1 dictate` | Record from the mic (Enter to stop, or `--seconds N`), correct, copy to clipboard |
| `./w1 transcribe FILE` | Transcribe an audio file and print raw vs corrected |
| `./w1 correct "text"` | Run text through the correction engine only, no audio |
| `./w1 doctor` | Check environment (deps, model, glossary counts, permission hints) |

`./w1` runs against the live source tree, so no reinstall is needed while developing.

## Tests

```bash
.venv/bin/python -m pytest tests/ -q                      # unit tests
.venv/bin/python -m pytest tests/ --cov=w1_core           # with coverage (fail_under = 80)
.venv/bin/lint-imports                                    # platform-boundary contract
```

Markers: `slow` for audio and WER tests needing the model on Apple Silicon, `macos` for tests
needing desktop APIs. Both are skipped in headless CI.

## Layout

| Path | What lives there |
|---|---|
| `src/w1_core` | portable engine: config, pipeline, correction, backends, audio types |
| `src/w1_data` | glossary and rule JSON, plus its loader |
| `src/w1_macos` | the macOS app: menu bar, widget, hotkey, mic, injection, settings |
| `scripts/` | glossary ingestion, rule sync, widget-frame generator |
| `packaging/` | py2app recipe, build script, entitlements |
| `docs/` | setup, packaging, supply chain, migration |

`w1_core` is contractually forbidden from importing anything macOS, desktop or ML-specific, and
that boundary is enforced by an import-linter contract in `pyproject.toml`. ML backends are lazy
optional imports inside `w1_core/backends`.

## Building the app

```bash
packaging/build.sh          # dist/w1.app
packaging/build.sh --dmg    # also dist/w1.dmg
```

py2app needs a **framework** Python; uv's standalone CPython cannot run it. Point
`W1_BUILD_PYTHON` at a framework-Python venv. The Whisper model is not bundled and downloads on
first run. See `docs/PACKAGING.md` for the full signing and notarization path.

Codesigning uses a stable bundle identifier so macOS TCC grants attach to a stable code identity
and survive rebuilds. Changing that identifier resets every existing user's permission grants;
see `docs/MIGRATION-osx-earth.md` before touching it.

## Name

w1, after the postcode. Built in London, for the way one person actually writes.

## Licence

MIT.
