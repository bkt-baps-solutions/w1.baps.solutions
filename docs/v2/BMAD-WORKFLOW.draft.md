# w1 to Wispr Flow Parity: BMAD v6.9.0 Workflow Plan

## 0. Preconditions that must be settled before step 1 runs

**Path notation used below.** `{PR}` = resolved `{project-root}`. `PA` = `{PR}/_bmad-output/planning-artifacts`. `IA` = `{PR}/_bmad-output/implementation-artifacts`. Today `{PR}` resolves to `/Users/jaypatel/Vault` because `_bmad/` exists only there, so every path below lands in the shared Vault tree unless **D0** is settled first.

**Three install defects the recon found, and the workaround baked into this plan:**

1. `bmad-create-epics-and-stories` globs `{PA}/*prd*.md` and `{PA}/*architecture*.md` one level flat, but `bmad-prd` and `bmad-architecture` write into dated run subfolders. Handled at Step 12 by sharding the PRD and hand-feeding paths at its step-01 prompt.
2. `bmad-investigate`'s row in `bmad-help.csv` and `bmm/module-help.csv` has a missing comma, blanking its `phase`. `bmad-help` will never route to it. Always invoke it by name.
3. `bmad-spec` has no discovery glob in `bmad-create-epics-and-stories`. SPEC.md must be handed over manually.

**Deprecated skills are not used anywhere in this plan.** `bmad-create-prd`, `bmad-edit-prd`, `bmad-validate-prd` are all replaced by **`bmad-prd`** (create / update / validate intents). `bmad-create-architecture` is replaced by **`bmad-architecture`**.

---

## 1. Phase-by-phase sequence

### Phase 1: Analysis

**Step 1. `bmad-document-project`**
- Trigger: `document this project`
- Phase: analysis
- Input: the w1 working tree at `/Users/jaypatel/Vault/baps.solutions/w1.baps.solutions` on `wip/settings-ui` (`be59260`), plus the recon inventory of stale docs.
- Produces: current-state brownfield documentation that supersedes `PLAN.md`, `docs/UI-PLAN.md`, `docs/base44-ui-prompt.md`, `ui/index.html` and the `web/` marketing copy, all of which describe a four-mode product that no longer exists in code.
- Output: `{PR}/docs/` (resolves from `project_knowledge`).
- Why first: every downstream skill will otherwise ingest specs for a deleted product.

**Step 2. `bmad-investigate`** (invoke by name, its catalog row is broken)
- Trigger: `investigate whether the multi-mode correction removal in wip/settings-ui was deliberate, and what depends on rules.py, transliterate.py and terminology_rules.json`
- Phase: catalogued 4-implementation, used here as an analysis-band forensic step.
- Input: `git diff main..wip/settings-ui`, `correction/rules.py` (dead, would raise `AttributeError`), `correction/transliterate.py` (127 lines, orphaned, complete), `terminology_rules.json` (20 KB, unloadable because `w1_data._DATASETS` excludes it), `git show main:tests/core/test_transliterate.py` (deleted, recoverable).
- Produces: an evidence-graded finding that settles **D1**.
- Output: `{IA}/mode-system-removal-investigation.md`

**Step 3. `bmad-technical-research`**
- Trigger: `produce a technical research report`
- Phase: analysis
- Input: the questions that gate the whole architecture. Local LLM options on Apple Silicon for Polish / Formal / Street / Prompt Engineer / meeting summarisation (MLX vs llama.cpp, quantisation, RAM contention alongside `whisper-large-v3-turbo`). macOS system-audio capture (ScreenCaptureKit vs CoreAudio process taps, permission surface, PyObjC reachability). Local diarization for speaker labels (pyannote vs sherpa-onnx vs channel-split heuristic). WKWebView-to-Python bridge patterns. Whether "join meeting" can exist without a cloud bot.
- Produces: a feasibility report with a recommendation per question, plus a memory and latency budget.
- Output: `{PA}/` research document.
- SOR-2 note: this report must include, for every candidate dependency, publish age, weekly download volume, install-script audit result, and the exact version to pin. No install happens at this step.

**Step 4. `bmad-forge-idea`** (core, `anytime`)
- Trigger: `pressure-test this idea`
- Phase: run in the analysis band.
- Input: the single hardest product question, stated bluntly: *w1's differentiator is 100% on-device, and every mode Jay asked for except plain dictation is LLM-dependent.*
- Produces: a hardened position that becomes the PRD's opening constraint and the input to **D3**.
- Output: `{PR}/_bmad-output/forge/{slug}/`

**Step 5. `bmad-product-brief`**
- Trigger: `create a product brief`
- Phase: analysis
- Input: Jay's raw request verbatim, the Wispr Flow capability map, the tracker design-system extraction, Steps 1 to 4.
- Produces: `brief.md`
- Output: `{PA}/briefs/brief-w1-{date}/`
- Skip `bmad-prfaq`. It stress-tests a market launch narrative. w1 is a single-operator tool with a known user, so the brief is the right altitude and PRFAQ would burn a cycle on a customer story that does not exist.

### Phase 2: Planning

**Step 6. `bmad-prd`** (create intent)
- Trigger: `create a PRD for w1`
- Phase: planning, **required**
- Input: the brief, the technical research report, the investigation, the Wispr parity scoping table (which features are cloud-hard vs locally computable), the raw user input including the full Prompt Engineer system prompt, the Polish/Formal/Street/Meeting/Join-meeting definitions, the language rule (English default, Gujarati and Mixed in the menu, transliteration always with **ā only, no other diacritic**), the summarisation routing to `jay@osx.earth` / `baps.solutions` / `sapio.health`, and the Insights screen composition.
- Produces: `prd.md` plus `addendum.md` (rejected alternatives, options matrices, the local-vs-cloud mechanism decision, personas, sizing) plus `.memlog.md`.
- Output: `{PA}/prds/prd-w1-{date}/`
- Pin `project_name = "w1"` for this run so the folder is self-identifying, since the tracker run proved `project_name` is supplied ad hoc rather than resolved.

**Step 7. `bmad-ux`**
- Trigger: `lets create UX design`
- Phase: planning
- Input: `prd.md` + `addendum.md`, plus the full tracker design-system extraction as a hard constraint (Jay's instruction: *the new UI will be based on tracker.baps.solutions*).
- Produces the peer pair:
  - `DESIGN.md`: the 19 HSL semantic tokens verbatim for `:root` and `.dark` (warm-grey hue 50 dark, not shadcn blue-grey), the `@theme inline` `--color-*` namespace, the radius scale with the deliberate `rounded-xl` passthrough at 12px, Onest + JetBrains Mono via variable axis with no weight array, the mono-mode weight shift and `-0.045em` tracking, the four glass recipes (`.card-glass`, `.liquid-glass`, `.liquid-glass-pill`, tint/pastel), the 18px dot-grid lattice with cursor spotlight, the `.app-tip` body-singleton tooltip, the arbitrary-px type scale (`text-[13px]` dominant), lucide at 14/16/18/20/22px with the 1.7/1.9/2/2.1/2.2 stroke-width convention, and the Tailwind stock shadow scale pinned to 4.1.4.
  - `EXPERIENCE.md`: the shell IA remapped from tracker's project model to w1's, the widget states, mode switching, meeting live-transcript behaviour, permission onboarding, empty and error states, reduced-motion behaviour, and keyboard-only operation.
- Output: `{PA}/ux-designs/ux-w1-{date}/`
- Carry forward the recon's open questions as explicit design calls: retire the `--tracker-*` hex constants (they have no `.dark` override, so `bg-tracker-surface-sunken` renders near-white in dark mode), pick one avatar/priority palette rather than carrying both v1 and demo-parity registries, and drop the dead `#root { height: 100% }` rule.

**Step 8. `bmad-prd`** (validate intent, same skill)
- Trigger: `validate the PRD`
- Phase: planning
- Input: `prd.md` + the two UX spines.
- Produces: `review-{slug}.md` and `reconcile-{slug}.md` inside the existing run folder, and flips `status` to `final`.
- Output: same `{PA}/prds/prd-w1-{date}/`

### Phase 3: Solutioning

**Step 9. `bmad-architecture`**
- Trigger: `create the architecture`
- Phase: solutioning, **required**
- Input: `prd.md`, `addendum.md`, `DESIGN.md`, `EXPERIENCE.md`, technical research, and the existing import-linter contract forbidding `w1_core` from importing `w1_macos`, `rumps`, `pynput`, `sounddevice`, `pyperclip`, `AppKit`, `Quartz`, `objc`.
- Produces `ARCHITECTURE-SPINE.md` carrying only invariants. The ones this project actually needs:
  - The **egress boundary**: exactly one module may perform network I/O, and `w1_core` may never import it. Enforced as a new import-linter contract, not by discipline.
  - The **LLM adapter boundary**: one Protocol, three implementations (none / local / cloud), with per-mode policy resolved before the adapter is reached.
  - The **diacritic invariant**: every text egress path passes a filter that permits `ā` and no other diacritic, including LLM output.
  - The **storage boundary**: history and stats live behind one store with a three-way retention policy, and nothing else in the app may persist transcripts.
  - The **Vault write boundary**: a path allowlist per destination, a hard denylist on `Secrets/` and any `.env`, and no writes to `~/Desktop/Repositories` or the iCloud archive.
  - The **UI transport boundary**: whatever D2 decides, the Python core exposes one message contract and the shell is a third platform adapter alongside `w1_macos`.
  - The **hot path rule**: plain dictation never touches the LLM adapter.
- Output: `{PA}/architecture/architecture-w1-{date}/ARCHITECTURE-SPINE.md` + `.memlog.md`

**Step 10. `bmad-spec`** (core, `anytime`)
- Trigger: `create a spec`
- Phase: sits orthogonal to the phases, run here because `bmad-architecture` explicitly routes to it and treats the spec package as the spine's home.
- Input: `ARCHITECTURE-SPINE.md` (adopted as a companion with stable `AD` ids), `prd.md` as a companion, the UX pair as adopted companions.
- Produces: `SPEC.md` with the five-field kernel and stable `CAP-N` capability ids that the epics will reference, plus spec-authored companions (`glossary.md` for the BAPS terminology contract, `stack.md` for the exact pins, `brownfield.md` for the dead-code disposition, `failure-modes.md`).
- Output: `{PR}/_bmad-output/specs/spec-w1/`

**Step 11. `bmad-shard-doc`**
- Trigger: `perform shard document`
- Phase: solutioning, mechanical
- Input: `prd.md` (the tracker PRD ran to 35.6 KB, w1's will exceed the ~500 line threshold).
- Produces: an `index.md` plus H2 shards at `{PA}/prd-w1/`, which is what makes the next step's `{PA}/*prd*/index.md` sharded branch actually match.
- Output: `{PA}/prd-w1/`

**Step 12. `bmad-create-epics-and-stories`**
- Trigger: `create the epics and stories list`
- Phase: solutioning, **required**
- Input: the sharded PRD (auto-discovered after Step 11) plus, hand-fed at its step-01 "any other documents to include?" halt, the absolute paths to `ARCHITECTURE-SPINE.md`, `SPEC.md`, `DESIGN.md`, `EXPERIENCE.md`. This manual handoff is mandatory, not optional, because of the glob defects.
- Produces: `epics.md`
- Output: `{PA}/epics.md` (flat file, not a run folder)

**Step 13. `bmad-check-implementation-readiness`**
- Trigger: `check implementation readiness`
- Phase: solutioning, **required**
- Input: PRD, UX pair, architecture spine, epics.
- Produces: a readiness report. Treat a fail here as a hard stop, not advisory. Add one project-specific check to the run: confirm every epic that touches text output references the ā-only invariant, and every epic that touches network references the egress boundary.
- Output: `{IA}/` readiness report

**Step 14. `bmad-generate-project-context`**
- Trigger: `generate project context`
- Phase: catalogued `anytime`, run here so implementation inherits it.
- Input: the spine, the standing rules from `~/Vault/CLAUDE.md`.
- Produces: `project-context.md`, which is the default `persistent_facts` file every skill loads. Encode into it: Conventional Commits, ask before any commit / push / branch operation, exact dependency pins, SOR-2 gate before any install, never touch `Secrets/` or `.env`, no PHI or PII in logs or test data, no time estimates, no em-dashes in generated prose, and the ā-only diacritic rule.
- Output: `{PR}/project-context.md`

### Phase 4: Implementation

**Step 15. `bmad-sprint-planning`**
- Trigger: `run sprint planning`
- Phase: implementation, **required**
- Input: `{PA}/epics.md` (this glob does line up, since epics is written flat).
- Produces: `sprint-status.yaml`
- Output: `{IA}/sprint-status.yaml`

**Step 16. The story cycle, repeated per story, one worktree per epic (SOR-1).**

| Order | Skill | Trigger | Consumes | Produces / Path |
|---|---|---|---|---|
| a | `bmad-create-story` (create) | `create the next story` | sprint-status.yaml, epics.md, spine, SPEC.md | `{IA}/{story_key}.md` (e.g. `2-3-glass-materials.md`) |
| b | `bmad-create-story` (validate) | `create story [id]` then validate action | the story file | validated story file in place |
| c | `bmad-dev-story` | `dev this story [story file]` | the story file | code in an epic worktree, tests, no commit without Jay's approval |
| d | `bmad-code-review` | `run code review` | the diff | triaged findings. Issues route back to c |
| e | `bmad-qa-generate-e2e-tests` | `create qa automated tests for [feature]` | the shipped feature | tests. Used for the golden corpora, not for review |
| f | `bmad-checkpoint-preview` | `checkpoint` | the epic's accumulated diff | a human-review walkthrough before the PR gate |
| g | `bmad-retrospective` | `run a retrospective` | the completed epic | lessons, feeds `bmad-correct-course` if scope moved |

**Sidecars, invoked as needed:**
- `bmad-sprint-status`, trigger `check sprint status`, for state across parallel worktrees.
- `bmad-correct-course`, trigger `correct course`, whenever a decision point reopens mid-sprint (very likely on D3 and D5).
- `bmad-quick-dev`, reserved strictly for out-of-band fixes not in the sprint. Never used to bypass the story cycle for planned epic work.
- `bmad-review-edge-case-hunter` on the correction chain, the diacritic filter, and the Vault write path. It is method-driven and orthogonal to `bmad-code-review`'s adversarial layers, so both are worth running on those three surfaces specifically.
- `bmad-advanced-elicitation` (pre-mortem, red team) on the summarisation routing design before it is built.
- `bmad-agent-tech-writer` at the end of each epic to update `docs/` and, critically, to correct `web/` and `ui/index.html`, which currently advertise four deleted modes to the public internet.

---

## 2. Proposed epic breakdown

Dependency order runs top to bottom. **UI** = presentation work against an existing or trivially-derived data source. **Engine** = new or substantially reworked `w1_core` / `w1_macos` capability.

| # | Epic | Type | Scope and the specific things that make it non-trivial |
|---|---|---|---|
| **E1** | Repo truth reset and boundary hardening | Engine (existing) + infra | Resolve D1 and act: delete `rules.py` and `terminology_rules.json` or rewire them. Fix `ingest_glossary_pdf.py` and `sync_rules_from_ts.py`, both of which hardcode `~/Desktop/Repositories/Mandir`, a path the workspace ground truth marks never-write. Create the `.github/` CI that PLAN.md promised: headless core-only install, `lint-imports`, pytest, coverage gate. Populate the empty `tests/data/` with the frozen 20-sentence golden set and the pure-English do-not-corrupt corpus that PLAN.md §8 makes a release gate. Clean `.venv_old_w4k/`, `build/`, `.import_linter_cache/` w4k residue, `.coverage 2`, `web/vite.config 2.ts`. Blocks everything. |
| **E2** | Design system port and app shell | **UI only** | Port tracker's `globals.css` wholesale: 19 tokens, `@theme inline` namespace, radius scale with the `rounded-xl` passthrough, four glass recipes, dot-grid lattice, `.app-tip` singleton, mono mode with its weight shift, reduced-motion neutraliser. Port the 13 shadcn primitives and the 16-file `view/` primitive layer. Adapt the three-column shell: sidebar (Home, History, Dictionary, Snippets, Modes, Meetings, Insights, Settings), opaque `rounded-3xl` content panel, resizable glass right rail. Two ports that are not copy-paste: tracker's dark mode is cookie-driven SSR under Next 15, which becomes localStorage plus the same synchronous boot script in a static build; and Tailwind must be pinned to **exactly 4.1.4** because no shadow tokens are defined, so a minor bump silently drifts the shadow rendering. |
| **E3** | Dictation core, hotkey and insert layer | Engine (hardening) | Keep the working pipeline: `transcribe_and_correct`, artifact denylist, confidence gate, mask/fuzzy/unmask chain, clipboard paste with restore, AX `editable_target()` conservative fallback, paste panel. Add: Esc cancel, target-field tracking across app switches, insertion long-tail fixes (IDEs, terminals, remote desktops, browser address bars, notification reply boxes), and end-to-end latency instrumentation against the p99 budget. Remove any session cap: an on-device product has no per-request cost, which is a real differentiator over Wispr's 20-minute stop. |
| **E4** | Local history and stats store | **Engine (new)** | The precondition for E10, and the epic where the zero-storage promise is formally renegotiated (see D6). Three-way retention policy (store / auto-delete every 24h / never store). Capture at insert time: word count, duration, WPM, corrections applied split into word-corrections and dictionary-fixes, target app bundle id mapped to a category (AI prompts, work messages, personal messages, emails, documents, other), mode used. Single writer, single reader, everything else goes through it. |
| **E5** | Mode system | **Engine (new)** + UI | Five modes. **Formal** and **Street** are largely deterministic and can extend the existing `cleanup.py` and a new punctuation/capitalisation stage: Formal punctuates, capitalises and lightly formalises; Street keeps colloquialisms and suppresses capitalisation entirely. **Polish** (Opt+1) and **Prompt Engineer** are generative and require the LLM adapter, and Prompt Engineer carries a fixed multi-section system prompt (Title, Role and stance, Task, Context, Inputs available, Output requirements, Constraints, Examples, Execution checklist, Conflict resolution). Plus the selection-based Transforms path: read highlighted text via AX, rewrite, offer a diff view before replacing. Plain dictation remains a mode that never reaches the adapter. |
| **E6** | Language and transliteration | **Engine (part revival)** | English default; Gujarati and Mixed in the menu. Revive `transliterate.py` with its test recovered via `git show main:tests/core/test_transliterate.py`. Restore Whisper `language="gu"` routing that went away with `CorrectionMode.gujarati`. Enforce the **ā-only** invariant as a filter on every egress path, including generative-mode output, backed by a property test. Mixed mode needs its own strategy: Wispr detects language once per session and cannot alternate mid-sentence, so decide whether w1 does a single-pass Gujarati decode plus transliteration, or a segment-level detect. |
| **E7** | Meeting mode: local capture | **Engine (new)** + UI | Dual-stream capture: microphone plus system audio via ScreenCaptureKit or a CoreAudio process tap, which requires a **new macOS permission** and therefore touches E12. Live incremental transcript, which means chunked or streaming decode rather than the current record-then-transcribe loop, a genuine change to the controller. Speaker labels via either local diarization or the cheap and surprisingly effective channel-split heuristic (mic stream is Jay, system stream is everyone else), with the heuristic as the shipping default and diarization behind D3's local-model decision. New live transcript surface in the shell. Persistent consent notice. |
| **E8** | Auto-capture meeting mode (Teams, Meet, Zoom) with Vault routing | Engine + integrations | Detect the active meeting by browser and app (Chrome/Edge/Brave for Meet, Zoom client, Teams client) and by calendar. Arm capture contextually. Ask for, or infer, the Vault destination folder at capture time. Naming depends on D5: if the no-bot model is chosen, this is "auto-capture", not "join". |
| **E9** | Post-meeting summarisation, Vault write-back and task generation | **Engine (new)** + integrations | Route by destination: `jay@osx.earth`, `baps.solutions`, `sapio.health`. For each, read existing Vault context so the summary is contextualised rather than generic, update the relevant notes in place, and generate tasks. Needs a long-context model, so it is the sharpest point of D3. Needs the Vault write contract from the spine: path allowlist per destination, hard denylist on `Secrets/` and `.env` with a test proving it, tasks landing in an inbox for one-click promotion rather than direct insertion. `sapio.health` destination gets a stricter policy than the other two. |
| **E10** | Insights analytics surface | **UI only** (given E4) | Rebuild the screenshotted screen on tracker's material: WPM radial gauge with `useCountUp`, corrections tile split into words-corrected and dictionary-fixes, cumulative total words with a month-over-month badge, horizontal app-category bar chart with the light/moderate/power intensity bands, and a GitHub-style contribution heatmap with current and longest streak. Omit the global percentile and the leaderboard, both of which require a server and a population (see D8). Add a graceful empty state when retention is set to "never store". |
| **E11** | Dictionary, snippets and glossary management | UI + light engine | Surface the 201-entry glossary, the 948-entry master glossary, the 20 protected terms and the 74 bias-seed terms that already exist and are currently invisible. Add auto-learning from typed corrections, misspelling replacement rules, and voice-triggered snippet expansion. Not named in Jay's request but is a large part of what makes Wispr feel useable. Mark as the parity backlog epic, cut first if scope pressure arrives. |
| **E12** | Packaging, permissions and distribution | Infra | Developer ID signing plus `xcrun notarytool` plus stapling, currently documented but never performed. Add the system-audio permission to the entitlements and the onboarding wizard alongside microphone and accessibility. Build a first-run permissions flow with re-check gating, since ad-hoc signing silently kills the global key listener (commit `9efd0ef` proves it). Correct `docs/PACKAGING.md`, which still says "ship the unsigned .app" while `build.sh` always signs. Must run early enough that E7's new permission is validated on a signed build rather than at the end. |

**Summary by type.** UI-only: E2, E10, and the surfacing half of E11. New engine work: E4, E5, E7, E8, E9, plus the revival half of E6. Existing engine hardening: E1, E3. Infrastructure: E12.

---

## 3. Decision points Jay must settle

### D0. BMAD scoping. Blocks Step 1.
- **(a)** Run from the Vault root. All w1 output collides with tracker's finalized PRD in one `_bmad-output` tree. Zero setup.
- **(b)** Second `npx bmad-method@6.9.0 install` inside `w1.baps.solutions`, giving it a project-local `_bmad/` and `_bmad-output/`.
- **(c)** Override `output_folder` in `_bmad/custom/config.toml`. This is a team-wide file, so it would repoint tracker's output too.

**Recommendation: (b).** Version 6.9.0 already passed the SOR-2 gate on 2026-07-27 (no pre/postinstall scripts, 17k weekly downloads, exact-pinned), so re-installing the identical pinned version is a no-cost repeat of a cleared decision. It gives w1 a self-contained artefact trail inside its own repo, makes `project_knowledge` resolve to w1's own `docs/` (which E1 needs), and leaves the tracker PRD untouched. Reject (c) outright: it silently repoints an unrelated project.

### D1. Is the multi-mode removal deliberate? Blocks E1 and E5.
- **(a)** Treat the removal as canonical. Delete `rules.py` and `terminology_rules.json`. Build the new modes fresh on the LLM adapter.
- **(b)** Revert to `main`'s rule-based mode system and extend it.

**Recommendation: (a), with one carve-out.** The new mode set Jay described (Prompt Engineer, Polish, Formal, Street) is generative rewriting, not regex substitution, so the 64 terminology rules serve none of it, and the current engine's explicit no-substitution contract ("temple" stays "temple") is a correctness guarantee worth keeping. The carve-out: `transliterate.py` is complete, was tested, and is the repo's only Gujarati-script-to-Roman capability. Revive it under E6 with its recovered test rather than deleting it with the rest.

### D2. Shell technology. Blocks E2 and every UI epic.
- **(a)** Stay pure Python/PyObjC, build the hub as native AppKit. No reuse of tracker at all: 19 tokens, four glass materials, a dot lattice, a radial gauge and a contribution heatmap all hand-ported to AppKit. High cost, poor fidelity on exactly the surfaces Jay screenshotted.
- **(b)** Keep the Python core and macOS adapter, add an embedded WKWebView hosting a Vite + React 19 + Tailwind 4.1.4 static build of the tracker design system, bridged via `WKScriptMessageHandler`.
- **(c)** Tauri v2 shell with the Python core as a sidecar. Best web reuse, but adds a Rust toolchain, sidecar packaging, a second signing surface, and forces re-plumbing of pynput, the AX layer and ScreenCaptureKit across IPC.
- **(d)** Electron. Heaviest resident footprint for an always-on menu-bar app.

**Recommendation: (b).** All of w1's actual value is in `w1_core` plus the macOS AX, hotkey and inject layer, all working today, and the existing import-linter contract already treats platform code as a swappable adapter. A WKWebView is a third adapter, not a rewrite. Two adjustments the port needs: tracker is Next.js with cookie-driven SSR dark mode, so the static build swaps the cookie for localStorage while keeping the identical synchronous boot script; and the floating widget stays a native `NSPanel` regardless, because a webview cannot be click-through, non-activating, screensaver-level and joined to all Spaces. Revisit (c) only if E7's live transcript proves too heavy over the bridge.

### D3. Local model versus any cloud call. The headline decision. Blocks E5, E7 and E9.
- **(a)** 100% on-device, local LLM only. Preserves the promise absolutely. Costs quality on Prompt Engineer and meeting summarisation, adds RAM contention alongside `whisper-large-v3-turbo`, and adds cold-start latency to Polish.
- **(b)** Local by default, with per-mode and per-destination opt-in to a cloud model, a non-defeatable visible indicator while any cloud call is in flight, and an audit log.
- **(c)** Cloud for everything, Wispr's model.

**Recommendation: (b), with a hard, code-enforced split.** Local-only, permanently, with no cloud path reachable: dictation, the correction chain, Formal, Street, transliteration, and meeting transcription. Local-by-default with explicit opt-in, off until enabled: Polish, Prompt Engineer, meeting summarisation. Reject (c): it destroys the only differentiator over an app that is better funded and faster, and makes the tool unusable in any clinical context. Reject (a) as the sole option only because meeting summarisation over a long transcript with Vault context is where local models are genuinely weak, and Jay should have the switch rather than a silently degraded feature.

Two conditions attach. First, the boundary must be an architecture invariant enforced by an import-linter contract and an egress test, not by convention. Second, E1 must rewrite the Settings footer and the deployed `web/` marketing site from "nothing is stored" to a truthful two-tier statement, because the current copy is already false about four modes that no longer exist.

### D4. Latency budget. Blocks E3's release criteria.
- **(a)** One budget for everything, matching Wispr's sub-700ms p99 end to end.
- **(b)** Split budgets by path.

**Recommendation: (b).** Plain dictation gets a hard p99 gate from key-release to text-inserted as a release criterion, benchmarked against Wispr's published 700ms. Polish and Prompt Engineer get a "visible progress, never blocking, always cancellable" contract instead of a latency number. Meeting summarisation is explicitly asynchronous and backgrounded. Pair this with the hot-path invariant from the spine: plain dictation never touches the LLM adapter, so adding modes cannot regress it.

### D5. What "join meeting" actually means. Blocks E8.
- **(a)** A real bot participant joining via Teams, Google and Zoom APIs. Requires cloud infrastructure, three OAuth integrations, and routes meeting audio through a third party.
- **(b)** Local system-audio capture with calendar awareness and no participant joining, which is Wispr Notetaker's model.
- **(c)** A locally driven headless browser that joins Google Meet from Jay's own machine.

**Recommendation: (b), and rename the mode.** Call it "auto-capture meeting", not "join meeting", so the product does not overclaim. (a) directly contradicts everything D3 protects. (c) is technically possible for Meet only, but raises consent and platform terms-of-service problems, and in any NHS or clinical setting recording others may be prohibited outright. If Jay genuinely needs capture of meetings he is not personally in, that is a separate later decision, not part of this build.

### D6. Zero-storage promise versus history and Insights. Blocks E4 and E10.
- **(a)** Keep zero storage and drop Insights entirely.
- **(b)** Adopt Wispr's three-way local policy: store, auto-delete every 24 hours, never store. Insights degrades gracefully.
- **(c)** Always store.

**Recommendation: (b), defaulting to store-locally-only with no cloud sync ever.** Note this is where Wispr is actually a useful precedent rather than a foil: its transcript history is genuinely local by default and is not synced unless explicitly enabled. Add a single "clinical mode" preset that flips retention to never-store and disables every cloud tier from D3 in one switch, so Jay can hard-lock the app before a shift rather than trusting six separate toggles.

### D7. Vault write authority. Blocks E9.
- **(a)** w1 writes summaries and tasks directly into `~/Vault`.
- **(b)** w1 writes only into a staging inbox for review.
- **(c)** Tasks go through tracker's API rather than the filesystem.

**Recommendation: a hybrid.** Summaries write directly into a per-destination allowlisted folder, since a summary that needs manual filing is a summary that never gets filed. Generated tasks land in an inbox for one-click promotion, since a wrong task is worse than a missing one. Both paths sit behind a hard denylist on `Secrets/` and `.env` enforced in code with a test, and never write to `~/Desktop/Repositories` or the iCloud archive. Defer (c) until tracker exposes a stable task API.

### D8. Percentile and leaderboard in Insights. Blocks E10.
- **(a)** Show a global percentile, which requires population data w1 does not have and cannot get without a server.
- **(b)** Omit it.
- **(c)** Replace it with a self-referential comparison.

**Recommendation: (c).** Wispr's "Top 0.2%" and the whole Leaderboard tab are a deliberate growth loop for a multi-tenant SaaS with an account system. w1 has one user and no account. Replace the percentile with a rolling personal baseline (this week against your 30-day median), keep the streak, keep the "you've written 1 book chapter" style milestone framing since that needs no external data, and drop the leaderboard and the social share carousel entirely.

### D9. Glossary source of truth. Blocks E1.
- **(a)** Locate Mandir's new home in the Vault and re-point both ingestion scripts.
- **(b)** Freeze `master_glossary.json` as vendored data with a checksum test and retire the scripts.

**Recommendation: (a) if Mandir is findable in the Vault, otherwise (b).** Either way the hardcoded `~/Desktop/Repositories/Mandir` paths must go before E1 closes, because the workspace ground truth marks that location historical and never-write, which means neither script can currently regenerate its own data.

### D10. Dependency additions, all SOR-2 gated.
No installs happen before Step 3's technical research report delivers, for each candidate: publish age (must exceed one month), weekly download volume, install-script audit, and the exact version to pin. Candidates this project will need: a local LLM runtime (`mlx-lm` or `llama-cpp-python`), possibly a diarization package (prefer the zero-dependency channel-split heuristic first), the web build chain pinned to tracker's exact versions (`tailwindcss` 4.1.4, `@tailwindcss/postcss` 4.1.4, `lucide-react` 0.468.0, `class-variance-authority` 0.7.1, `tailwind-merge` 3.5.0, the six Radix packages), and Vite plus React 19. Prefer native ScreenCaptureKit through PyObjC over any new capture dependency.

---

## 4. Risks and how the workflow de-risks them

**R1 (headline). The on-device promise versus LLM-dependent modes.** Every mode Jay asked for except plain dictation is a rewriting task, and Wispr's own docs are blunt that this is why it is cloud-only ("Transcription always occurs on the cloud", "runs entirely in the cloud"). Meanwhile w1's Settings footer and marketing site both promise nothing leaves the device. De-risked by: Step 3 answering local-model feasibility **before** the PRD is written rather than after; Step 4 forging the tension explicitly rather than letting it stay implicit; D3 splitting the modes into a permanently-local set and an opt-in set; the spine making that split an import-linter-enforced invariant rather than a code-review habit; a `bmad-qa-generate-e2e-tests` run asserting zero network egress from the local-only path; and E1 correcting the copy that is already false.

**R2. Scope explosion.** Wispr has roughly 25 distinct features and this plan has 12 epics. De-risked by the `bmad-check-implementation-readiness` gate at Step 13, by E11 being explicitly labelled the cut-first backlog epic, and by the parity scoping table from the recon being carried into the PRD so "not building this" is written down rather than assumed.

**R3. Building from stale specs.** `PLAN.md`, `docs/UI-PLAN.md`, `docs/base44-ui-prompt.md`, `ui/index.html` and the deployed `web/` site all describe a four-mode product with history, glossary management and meetings that do not exist, and `docs/UI-PLAN.md` even makes two false claims about `settings_window.py`. De-risked by `bmad-document-project` running first, and by the PRD explicitly declaring those five documents superseded.

**R4. BMAD's own install defects.** Output collision at the Vault root, the epics skill unable to discover the PRD or the architecture, and `bmad-investigate` unroutable. De-risked by D0, by Step 11's shard producing the `index.md` that makes the sharded glob match, by the hand-feed at Step 12's step-01 halt being mandatory rather than optional, and by invoking `bmad-investigate` by name.

**R5. The diacritic invariant leaking through generative modes.** A local LLM will happily emit `é`, `ṇ` or `ā`-adjacent forms. De-risked by making the ā-only filter an egress-path invariant in the spine (so it applies after the LLM, not only after the transliterator), and by a property test in E6 that fuzzes generated output.

**R6. macOS permission and packaging regression.** Ad-hoc signing silently kills the global key listener, proven by commit `9efd0ef`, and E7 introduces a brand new system-audio permission. De-risked by scheduling E12 early enough to validate the new permission on a signed build, and by a smoke test on the signed artefact at every epic's PR gate rather than only at release.

**R7. Latency regression on the hot path.** Adding a mode dispatch in front of insertion is the obvious way to slow down the one thing that already works. De-risked by D4's split budgets, the spine's hot-path invariant, and a p99 measurement as a named release criterion in the readiness check.

**R8. Parallel Claude sessions clobbering work.** The standing rules already flag this. De-risked by SOR-1's worktree-per-epic model with PR gates, by `bmad-sprint-status` as the cross-worktree state view, and by the ask-before-commit rule below.

**R9. Consent and legality of meeting capture.** Recording others, especially in NHS contexts, is not universally permissible. De-risked by D5 choosing the no-bot model, a persistent consent notice during capture, and the `sapio.health` destination inheriting a stricter never-store, never-cloud policy by default.

**R10. Memory contention on Apple Silicon.** `whisper-large-v3-turbo` plus a 7-8B LLM plus optional diarization on one machine, while the app is menu-bar resident. De-risked by Step 3 producing an explicit memory budget, and by that budget becoming an invariant in the architecture spine so model choices in E5, E7 and E9 are constrained rather than negotiated per epic.

---

## 5. How the standing rules are baked in

**SOR-1 (plan, orchestrate, code, QA, parallel fleet).** The plan phase is Steps 1 to 14. Orchestration is Step 15's `sprint-status.yaml`. Code is `bmad-dev-story`. QA is `bmad-code-review` plus `bmad-qa-generate-e2e-tests` plus `bmad-review-edge-case-hunter` on the three highest-risk surfaces. The parallel fleet runs one git worktree per epic, each gated by a PR, with `bmad-checkpoint-preview` as the human review before the gate and `bmad-retrospective` after the merge. E1 must land on its own before any fleet fans out, because it changes the test and CI substrate everything else builds on.

**SOR-2 (dependency security gate).** No `npm` or `pip` install occurs anywhere in Phases 1 to 3. Step 3's technical research report is the gate document: for every candidate it must record publish age over one month, weekly download volume, an install-script audit, and an exact version to pin. D0's BMAD re-install is a repeat of an already-cleared decision on the identical pinned version. The web build chain is pinned to tracker's exact versions rather than a range, specifically because the recon showed no shadow tokens are defined, so a Tailwind minor bump would silently change the rendering.

**Conventional Commits.** Encoded in `project-context.md` at Step 14, so every `bmad-dev-story` run inherits it.

**Ask before any commit, push or branch operation.** Encoded in `project-context.md` and restated in every story file. `bmad-dev-story` produces code in a worktree and stops. Branch creation for a new epic worktree, every commit, and every push each require Jay's explicit go-ahead, because parallel sessions may be active on the same repo. Note the repo is currently on `wip/settings-ui` in sync with origin, with `main` one commit behind, so the branch strategy itself is a decision to confirm before the first worktree is cut.

**Exact pins.** Already the pattern in `pyproject.toml` (pydantic 2.13.4, rapidfuzz 3.14.5, jellyfish 1.2.1, pyyaml 6.0.3, numpy 2.4.6). Extended to the new web chain and to any model runtime.

**Never touch `Secrets/` or `.env`, no PHI or PII in logs or test data.** Enforced twice over: as a denylist in the Vault write boundary invariant in the architecture spine (E9), and as a test that proves the denylist holds.

**No time estimates.** None appear in this plan, and `project-context.md` carries the rule forward so no generated story, epic or sprint artefact introduces one.