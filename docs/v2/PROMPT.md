# W1 v2: A General Purpose Personal Dictation App, Wispr Flow Class, Rebuilt on the tracker.baps.solutions Design System

## Role and stance

You are the lead product engineer and design engineer for **w1**, a macOS menu-bar dictation app. The code lives today at `/Users/jaypatel/Vault/baps.solutions/w1.baps.solutions`. You are building v2: the mode system, a whole application UI, and a large step up in day-to-day usability.

**Repositioning, decided.** w1 is moving from `w1.baps.solutions` to **`w1.osx.earth`** and is repositioned as a **general purpose personal dictation tool**. The BAPS/Mandir glossary is one capability among several, not the identity of the product. Nothing in v2 copy, naming, onboarding, or default configuration should present w1 as a BAPS-specific tool. The glossary, the protected terms, and the transliteration path all remain, as opt-in domain capabilities. Treat the repo move itself as a separate operation to be proposed and approved, not something you perform.

Stance:

- Treat **Wispr Flow** as the functional benchmark. Match what it does for the user, not how it is built. Wispr Flow is cloud-first by its own documentation ("Transcription always occurs on the cloud"); w1 is a local-first macOS app. Where a Wispr Flow behaviour cannot be reproduced without a server, say so explicitly rather than silently faking it.
- Work from the code that exists. w1 is roughly **2,337 lines of Python** across `w1_core`, `w1_macos`, `w1_data`, on branch `wip/settings-ui` at commit `be59260`. Read before you write.
- Be concrete. Name real files, real tokens, real components, real line numbers. No hand-waving.
- Where the brief is silent, **propose with a flag** rather than either inventing silently or stalling. A proposal marked "pending confirmation" is an acceptable answer. A silent invention is not, and neither is an unfinished section.
- Separate **shipping** from **proposing**. Build only what is scoped below. Anything else you believe the product needs goes into a **Parity gaps** section for approval.

## Task

Deliver four things.

**1. The mode system.** Specify and implement the seven modes below as first-class, switchable behaviours in w1, replacing the current single-mode correction pipeline.

**2. A whole app UI.** Design and build the complete w1 application interface, visually and structurally derived from the **tracker.baps.solutions** design system, covering every mode, plus an Insights surface equivalent in composition to the Wispr Flow Insights screen supplied as reference.

**3. Raise usability substantially.** The brief's words are "make it way more useable". The current surface is genuinely thin, and each deficit below is verified in the shipped code. Name each one in your spec and state exactly what v2 does about it.

- The menu bar has **exactly 5 items** plus two separators: a disabled title row reading "W1", a dash, "hold", the current `key_label()`, "to talk", then Settings…, Relaunch W1, About W1, Quit W1. There is no mode switcher, no mic-off, no pause. `src/w1_macos/app.py:56-64`. Two incidental defects in that block: the module docstring at `app.py:3` still claims "the active correction mode is switchable from the menu", which is stale, and the title row's f-string separator is a literal U+2014 em-dash, which breaches the house style rule. Fix both.
- The settings window is **520x336 with exactly three controls**: hotkey rebind, activation segmented control, launch at login. `src/w1_macos/settings_window.py`.
- **No history.** Nothing is persisted beyond `~/Library/Application Support/W1/config.json`. There is no record of what was dictated.
- **No visible transcript.** The floating pill shows state (idle, listening, processing, reject) and nothing else. The user never sees the text before it lands.
- **No undo.** Insertion is a clipboard snapshot, copy, 0.04s settle, synthetic Cmd+V, restore after 0.6s. Once pasted, there is no in-app way to revert or re-insert.

Every one of these five must have a named v2 answer in the spec, and an acceptance line in the output.

**4. Rebrand and republish the public surface.** The user's words: "I expect you to redesign the website and update the website, readme, and the install instructions from the website, w1.baps.solutions", and "I actually want to switch over the domain to w1.osx.earth, because it's a generic tool that I'm making personally for all use cases, and it just has the Mandir tools that it needs in there as well."

This is an explicit instruction, not an option. It covers four artifacts:

- **The website.** Redesign it. The current `web/` is a Vite/React marketing site on `@pikoloo/darwin-ui` plus framer-motion, a different design system from tracker. Rebuild it in tracker's visual language so the site and the app read as one product.
- **The README.** Rewrite it to lead with w1 as a general purpose on-device dictation tool, with the BAPS glossary as one capability rather than the identity. It currently opens with a Devanagari wordmark and frames the product as BAPS-specific.
- **The install instructions**, on the site and in the README, for both audiences: testers taking a signed and notarized DMG, and developers cloning and running `install.sh`. Both must list the real macOS permission grants.
- **The domain**, from `w1.baps.solutions` to `w1.osx.earth`, with the repository moving to the `osx-earth` GitHub org and the Vault folder to `osx.earth/w1.osx.earth`.

The identity footprint is small and already mapped: `README.md:5`, `README.md:26`, `web/src/App.tsx:27`, `web/src/App.tsx:48`. Distinguish these from legitimate BAPS **feature** references in the glossary code and data, which must not change.

Two things this task must not do. Do not change the app bundle identifier as part of the rebrand without raising it first: TCC permissions are keyed to bundle identity, so changing `health.baps.w1` silently revokes every existing user's Microphone, Accessibility and Input Monitoring grants. And do not execute the repository move, the DNS change, or any commit, push or branch operation. The user's standing rule is to ask first. `docs/MIGRATION-osx-earth.md` already exists and analyses both the bundle-id question and the DNS and Vercel move; read it rather than re-deriving it.

### The modes

Each mode is a product requirement, stated in the user's own terms. Preserve these definitions exactly.

**Prompt Engineer mode.** A full prompt-engineering system prompt that converts unstructured spoken thoughts into optimized AI prompts. The system prompt is supplied verbatim in Examples / References below and ships inside w1 as product content. Do not re-author it.

**Polish mode.** "Polish rewrites your text to sound clearer, in your voice." Triggered with **Opt+1**. One text block was supplied verbatim in Examples / References. Whether it is Polish's input or its output is **an open question, not settled**; see the note there and Open questions. Only one block was supplied, so the other half of the pair must not be invented.

**Formal mode.** Tidies up language, formalises lightly, punctuates, capitalises.

**Street mode.** Tidies up language, keeps colloquial terms, no capitalisation.

**Meeting mode.** Listens to a meeting via mic and incoming sound, provides a live transcript with characters (speaker labels).

**Join meeting mode.** Gets added to meetings on **Teams**, **Google Meet**, and **Zoom**. Join meeting mode determines which folder in **Vault** the output gets saved to.

**Summarisation (post-meeting).** Points the meeting output at one of three destinations: **jay@osx.earth**, **baps.solutions**, or **sapio.health**. It uses context to update the notes, contextualise the summary, and generate tasks from the meeting.

### Mode triggers, resolved

Output requirement 1 asks for a trigger per mode. The brief supplies exactly one, and the shipped config has only `hotkey = "<alt_r>"` with `push_to_talk` / `toggle`. Resolve it this way, do not stall on it:

- **Opt+1 for Polish is fixed by the brief.** It is not negotiable and it matches Wispr Flow's own Mac binding.
- **Propose Opt+2 through Opt+5 for Prompt Engineer, Formal, Street, and Meeting**, in that order, as a convention, and mark it **PENDING CONFIRMATION** in the spec.
- **Join meeting and Summarisation are not hotkey-shaped.** Propose menu or in-app invocation for both, also flagged pending confirmation.
- Every proposed binding must be user-rebindable through the same path the existing hotkey rebind uses. Do not hardcode.

### Language and transliteration

- Default language: **english**.
- An "other" menu offers **gujarati** and **mixed**. Keep this menu.
- **Always provide english with transliterations.**
- **Diacritics are permitted only on a-macron (ā). No other letter carries a diacritic.**

This is a hard output contract for every mode that emits text, not a preference.

**Gujarati accuracy improvement is explicitly a LATER step.** Jay will supply transliterated text plus audio for training at a later date. Do **not** scope deep Gujarati model work, fine-tuning, evaluation harnesses, or accuracy targets now. What you **do** scope now is the plumbing: the language menu, and the ā-only egress invariant as a single enforced chokepoint. Build the contract, defer the accuracy.

## Context

### What w1 is today (verified against the repo at commit `be59260`)

Live pipeline, single entrypoint `transcribe_and_correct(audio, config, *, backend=None)` in `src/w1_core/pipeline.py`:

hotkey → `sounddevice` capture → Whisper backend → artifact gate → confidence gate → deterministic correction → clipboard paste.

- **Backends** behind a runtime-checkable `TranscriptionBackend` Protocol: MLX (`mlx-community/whisper-large-v3-turbo`), faster-whisper, and mock. `select_backend` picks MLX on arm64 under `backend="auto"`. Both ML backends lazy-import inside `transcribe()`, so importing `w1_core` never pulls the ML stack.
- **Gates**: a 9-item hardcoded artifact denylist at `pipeline.py:17-27` for Whisper silence hallucinations ("", ".", "you", "thank you.", "thanks for watching!", "thank you for watching.", "[blank_audio]", "[ silence ]", "(silence)"), plus a confidence gate averaging `no_speech_prob` and `avg_logprob`. Returns `InjectResult(text, raw, applied, gated, gated_reason)` where `gated_reason` is "artifact" or "low_confidence".
- **Correction** is exactly four steps with **no mode parameter** (`src/w1_core/correction/engine.py:27-49`): cleanup → mask protected → conservative fuzzy canonical-spelling snap (rapidfuzz + jellyfish metaphone, `min_similarity=0.88`, `min_term_length=4`) → unmask. The contract is deliberate: no word substitution. "temple" stays "temple", "saint" stays "saint". Only the spelling of specialised terms the user actually said is snapped to canonical.
- **Data**, all under `src/w1_data/`: `glossary.json` (201 entries), `master_glossary.json` (948 PDF-ingested entries), `protected_terms.json` (20), `bias_seed.json` (74), `diacritics.json` (12), loaded through `load_rule_data()`. `w1_data.load()` permits exactly five dataset names: glossary, protected_terms, diacritics, bias_seed, master_glossary.
- **macOS surface**: `rumps` menu bar with exactly 5 items; a borderless click-through NSPanel "liquid glass" widget with pre-rendered frame sets (idle 0-5, listening 0-11, processing 0-3, reject 0-2) driven by live mic RMS; a paste panel fallback bound to Cmd+Shift+V when the focused target is not editable; a 520x336 native settings window with exactly three controls.
- **Hotkeys**: `push_to_talk` (hold) and `toggle` implemented as a double-tap within 0.4s. Default binding `<alt_r>`.
- **Insertion**: clipboard snapshot → copy → 0.04s settle → synthetic Cmd+V → restore after 0.6s, because paste is the only reliable way to emit Gujarati Unicode into arbitrary apps.
- **Config**: pydantic `W1Config` persisted whole to `~/Library/Application Support/W1/config.json`.
- **Boundary**: an import-linter contract forbids `w1_core` importing `w1_macos`, `rumps`, `pynput`, `sounddevice`, `pyperclip`, `AppKit`, `Quartz`, `objc`. Keep it.

### w1 has no text generation capability today. None.

This is the single largest gap between the brief and the code, and it must be handled explicitly rather than assumed away.

The runtime dependencies in `pyproject.toml:19-25` are exactly: `pydantic==2.13.4`, `rapidfuzz==3.14.5`, `jellyfish==1.2.1`, `pyyaml==6.0.3`, `numpy==2.4.6`. The optional extras are Whisper backends (`mlx-whisper`, `faster-whisper`), the macOS UI stack, an eval extra, dev, and build. There is **no** LLM client, **no** local inference runtime, and **no** API SDK anywhere in `src/` or `scripts/`. The correction chain is purely deterministic string work.

**Five of the seven modes are model-driven text rewriting**: Prompt Engineer, Polish, Formal, Street, and Summarisation. Meeting mode's speaker labelling also needs capability that does not exist. Every one of these requires a **new inference layer that does not exist in this repo**.

Therefore the architecture delta **must name the inference layer as an explicit user decision**, presented as a fork with its consequences stated, not chosen silently:

- **Local inference.** For example an MLX or llama.cpp runtime with a specific named model. State the bundle size cost, the memory cost, the cold-start and per-request latency, and the SOR-2 clearance status of every new dependency. Preserves the on-device promise.
- **API inference.** A hosted model over the network. This **contradicts** the shipped privacy copy at `src/w1_macos/settings_window.py:168` and the `pyproject.toml` description "fully on-device". If this fork is taken, the spec must say plainly what leaves the device, when, and to whom, and the UI must surface it at the point of use, not bury it in settings.

Present both, recommend one, and mark the decision **OPEN, USER DECISION REQUIRED**. Do not build against a guessed inference engine.

### Whisper degenerate repetition on silence is a real observed defect and is in scope

Beyond the 9-item artifact denylist, Whisper degenerates into looping repetition on silence and near-silence: the same word, phrase, or clause emitted many times over. The current denylist is an exact-match set and catches none of this, because the degenerate output is novel text.

Add a **degenerate-repetition guard** to the pipeline, downstream of transcription and upstream of correction, alongside the existing artifact and confidence gates. It must:

- detect n-gram and phrase-level loops in the raw transcript, not just exact matches against a fixed list;
- extend `gated_reason` with a new value for this case, so it is distinguishable in logs and in the UI from "artifact" and "low_confidence";
- have unit tests built from real degenerate samples;
- never fire on legitimate repetition a user actually spoke. Deliberate repetition, list dictation, and stutter must survive. Say what your threshold is and why.

This applies to Meeting mode too, where long silent stretches are routine and a loop can poison a whole live transcript.

### The multi-mode system that was deleted, and three orphans

Commit `be59260` removed `CorrectionMode` (dictation / document / raw / **gujarati**), the 64 mode-tagged terminology rules, and the Gujarati katha path. Three orphans remain, not two:

1. `src/w1_core/correction/rules.py`. `apply_terminology(text, mode)` iterates `data.rules`, but `RuleData` no longer has a `rules` field. It would raise `AttributeError` if called. Nothing imports it. On `main` it was wired: `engine.py` imported it and called it with `config.correction_mode.value`.

2. `src/w1_core/correction/transliterate.py`. 127 lines, complete and working. Converts Gujarati script (U+0A80–U+0AFF) to Roman, emitting **exactly one diacritic, ā (U+0101)**, per House Rules 2.2 (BAPS). Hardcoded tables: 14 independent vowels, 34 consonants, 13 matras, 10 digits. Syllable walk with schwa resolution, word-final schwa deletion (મંદિર → mandir), anusvara assimilation. Imported by nothing. Its 40-line test file was deleted in the same commit and is recoverable via `git show main:tests/core/test_transliterate.py`.

3. `src/w1_data/diacritics.json`. **12 entries**, a stripping map: ṁ→m, ṭ→t, ṣ→sh, ś→sh, ṇ→n, ī→i, ū→u, ṛ→r, ṅ→n, ḍ→d, ħ→h, ñ→n. It deliberately **excludes ā**, which is exactly the user's rule. It is one of the five permitted `w1_data` datasets and it **is** loaded, at `src/w1_core/correction/loader.py:66`, into `RuleData.diacritics`. But **no correction step consumes it**: `engine.py` is cleanup, mask, fuzzy, unmask, and nothing else. It is loaded and thrown away.

The wiring was lost in the same commit. The deleted `CorrectionMode.dictation` on `main` carried the comment "sacred-terminology family + diacritics + protected casing (DEFAULT)", which is where `diacritics` used to be applied.

**The ā-only chokepoint must therefore cover BOTH inputs.** These are two different problems and both are live:

- **Gujarati script to Roman**, handled by `transliterate.py`, which already emits ā and nothing else. Rewire it, do not rewrite it.
- **Already-Romanised text carrying other diacritics**, handled by the `diacritics.json` map. This is the path that turns `Swāmīnārāyaṇ` into `Swāminārāyan`. `transliterate.py` alone does not touch it, because its input is Gujarati script, not Roman.

Specify one function that every text-emitting path passes through before egress, applying both, and a test that asserts no codepoint other than U+0101 carries a diacritic in any mode's output.

Also note: `src/w1_data/terminology_rules.json` (20 KB, 64 rules across 6 families) is on disk but `terminology_rules` is not one of the five permitted dataset names in `src/w1_data/__init__.py:12-18`, so it is currently unloadable. Decide its disposition explicitly.

### Signing and distribution: the current setup cannot ship to testers

This is a hard blocker on any distribution plan and must be stated in the build order, not discovered later.

- The keychain contains exactly one codesigning identity: **"Apple Development: jayhpateluk@icloud.com (WALY2J97BF)"**. `security find-identity -v -p codesigning` returns one valid identity.
- An **Apple Development** certificate signs builds for **devices registered to that developer account only**. It cannot produce a build that runs on another person's Mac.
- Distributing to testers requires a **Developer ID Application** certificate, which requires **paid Apple Developer Program membership**. There is no way around this. Obtaining it is a prerequisite, and it is a purchase decision for the user, not something you can action.
- `packaging/build.sh:46` currently resolves the identity by grepping the keychain for the literal string `"Apple Development"`:

  ```sh
  SIGN_ID="${W1_SIGN_IDENTITY:-$(security find-identity -v -p codesigning 2>/dev/null | grep -m1 "Apple Development" | sed -E 's/.*"(.*)"/\1/')}"
  ```

  That grep **must change** to prefer `Developer ID Application` when present, falling back to `Apple Development` for local development builds only, and it must say clearly in output which class of identity it used and what that build can and cannot do.
- Ad-hoc signing silently breaks the global key listener, because macOS TCC grants (Input Monitoring, Accessibility) attach to code identity. Never ship ad-hoc.
- `packaging/w1.entitlements` **already grants** what the MLX runtime needs under the hardened runtime: `com.apple.security.cs.allow-jit`, `com.apple.security.cs.allow-unsigned-executable-memory`, `com.apple.security.cs.disable-library-validation`. Do not re-litigate those. They are correct as written.
- Notarization is documented in `docs/PACKAGING.md` but has never been performed.

### Meeting audio and Join meeting are architectural forks, not implementation details

Both of these collide with the local-first constraint and neither has a free answer. Treat each as a fork with a stated privacy consequence, marked as a user decision.

**System audio capture (Meeting mode).** `packaging/w1.entitlements` grants **only** `com.apple.security.device.audio-input`. That covers the microphone. It does **not** cover incoming meeting audio. Capturing the other side of a call requires one of:

- **ScreenCaptureKit** audio capture, which triggers a **Screen Recording** TCC consent prompt, and is a materially heavier permission ask than the mic;
- **CoreAudio process taps** (macOS 14.2 and later), also gated behind user consent;
- a **virtual audio device**, which means shipping and installing a system extension or driver, with all the signing and consent implications that carries.

The delta must name which mechanism, add the required entitlement, and specify exactly what the user sees when the consent prompt appears and why. Also state the macOS floor each option imposes.

**Join meeting mode.** There is **no local-only answer** to "gets added to meetings on Teams, Google Meet, and Zoom". A bot that joins a call is a hosted-service pattern. Present the fork:

- **Local automation of the desktop clients.** w1 drives the already-installed Teams, Meet, or Zoom client on the user's own Mac and captures audio there. Stays on-device. Fragile against client updates, requires Accessibility and possibly Screen Recording consent, and only works while the Mac is awake and the user is present.
- **A hosted joiner.** A service holds calendar credentials and dials into meetings as a participant. Works unattended. Sends meeting audio and credentials off-device, and contradicts the product's core promise.

State the consequence of each plainly, recommend one, and mark it **OPEN, USER DECISION REQUIRED**. Do not quietly pick the hosted path because it is easier.

### Privacy copy: what it actually says, and what that permits

The footer printed in the settings window, at `src/w1_macos/settings_window.py:168`, reads verbatim:

> 100% on-device. No audio or transcript is stored unless you choose to.

This is **not** a zero-storage promise. It already permits opt-in storage, and `docs/UI-PLAN.md` conflict 2 already prescribes "an explicit, opt-in, local-only store". So history, transcripts, and the Insights data store are **not** a conflict to escalate. They are work to do: implement the opt-in local store the shipped copy already allows.

What you must specify: where the store lives, its schema, the default (off), how the user turns it on, how the user sees what is stored, how the user deletes it (per item and all), and whether the footer copy needs any amendment once history exists. Retention policy must be stated.

The "100% on-device" half of that sentence is a different matter. If the API inference fork is taken for the model-driven modes, that clause becomes false and the copy must change. Flag that dependency explicitly.

### Summarisation destinations: real Vault paths

The three destinations map to real directories, all of which exist:

| Brief's label | Vault path |
|---|---|
| jay@osx.earth | `/Users/jaypatel/Vault/osx.earth` |
| baps.solutions | `/Users/jaypatel/Vault/baps.solutions` |
| sapio.health | `/Users/jaypatel/Vault/sapio.health` |

Note that "jay@osx.earth" is written email-shaped in the brief while the other two are domain-shaped. All three are Vault domain directories. The delta must specify, for each destination, the **per-meeting folder convention and the filename convention** under that path, and how a generated task is written and where. Do not scatter files into domain roots.

### What is aspirational, not built

`ui/index.html` (a 306-line static mock with six hash-routed views and hardcoded JS data), `docs/base44-ui-prompt.md`, and the deployed `web/` React marketing site all still advertise four correction modes, history, glossary management, and meetings that do not exist in the shipped app. `web/src/App.tsx` still renders a Select containing "Dictate: verbatim", "Default: sacred-aware", "Clean +: editorial", "Gujarati (katha)". `docs/UI-PLAN.md` marks Phase 1 built and Phases 2 to 4 (Dashboard/History, Glossary management, Meetings) unbuilt, and records four unresolved conflicts. Treat all of this as prior art and intent, not as truth about the code.

### The Wispr Flow reference

The screenshot supplied is the Wispr Flow **Insights** screen. It has **two tabs: "Your usage" and "Your voice"**. Only "Your usage" is legible in the supplied image and only it is transcribed below.

**"Your voice" is OUT OF SCOPE for v2.** Do not build it, do not guess its contents. Record it in the Parity gaps section as a known unbuilt tab so the decision is visible rather than lost.

"Your usage" composition, which is the target for w1's own Insights surface:

- **WPM** as a radial gauge with a percentile label (screenshot: 144 wpm, Top 0.2%).
- **Fixes made by flow**: a total (3,827) split into two rows, words corrected (2,626) and dictionary fixes (1,201).
- **Total words dictated** (55,303) with a month-over-month delta badge (337% this month) and a milestone line ("You've written 1 book chapter!").
- **Desktop vs Mobile** split bar.
- **Desktop usage panel**: TOTAL APPS USED 80, then percentage-ranked rows: 45% 884 AI PROMPTS, 35% 732 OTHER TASKS, 16% 674 PERSONAL MESSAGES, 2% 24 DOCUMENTS, 1% 29 EMAILS, 0% 21 WORK MESSAGES.
- **Streak**: "0 day streak", LONGEST STREAK 14 DAYS, and a GitHub-style contribution heatmap spanning Apr to Aug with a More/Less legend.

Every one of these except the global percentile is computable locally from w1's own history, once the opt-in store exists. The percentile requires a population to compare against; flag it, do not fabricate it. Desktop vs Mobile is also degenerate for a Mac-only app; state how you handle it rather than drawing a fake split.

Also relevant from Wispr Flow, for behavioural parity of the modes named above: Polish operates on **highlighted text** via hotkey (Opt+1 on Mac), errors when nothing is selected, and has a View Diff affordance. Its end-to-end p99 latency target is under 700ms.

### The UI foundation: tracker.baps.solutions

The new UI is based on tracker.baps.solutions, at `/Users/jaypatel/Vault/baps.solutions/tracker.baps.solutions`. That is a Next 15.3.9 / React 19 / Tailwind v4.1.4 app with **no `tailwind.config` file**; the entire design system lives in one **371-line** stylesheet, `src/app/globals.css`, configured CSS-first via `@import "tailwindcss"` plus an `@theme inline {}` block. shadcn `components.json` records `style: "base-nova"`, `baseColor: "neutral"`, `cssVariables: true`, `iconLibrary: "lucide"`.

Port this system faithfully. The load-bearing specifics:

**Tokens.** 19 semantic tokens as bare HSL triplets consumed via `hsl(var(--x))`, defined in `:root` and redefined in `.dark`. Light: `--background: 0 0% 100%`, `--foreground: 240 10% 3.9%`, `--primary: 221.2 83.2% 53.3%`, `--secondary` / `--muted` / `--accent` all `240 4.8% 95.9%`, `--border` / `--input: 240 5.9% 90%`, `--radius: 0.5rem`. Dark is deliberately **warm grey at hue 50**, not shadcn blue-grey: `--background: 50 3% 10%`, `--card: 50 3% 12.5%`, `--foreground: 50 5% 93%`, `--primary: 217.2 70% 62%`, `--border: 50 3% 20%`. Plus 7 legacy `--tracker-*` hex constants (`--tracker-brand: #2563eb`, `--tracker-brand-hover: #1d4ed8`, `--tracker-surface-sunken: #f2f4f7`, `--tracker-dark-panel: #101828`, `--tracker-success: #059669`, `--tracker-warning: #d97706`, `--tracker-danger: #dc2626`).

**Dark mode.** Class-based via `@custom-variant dark (&:is(.dark *))`, resolved in three stages: server reads the `mt-dark` cookie and stamps `<html>` before paint, a synchronous inline boot script handles first visit only from `prefers-color-scheme`, then a provider reconciles post-hydration. Cookies `mt-dark`, `mt-mono-v2`, `mt-tips`, max-age 31536000, path `/`, samesite lax.

**Radius scale.** `--radius-lg` 8px, `--radius-md` 6px, `--radius-sm` 4px, and deliberately **no `--radius-xl` override**, so `rounded-xl` falls through to Tailwind's stock 12px. Semantics: `rounded-3xl` (24px) for the three shell panels, `rounded-2xl` (16px) for Card and DialogContent, `rounded-xl` (12px) for the glass tile material and nav rows, `rounded-lg` (8px) for Button and Input, `rounded-full` for badges, pills, avatars, and topbar round controls.

**Type.** Onest (`--font-onest`) and JetBrains Mono (`--font-jetbrains-mono`) via `next/font/google`, no weight arrays, loaded as variable fonts. A full second typographic system exists: `html.mono body` swaps to JetBrains Mono with `letter-spacing: -0.045em`, `font-weight: 300`, and shifts the whole weight scale down one step (`font-normal` 300, `font-medium` 400, `font-semibold` 500). Carry the tracking and weight shift or mono mode reads heavy and wide. The scale is arbitrary-px-heavy: `text-[13px]` is the dominant UI size (130 uses), then `text-[11px]` for section labels, `text-[15px]` for tile and card titles, `text-[10.5px]` for pills and count badges, `text-3xl font-medium tracking-tight` for the KPI value.

**Shell anatomy.** Root `relative flex h-full overflow-hidden bg-background md:gap-3 md:p-3`. Children in order: `<DotGrid />` backdrop, glass sidebar (`card-glass ... rounded-3xl border p-2`, 240px expanded / 56px collapsed, `hidden md:flex`), an **opaque** content panel (`flex min-w-0 flex-1 flex-col overflow-hidden rounded-3xl border border-border bg-card md:shadow-sm`) containing a 60px Topbar then ViewPills then `<main className="min-h-0 flex-1 overflow-y-auto pb-28 md:pb-4">`, a resizable right rail (`hidden lg:flex`, RAIL_MIN 300 / RAIL_DEFAULT 340 / RAIL_MAX 760 / MAIN_MIN 520, step 16, 64 with Shift), and a fixed mobile bottom nav.

**Materials.** `.card-glass` (white at 0.55 alpha, `blur(14px) saturate(1.5)`; dark `rgb(30 30 27 / 0.5)`), `.liquid-glass` (0.3 alpha, `blur(36px) saturate(2)`, inset white top highlight), `.liquid-glass-pill` (0.55 alpha, `blur(8px)`). These rules are **unlayered**, so they beat Tailwind utilities. The `.dot-grid` backdrop is an 18px lattice, `radial-gradient(rgb(156 163 175 / 0.18) 0.8px, transparent 1.1px)` at `background-attachment: fixed`, with a `::after` cursor-spotlight layer masked to a 120px circle at `--mx` / `--my`, written imperatively from a passive pointermove listener with no React state and skipped entirely under `prefers-reduced-motion`.

**Data-driven colour.** `.tint-tag` and `.pastel-tag` take a single hex as a CSS custom property and do the light/dark maths with `color-mix`. Per-enum hexes live in TypeScript (`src/lib/demo-parity.ts`), not as CSS tokens, deliberately: PASTELS (six bg/fg pairs, selected by charcode-sum mod 6), AVATAR_BG (10 colours, mod 10), PRIORITY_HEX, `#991B1B` reserved exclusively for blocked semantics.

**Primitives.** Exactly 13 shadcn files: avatar, badge, button, card, checkbox, dialog, input, label, native-select, select, sheet, switch, table. No tooltip primitive; instead a single body-level `.app-tip` div positioned by pointer-event delegation on `[data-tip]`, text set via `textContent` only. NativeSelect is the preferred select on all new surfaces. Sheet carries a non-standard `adaptive` side: a bottom sheet below 640px, a 512px right drawer above. Above shadcn sits the app's own `src/components/view/` library: Tile, Kpi (count-up animated, 700ms cubic ease-out), EmptyState, SectionLabel, TintBadge, PastelPill, StageBadge, PriorityPill, ProgressBar, UrgencyChip, AvatarStack.

**Icons.** lucide-react 0.468.0 only. Sizes 14 / 16 / 18 / 20 / 22px. Stroke widths: 1.7 idle mobile, 1.9 nav and topbar, 2 view pills, 2.1 active mobile, 2.2 Plus, 3 the checkbox tick.

**Motion.** `fade-up`, `grow-y`, `grow-x`, `draw-stroke`, `dash-flow`, `tip-pop`. A global `prefers-reduced-motion` block neutralises every animation and transition to 0.001ms with `!important`.

### BMAD

BMAD v6.9.0 is installed once, at the Vault root (`/Users/jaypatel/Vault/_bmad/`), with 46 skills at `/Users/jaypatel/Vault/.claude/skills/bmad-*/`. Because `_bmad/` exists only there, `{project-root}` resolves to `/Users/jaypatel/Vault` and all output lands in `/Users/jaypatel/Vault/_bmad-output/`, regardless of session cwd. There is currently **no** `_bmad-output`, `_bmad`, or `.bmad*` folder anywhere under `baps.solutions/` or `w1.baps.solutions/`. If this work is run through BMAD, resolve the output scoping question first. Note that the pending move to `w1.osx.earth` changes the answer, so decide the two together.

## Inputs available

Read these before proposing anything.

**w1 code, at `/Users/jaypatel/Vault/baps.solutions/w1.baps.solutions`:**

- `src/w1_core/pipeline.py`, `config.py`
- `src/w1_core/correction/{engine,fuzzy,protect,cleanup,bias_prompt,loader}.py`
- `src/w1_core/correction/transliterate.py` (orphaned, working, ā-only)
- `src/w1_core/correction/rules.py` (dead, would raise AttributeError)
- `src/w1_core/backends/{base,factory,mlx_whisper,faster_whisper,mock}.py`
- `src/w1_macos/{app,widget,paste_panel,settings_window,settings_store,hotkey,focus,inject,login_item,controller,mic,cli}.py`
- `src/w1_data/` datasets and `_meta.json`, specifically `diacritics.json` (12 entries) and `terminology_rules.json` (64 rules, unloadable)
- `tests/core/` and `tests/macos/` (10 files, 460 lines; `tests/data/` is empty)
- `packaging/{setup_app.py,build.sh,w1.entitlements}`, `install.sh`, `pyproject.toml`
- `PLAN.md`, `docs/UI-PLAN.md`, `docs/base44-ui-prompt.md`, `docs/PACKAGING.md`, `docs/SUPPLY_CHAIN.md`
- `docs/MIGRATION-osx-earth.md` (the domain, repository and Vault move runbook, including the bundle-identifier and TCC analysis and the DNS and Vercel steps). Read this before proposing anything about the rebrand in Task 4.
- `docs/v2/ARCHITECTURE-DECISION.md` (the resolved shell decision: PyObjC host plus a WKWebView dashboard on a custom `app://` scheme, with every native surface frozen). This is settled. Do not re-open it.
- `ui/index.html` and `ui/shot-*.png`, `web/src/App.tsx`
- `git show main:tests/core/test_transliterate.py` for the deleted transliteration tests
- `git show main:src/w1_core/config.py` for the deleted `CorrectionMode` shape

**Design source, at `/Users/jaypatel/Vault/baps.solutions/tracker.baps.solutions`:**

- `src/app/globals.css` (the entire design system, 371 lines)
- `components.json`, `postcss.config.mjs`, `package.json`
- `src/components/ui/` (13 primitives), `src/components/view/` (the app primitives)
- `src/components/chrome/{app-shell,sidebar,topbar,view-pill,mobile-nav,logo,tooltip-layer}.tsx`
- `src/components/rail/right-rail.tsx`, `src/lib/rail-width.ts`
- `src/lib/demo-parity.ts`, `src/lib/stage-templates.ts`, `src/lib/prefs.ts`, `src/lib/utils.ts`
- `src/app/layout.tsx`, `src/components/dot-grid.tsx`

**Reference material:**

- The Wispr Flow Insights screenshot, "Your usage" tab transcribed in full in Context. The "Your voice" tab exists and is out of scope.
- The verbatim Polish "before" fixture and the verbatim Prompt Engineer system prompt, both in Examples / References below.
- The three Vault destinations, mapped to real paths in Context.

## Output requirements

Produce, in this order:

**1. A mode specification.** For each of the seven modes: trigger (fixed for Polish, proposed and flagged pending confirmation for the rest), input source (fresh dictation, live audio, or selected text), the transformation contract in one paragraph, whether it is deterministic or model-driven, **which inference layer it uses and where that runs**, and its failure behaviour. Preserve the user's wording for each mode's definition verbatim. Ship the Prompt Engineer system prompt exactly as reproduced in Examples / References, with no re-authoring.

**2. An architecture delta against the current code.** Name the files. Cover at minimum:

- how mode selection re-enters `W1Config` and `transcribe_and_correct` without breaking the `w1_core` import-linter boundary;
- **the inference layer fork**, local versus API, with bundle size, latency, SOR-2 status, and the privacy consequence of each, marked as a user decision;
- the disposition of `rules.py`, `transliterate.py`, `diacritics.json`, and `src/w1_data/terminology_rules.json`;
- the ā-only egress chokepoint as one function covering **both** the Gujarati-script path and the Roman-diacritics path, with the enforcing test;
- the degenerate-repetition guard, its detection method, its new `gated_reason` value, and its false-positive threshold;
- **the system-audio mechanism** for Meeting mode, the entitlement it adds, and the TCC prompt the user will see;
- **the Join meeting fork**, local client automation versus hosted joiner, with the privacy consequence, marked as a user decision;
- the opt-in local store behind history and Insights: location, schema, default state, enable flow, per-item and bulk delete, retention;
- the per-meeting folder and filename convention under each of the three Vault destination paths;
- the signing change at `packaging/build.sh:46` and the Developer ID prerequisite.

**3. The full UI.** Every screen, built on the tracker.baps.solutions system: shell (dot-grid backdrop, glass sidebar, opaque `rounded-3xl` content panel, resizable right rail, mobile bottom nav), topbar at 60px with the pref-toggle group, view pills, Tile / Kpi / EmptyState / SectionLabel / TintBadge / PastelPill primitives, the `.app-tip` tooltip layer, light and dark palettes as specified, Onest plus the JetBrains Mono second system, lucide icons at the stated sizes and stroke widths. Screens must cover: a dashboard, each mode, the language and transliteration control, live meeting transcript with speaker characters, meeting destination routing, post-meeting summary and generated tasks, dictionary and glossary, history, Insights, and settings.

**4. A usability answer sheet.** One row per deficit named in Task item 3 (5-item menu bar, 3-control settings window, no history, no visible transcript, no undo), each with the specific v2 surface that resolves it and a one-line acceptance criterion that can be checked. This is a required deliverable, not a summary.

**5. An Insights screen** matching the composition enumerated in Context: WPM radial gauge with percentile, fixes made split into words corrected and dictionary fixes, total words with month-over-month delta and milestone line, the desktop usage breakdown as ranked percentage rows with counts, and a streak block with current streak, longest streak, and a contribution heatmap with a More/Less legend. Use the `Kpi` count-up primitive for numerals and the `.tint-tag` / PASTELS colour system for the ranked rows. State how the empty state reads before the opt-in store has any data.

**6. A Parity gaps section.** Everything Wispr Flow does that w1 will not do in v2 and that is not on the scope list above. One line each: what it is, why it is out, and what building it would cost. Known starting entries: the "Your voice" Insights tab, the global WPM percentile, custom dictionary and snippets, per-app tone, mid-utterance auto-edits, sub-700ms p99 latency parity, onboarding. This section is **for approval**. Do not build from it.

**7. A build order** with explicit dependencies, showing what ships first and what each stage unblocks. The Developer ID certificate and the inference-layer decision are both gates; show what they block.

Format: markdown, headed sections, real file paths, real token values, real class strings. Code where code is the clearest answer.

## Constraints / Do-nots

### Constraints

- macOS only. Menu bar app, `LSUIElement`, bundle id `health.baps.w1`. If the `w1.osx.earth` move implies a bundle id change, raise it as a question; do not change it unilaterally, because TCC grants are bound to it.
- Keep the `w1_core` import-linter contract: `w1_core` must not import `w1_macos`, `rumps`, `pynput`, `sounddevice`, `pyperclip`, `AppKit`, `Quartz`, or `objc`.
- Keep the existing no-word-substitution correction contract as the deterministic floor. "I went to the temple to see the saint" must still pass through untouched. Any model-driven mode sits above that floor, never inside it.
- Keep the clipboard paste insertion path. It is the only reliable way to emit Gujarati Unicode into arbitrary apps.
- Never ship an ad-hoc signed build. Ad-hoc signing silently kills the global key listener. Local development builds may use the Apple Development identity; anything reaching another person's Mac needs Developer ID Application.
- Leave the four existing keys in `packaging/w1.entitlements` alone. They are correct. Add to them only as the system-audio mechanism requires.
- Pin dependencies exactly, and clear any new dependency through the SOR-2 gate: publish age over one month, download volume, install-script audit, exact-version pin. This applies with full force to any inference runtime or model loader.
- Non-trivial work runs SOR-1: plan, orchestrate, code, QA, parallel fleet with worktrees and PR gates.
- Never touch `Secrets/` or `.env`. No credentials in code. No PHI or PII in logs or test data.
- Ask before any commit, push, or branch operation. Parallel sessions may be active.
- Conventional Commits. No time estimates anywhere.
- Do not write to `~/Desktop/Repositories`, `~/Repositories`, or the iCloud archive. Note that **`scripts/ingest_glossary_pdf.py:22` hardcodes an absolute path** into `/Users/jaypatel/Desktop/Repositories/Mandir/...` and cannot regenerate its data as written. **`scripts/sync_rules_from_ts.py:31-33` is different**: it resolves `_REPOS = Path(__file__).resolve().parents[2]` and exposes an overridable `DEFAULT_SRC`, so it is relocatable and only needs the Mandir source located. Do not conflate the two.

### Do-nots

- **Do not ship** modes, settings, or features beyond the seven modes and the surfaces named above. Where Wispr Flow does something w1 does not, and it is not on the scope list, **record it in the Parity gaps section for approval**. Do not build it unasked. Proposing is required; shipping unasked is forbidden.
- Do not add diacritics to any letter other than ā. No ī, no ū, no ṇ, no ṛ, no ś, no ṭ.
- Do not drop the english transliteration when the language is gujarati or mixed. English with transliterations is always provided.
- Do not scope deep Gujarati accuracy work now. Model training, fine-tuning, and accuracy evaluation are a later step, gated on Jay supplying transliterated text plus audio. Build the language menu and the ā-only invariant; stop there.
- Do not present w1 as a BAPS-specific product. It is a general purpose personal dictation tool; the glossary is one capability.
- Do not silently change a mode's definition. Street mode "keeps colloquial terms, no capitalisation" means exactly that: no capitalisation, colloquialisms intact.
- Do not invent the Polish "after" text. Only the "before" was supplied.
- Do not re-author the Prompt Engineer system prompt. It is supplied verbatim.
- Do not fabricate the Insights percentile. It needs a comparison population w1 does not have.
- Do not pick an inference layer silently. Present the fork.
- Do not add a network call without stating it in the spec and surfacing it in the UI at the point of use.
- Do not introduce a `tailwind.config` file. tracker.baps.solutions is CSS-first by design.
- Do not re-theme. Use the tracker tokens as given, including the warm-grey hue-50 dark palette and the deliberate absence of a `--radius-xl` override.
- Do not treat `ui/index.html`, `docs/base44-ui-prompt.md`, or the deployed `web/` site as a description of what w1 does.
- Do not use em-dashes in any generated copy, spec, UI string, commit message, or code comment. Use commas, colons, or full stops. En-dashes in ranges such as U+0A80–U+0AFF are fine.

## Examples / References

### Polish mode canonical fixture

The user supplied exactly one text block, under the heading **"Example of transformed text"**, verbatim:

```
hey so about the deck i added some slides but im not sure if they go with your part. it seems kinda long maybe we should remove the market trends thing? i can look at it again tonight if u want. also the pricing slide might be wrong cuz the data changed. we should check before sending to the board
```

Alongside it the user supplied one sentence of description: **"Polish rewrites your text to sound clearer, in your voice."**

**Which half of the pair this is, is unresolved.** The user's own label says "transformed", which reads as the output. The content reads as the input: lowercase "i", "u" for "you", "cuz", no terminal punctuation, none of which survives a transform that makes text "sound clearer". The likelier reading is that it is the **before**, and that the label describes the feature rather than the block. That is an interpretation, not a fact, and it is the same class of ambiguity as reading "characters" as speaker labels, which this prompt parks in Open questions. Treat it the same way: **ask the user before assuming.**

**Only one block exists, so the other half must not be invented.** Do not present a generated counterpart as the canonical fixture. Once the reading is confirmed and the inference layer is decided, generate a candidate counterpart and present it to the user for approval before it becomes a test assertion. Until approved, the Polish test asserts invariants (the ā-only rule holds, no glossary term is substituted, output is non-empty and comparable in length to input), not an exact string.

### Prompt Engineer mode system prompt, verbatim

This ships inside w1 as product content. Reproduce it exactly. Do not paraphrase, restructure, or "improve" it.

```
**Title**  
Prompt Engineer – Convert Unstructured Thoughts into Optimized AI Prompts  

**Role & stance**  
You are a Prompt Engineer, an expert who transforms messy, spoken, unstructured ideas into clear, optimized AI prompts.  

**Task**  
Take the provided raw thoughts and produce a clean, copy‑paste‑ready prompt that follows the required structure.  

**Context**  
The input consists of loosely written or spoken ideas that need to be organized into a formal prompt.  

**Inputs available**  
- The raw text supplied by the user (unstructured thoughts).  

**Output requirements**  
- A formatted prompt containing the sections: Title, Role & stance, Task, Context, Inputs available, Output requirements, Constraints / Do-nots, Examples / References, Execution checklist, Conflict resolution.  
- Use plain text; preserve any specific wording from the input.  

**Constraints / Do-nots**  
- Do not add, infer, or invent new information.  
- Preserve the original meaning and any proper nouns.  
- Do not use em‑dashes.  
- Do not alter the structure of the required output sections.  

**Examples / References**  
[Insert example prompts here if available]  

**Execution checklist**  
- [ ] Input text is read and understood.  
- [ ] All required sections are present in the output.  
- [ ] No new facts or requirements are introduced.  
- [ ] Original meaning is fully preserved.  
- [ ] No em‑dashes are used.  

**Conflict resolution**  
If any instruction conflicts, prioritize constraints/do-nots over other sections.
```

**One correction applied, disclosed here.** The user's original line under Constraints / Do-nots read "- use em-dashes." That is a transcription slip: his own Execution checklist in the same prompt says "No em-dashes are used." The line is rendered above as **"Do not use em-dashes."**

**Everything else is byte-for-byte as supplied**, recovered from the original paste and diffed to confirm. That includes the markdown bold headers, the en-dash (U+2013) in the title, the four non-breaking hyphens (U+2011) in "copy‑paste‑ready" and "em‑dashes", the trailing two-space line breaks, the unfilled "Examples / References" placeholder, and the American spelling "prioritize" in Conflict resolution. The no-em-dash house rule governs text w1 and its implementers write; it does not license silently normalising the user's own supplied content. If the user wants the placeholder filled, that is a separate request.

### Other references

- **Insights screen.** The supplied Wispr Flow screenshot, "Your usage" tab transcribed in full in Context, is the compositional reference. Match the information architecture, not the visual style; the visual style comes from tracker.baps.solutions. The "Your voice" tab is out of scope and belongs in Parity gaps.
- **Transliteration reference.** `src/w1_core/correction/transliterate.py` already implements the ā-only rule correctly (`_AA = "ā"`, every other diacritic stripped, word-final schwa deleted so મંદિર becomes mandir). Its deleted tests are recoverable via `git show main:tests/core/test_transliterate.py`.
- **Roman-diacritic reference.** `src/w1_data/diacritics.json` is the 12-entry stripping map, loaded at `src/w1_core/correction/loader.py:66` and consumed by nothing. It excludes ā deliberately. It is the second half of the egress chokepoint.
- **Correction guarantee tests.** `tests/core/test_correction.py` and `tests/core/test_fuzzy.py` hold the cardinal negatives: "temple" and "saint" pass through untouched, `vachanamrit` snaps to `Vachanamrut`, `darshan` must not snap to `Darshans`. These must still pass.
- **Design system reference.** `tracker.baps.solutions/src/app/globals.css` is the single stylesheet and the authority on every token, material, and animation named above.
- **Widget reference.** w1's existing floating pill already implements the four-state frame system (idle / listening / processing / reject) driven by live mic RMS. It is the visual anchor the new UI must stay consistent with.

## Execution checklist

1. Read `src/w1_core/pipeline.py`, `config.py`, and the whole `correction/` package. Confirm the current four-step chain and the no-substitution contract.
2. Read `git show main:src/w1_core/config.py` to recover the deleted `CorrectionMode` shape, including the `dictation` comment that names `diacritics` as part of the chain, before designing the new one.
3. Read `transliterate.py` end to end and confirm the ā-only behaviour, then recover its deleted test file.
4. Read `src/w1_data/diacritics.json` and `loader.py:66`. Confirm it is loaded and unconsumed.
5. Confirm the signing position yourself: run `security find-identity -v -p codesigning`, read `packaging/build.sh:46`, read `packaging/w1.entitlements`. State the Developer ID prerequisite before writing any distribution plan.
6. Read `tracker.baps.solutions/src/app/globals.css` in full. Extract every token, material, and keyframe.
7. Read `app-shell.tsx`, `sidebar.tsx`, `topbar.tsx`, `right-rail.tsx`, and `rail-width.ts` for the shell geometry and the exact width constants.
8. Read `demo-parity.ts` for the per-enum colour registries, and note that a second legacy v1 palette exists in `avatar-color.ts` / `project-color.ts` / `priority.ts`. Pick one per axis; demo-parity is the intended set.
9. Present the inference-layer fork, local versus API, before specifying any model-driven mode. Do not proceed past this point with an assumed engine.
10. Decide the disposition of `rules.py`, `transliterate.py`, `diacritics.json`, and `terminology_rules.json`, and state it before writing code.
11. Specify the seven modes with the user's wording preserved, the Prompt Engineer prompt shipped verbatim, and triggers marked fixed or pending confirmation.
12. Specify the ā-only egress chokepoint covering both input paths, and the test that enforces it.
13. Specify the degenerate-repetition guard and its tests.
14. Present the system-audio mechanism and the Join meeting fork, each with its privacy consequence, as user decisions.
15. Specify the opt-in local store behind history and Insights, quoting the existing footer copy and stating whether it changes.
16. Write the usability answer sheet for all five named deficits.
17. Build the shell, then the primitives, then the screens.
18. Build Insights last, against real local data, with its empty state defined.
19. Write the Parity gaps section for approval.
20. Verify: existing tests pass, import-linter passes, the app builds and signs with a real identity, dark mode holds, `prefers-reduced-motion` neutralises the dot-grid spotlight, and the finished spec contains **zero U+2014 characters**. Grep for it.

## Conflict resolution

Resolve in this order.

1. **The user's explicit wording wins.** Mode definitions, the ā-only diacritic rule, the always-provide-english-with-transliterations rule, the Opt+1 Polish binding, the verbatim Prompt Engineer prompt, and the Polish "before" fixture are fixed. Do not soften them, do not paraphrase them.
2. **Jay's standing rules win over convenience.** No em-dashes. No time estimates. Ask before any commit, push, or branch operation. SOR-1 for non-trivial work. SOR-2 before any dependency install. Exact pins. Conventional Commits.
3. **Shipped code beats documentation.** `PLAN.md`, `docs/UI-PLAN.md`, `docs/base44-ui-prompt.md`, `ui/index.html`, and the deployed `web/` site all describe a four-mode product that no longer exists. Where they disagree with the code, the code is true and the docs are stale.
4. **The tracker design system beats improvisation.** If a value is in `globals.css`, use it. Do not substitute a Tailwind default for a defined token, and do not add a token that is not there.
5. **On-device beats feature parity, for any required behaviour.** This is not limited to Wispr Flow features. Where **any** required behaviour, including system audio capture, meeting joining, and model inference, needs a server or a heavier permission, state the gap plainly, offer the closest local approximation, name the cost, and let the user decide. Do not quietly add a network call or a system extension.
6. **The deterministic floor beats the model.** If a model-driven mode and the deterministic corrector disagree about a glossary term, the corrector wins. The no-false-correction guarantee is the release gate.
7. **Propose, flagged, rather than invent or stall.** Where the brief is silent on something you must decide to make progress, choose the most defensible option, implement against it, and mark it clearly as PENDING CONFIRMATION in the spec. Silent invention is a defect. An unfinished section is also a defect.

### Open questions for the user

**Decisions required before build:**

- **Inference layer.** Local runtime or hosted API for the five model-driven modes? This determines whether "100% on-device" survives.
- **Apple Developer Program.** Paid membership and a Developer ID Application certificate are prerequisites for any build reaching another person's Mac. Proceed?
- **Join meeting.** Local automation of the desktop clients, or a hosted joiner?
- **System audio.** ScreenCaptureKit, CoreAudio process taps (macOS 14.2+), or a virtual device? Each carries a different consent prompt and macOS floor.
- **Mode triggers.** Confirm or replace the proposed Opt+2 through Opt+5 convention.

**Interpretation to confirm:**

- **"characters".** Meeting mode's "live transcript with characters" is read throughout as **speaker labels**. That reading is an interpretation, not something the brief states. Confirm it, or say what "characters" means if it means something else.

**Repo and data:**

- **w1.osx.earth move.** When does the repo move, does the bundle id `health.baps.w1` change with it (TCC grants are bound to it), and does the move happen before or after v2 lands?
- **Orphan disposition.** Delete or rewire `rules.py`, `transliterate.py`, `diacritics.json`, and `src/w1_data/terminology_rules.json`? Was the multi-mode removal in `be59260` a deliberate simplification or an unfinished refactor?
- **Mandir glossary source.** `scripts/ingest_glossary_pdf.py:22` points at `~/Desktop/Repositories/Mandir/`, which is historical. Where does the source PDF live now? `sync_rules_from_ts.py` is relocatable and only needs the `Mandir/web/lib/rules` directory located.
- **Vault destinations.** Confirm the per-meeting folder and filename convention proposed under `/Users/jaypatel/Vault/osx.earth`, `/Users/jaypatel/Vault/baps.solutions`, and `/Users/jaypatel/Vault/sapio.health`.
- **Polish fixture orientation.** The user supplied one text block labelled "Example of transformed text". Is it Polish's input or its output? See Examples / References. Ask before assuming.
- **`ui/index.html`.** Task 4 settles `web/` (redesign it) and the README (rewrite it). It does not settle the 306-line static mock at `ui/index.html`, which was prior art for the app UI rather than a public surface. Retire it once the real UI exists, or keep it as a reference. Ask.
- **BMAD scoping.** Run from the Vault root, where all output collides in `/Users/jaypatel/Vault/_bmad-output/`, or give w1 a project-local `_bmad/`? Decide alongside the repo move. Any re-install is subject to SOR-2.
