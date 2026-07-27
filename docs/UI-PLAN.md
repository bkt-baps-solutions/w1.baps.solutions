# W1 Companion UI — phased build plan

BMAD-routed plan for the W1/वाणी companion UI described in `base44-ui-prompt.md`. Routed
Analysis (Mary) → Solutioning (Winston) → Planning (John). Phase 1 is **built**; later phases
are scoped here and gated on the decisions in §Conflicts.

## Current state (Mary)
- Menu-bar app (Python/rumps + PyObjC); floating widget + paste panel are native and working.
- **Config now persists** (Phase 1): `~/Library/Application Support/W1/config.json`.
- **No transcript/stats/meeting storage** — deliberate: "nothing stored unless you choose to."
- **Glossary is read-only**, generated from Mandir (`w1_data/glossary.json`); Mandir is the
  single source of truth — local hand-edits are forbidden by design.
- **No meeting capture / no speaker diarization** anywhere in the codebase.

## Conflicts to resolve before Phase 2+ (Winston)
1. **Native vs web** for the dashboard. Phase 1 settled Settings as native (no server, no extra
   permissions). Dashboard/History/Glossary/Meetings are web-shaped — decide before building.
2. **Persistence vs zero-storage.** Dashboard stats and History require stored transcripts,
   which contradicts the privacy default. Needs an explicit, opt-in, local-only store.
3. **Glossary writes vs Mandir source-of-truth.** "Add/correct a term" needs a *local override
   layer* that never edits the generated JSON and is reconciled upstream into Mandir.
4. **Meetings + diarization** is a new subsystem (capture + speaker labelling), its own epic.

## Phases (John) — each shippable, no loose ends
### Phase 1 — Native Settings + config persistence ✅ BUILT
- `settings_store.py` — atomic JSON load/save of `W1Config`; corrupt/missing → defaults.
- `hotkey.py` — `serialize_key`/`parse_key`/`key_label`, live `set_binding`, `capture_once`
  (press-to-capture).
- `login_item.py` — launch-at-login via a per-user LaunchAgent that opens `/Applications/W1.app`.
- `settings_window.py` — native PyObjC panel: hotkey + press-to-capture **Rebind**,
  Hold-to-talk / Double-tap activation, correction mode, launch at login, privacy footer.
- `app.py` — loads persisted config on launch, `Settings…` menu item, single mode-change path
  (menu ↔ window stay in sync), saves on every change.
- Tests: `tests/macos/{test_hotkey,test_settings_store,test_login_item}.py`.

### Phase 2 — Dashboard + History (gated on decisions 1 & 2)
- Opt-in local store (default off) for transcripts + daily stats.
- Dashboard: engine/model/permission status, words-today, sacred-terms-corrected, recent feed.
- History: list, raw↔corrected diff, mode + fired-correction chips, copy, search/filter.

### Phase 3 — Glossary management (gated on decision 3)
- Searchable term table (term · category · definition · aliases · protected shield).
- "Add / correct a term" writes to a **local override layer**; export path back to Mandir.

### Phase 4 — Meetings + diarization (separate epic)
- Start/stop capture → destination folder; live speaker-labelled, timestamped transcript;
  saved-meetings list; Markdown export.
