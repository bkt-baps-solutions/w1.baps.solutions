# w1: BMAD v6.9.0 Workflow Plan

**Product framing (changed since the draft).** w1 is a general purpose, on-device personal dictation tool for macOS. The BAPS and Mandir terminology glossary is **one capability among several**, not the product identity. The product moves from `w1.baps.solutions` to **`w1.osx.earth`** and from the `bkt-baps-solutions` GitHub org to **`osx-earth`**.

**Gujarati scope (changed since the draft).** Deep Gujarati accuracy work is explicitly **out of near-term scope**. Jay will supply transliterated text plus matched audio for training at a later date. What stays in near-term scope is the **language menu** (English default, Gujarati and Mixed selectable) and the **ā-only egress invariant**. What leaves near-term scope is any model tuning, fine-tuning, decoder work or accuracy programme for Gujarati. See E15.

---

## 0. Preconditions that must be settled before Step 1 runs

**Path notation.** `{PR}` = the resolved `{project-root}`. `PA` = `{PR}/_bmad-output/planning-artifacts`. `IA` = `{PR}/_bmad-output/implementation-artifacts`. `OF` = `{PR}/_bmad-output` (the `output_folder` itself, which is a sibling of PA and IA, not a parent-only container).

**Today `{PR}` resolves to `/Users/jaypatel/Vault`,** because `resolve_config.py` requires `--project-root` to contain a `_bmad/` directory and `_bmad/` exists at exactly one location in the whole Vault. Every path below lands in the shared Vault tree unless **D0** is settled first.

### P1. Do the rebrand move BEFORE anything else (see D14)

Every absolute path in this plan, including the `--project-root` argument passed to `resolve_config.py` and `resolve_customization.py` on every single skill activation, is invalidated if the repo moves mid-run. Settle **D14** and, on the recommended answer, perform the physical move first so that `{PR}` is `/Users/jaypatel/Vault/osx.earth/w1.osx.earth` from Step 1 onward. Every path written below assumes that move has happened. If D14 goes the other way, substitute `/Users/jaypatel/Vault/baps.solutions/w1.baps.solutions` throughout and accept that the epic performing the move will have to rewrite the artefact trail.

### P2. Install defects in this BMAD build, verified, with the workaround this plan uses

1. **`bmad-create-epics-and-stories` cannot discover the PRD or the architecture spine.** Its `steps/step-01-validate-prerequisites.md` searches `{PA}/*prd*.md` then `{PA}/*prd*/index.md`, and `{PA}/*architecture*.md` then `{PA}/*architecture*/index.md`, all one level flat. `bmad-prd` writes to `{PA}/prds/prd-{project_name}-{date}/prd.md` and `bmad-architecture` writes to `{PA}/architecture/architecture-{project_name}-{date}/ARCHITECTURE-SPINE.md`, both two levels deeper. Neither glob will ever match. Handled at Step 12 by a **mandatory** hand-feed of absolute paths at the step-01 "any other documents to include for analysis?" halt. The UX pair is the one hop that works: step-01 has an explicit `{PA}/ux-designs/ux-*/DESIGN.md` plus `EXPERIENCE.md` run-folder pattern.
2. **`bmad-investigate` is unroutable through `bmad-help`.** Its row in `_bmad/_config/bmad-help.csv` and `_bmad/bmm/module-help.csv` is missing a comma, so the fields shift from `args` onward and `phase` parses as empty. The `bmm` copy is also short a whole field, 12 against a 13-column header. Always invoke `bmad-investigate` **by name**. Do not patch the CSV: those files are installer-owned and regenerated on every install.
3. **`bmad-spec` has no SPEC.md discovery glob in `bmad-create-epics-and-stories`.** SPEC.md must be handed over manually at the same step-01 halt.
4. **`bmad-generate-project-context` writes to `{OF}/project-context.md`, not `{PR}/project-context.md`.** See P3, this is load-bearing.

### P3. The `project-context.md` path defect and its concrete fix

`bmad-generate-project-context/SKILL.md:72` declares `output_file = {output_folder}/project-context.md`, and `steps/step-01-discover.md:126` plus `steps/step-03-complete.md:138,231` all write there. `output_folder` is `_bmad-output` (`_bmad/bmm/config.yaml`, `_bmad/core/config.yaml`, `_bmad/config.toml:16`). **The real path is therefore `{PR}/_bmad-output/project-context.md`.**

This matters because of a mismatch in how skills reference the file:

| Skill | `persistent_facts` entry | Will it find the file at `{OF}/project-context.md`? |
|---|---|---|
| `bmad-prd`, `bmad-architecture`, `bmad-ux`, `bmad-product-brief`, `bmad-technical-research`, `bmad-create-epics-and-stories`, `bmad-check-implementation-readiness`, `bmad-create-story`, `bmad-dev-story`, `bmad-qa-generate-e2e-tests`, `bmad-generate-project-context` itself | `file:{project-root}/**/project-context.md` | **Yes.** The `**` glob descends into `_bmad-output/`. |
| **`bmad-spec`** (`customize.toml:25-27`) | `file:{project-root}/project-context.md` | **No.** Non-glob, top-level only. It will silently load nothing. |

**The fix, and it is a concrete edit, not a note.** Before Step 1 runs, create `{PR}/_bmad/custom/bmad-spec.toml` containing:

```toml
[workflow]
persistent_facts = [
  "file:{project-root}/_bmad-output/project-context.md",
]
```

Arrays **append** under the BMad merge rules (stated at the head of every `customize.toml`), so the broken default entry survives harmlessly alongside the working one and nothing else in `bmad-spec` is disturbed. Write this file with `bmad-customize` (trigger: `customize bmad`) rather than by hand, so the override lands in the shape the resolver expects.

**Verify before relying on it,** from inside the project root:

```
uv run {PR}/_bmad/scripts/resolve_customization.py \
  --skill {PR}/.claude/skills/bmad-spec --key workflow
```

The resolved `persistent_facts` array must contain the `_bmad-output` path. Do not proceed to Step 10 until it does.

*Rejected alternative:* placing a duplicate copy at `{PR}/project-context.md`. It satisfies `bmad-spec` but creates two files that drift, and `bmad-generate-project-context`'s own re-run discovery (`step-01-discover.md:37`) looks at both `{project_knowledge}/project-context.md` and `{project-root}/**/project-context.md`, so a stray duplicate makes the "found existing context, update or create new?" prompt ambiguous. One file, one override.

### P4. Deprecated skills are not used anywhere in this plan

| Deprecated (removed in v7) | Replacement used here |
|---|---|
| `bmad-create-prd` | **`bmad-prd`**, create intent |
| `bmad-edit-prd` | **`bmad-prd`**, update intent |
| `bmad-validate-prd` | **`bmad-prd`**, validate intent |
| `bmad-create-architecture` | **`bmad-architecture`** |

None of the four appear in `bmad-help.csv`, so the router will never suggest them either.

---

## 1. Phase-by-phase sequence

### Phase 1: Analysis

**Step 1. `bmad-document-project`**
- Trigger: `document this project`
- Phase: catalogued `anytime`, run first.
- Input: the w1 working tree at the resolved project root on the branch chosen by **D11**, plus the recon inventory of stale docs.
- Produces: current-state brownfield documentation that supersedes `PLAN.md`, `docs/UI-PLAN.md`, `docs/base44-ui-prompt.md`, `ui/index.html` and the `web/` marketing copy, all of which describe a four-mode product that no longer exists in code and a BAPS-only identity the product is moving away from.
- Output: `{PR}/docs/` (resolves from `project_knowledge`).
- Why first: every downstream skill would otherwise ingest specs for a deleted product.

**Step 2. `bmad-generate-project-context`** ← *moved up from Step 14 in the draft*
- Trigger: `generate project context`
- Phase: catalogued `anytime`.
- Why here and not later: `persistent_facts` are loaded **once, at activation**. `bmad-prd/SKILL.md` "On Activation" step 2 says *"Treat `{workflow.persistent_facts}` as foundational context (entries prefixed `file:` are loaded)"*, and the step-file skills carry the same instruction as an explicit numbered step, for example `bmad-qa-generate-e2e-tests` "Step 3: Load Persistent Facts". Nothing re-reads the file mid-run. If `project-context.md` does not exist when `bmad-prd`, `bmad-architecture` or `bmad-spec` activates, the standing rules are simply absent from that entire run. This was the single largest defect in the draft plan, whose Section 5 rested its whole enforcement story on a file that would not have existed yet.
- Input: `{project_knowledge}` (which Step 1 has just populated) plus the standing rules from `~/Vault/CLAUDE.md`.
- Encode into it, at minimum: Conventional Commits. Ask before any commit, push or branch operation. Pin dependencies exactly. SOR-2 gate before any npm or pip install. Never touch `Secrets/` or `.env`. No PHI or PII in logs or test data. No time estimates in any generated artefact. No em-dashes (U+2014) in generated prose. The **ā-only** diacritic rule on every text egress path. The import-linter contract forbidding `w1_core` from importing `w1_macos`, `rumps`, `pynput`, `sounddevice`, `pyperclip`, `AppKit`, `Quartz` or `objc`.
- Output: **`{PR}/_bmad-output/project-context.md`** (see P3).
- **Re-run this step after Step 9** once the architecture spine exists, to fold the new invariants (egress boundary, LLM adapter boundary, storage boundary, Vault write boundary) into the same file. The skill's own discovery offers "update this or create a new one" on re-run, so answer *update*. The re-run is what makes the invariants persistent facts for Phase 4's story cycle.

**Step 3. `bmad-investigate`** (invoke by name, its catalog row is broken)
- Trigger: `investigate whether the multi-mode correction removal in wip/settings-ui was deliberate, and what depends on rules.py, transliterate.py and terminology_rules.json`
- Input: `git diff main..wip/settings-ui`, `correction/rules.py` (dead: `apply_terminology` iterates `data.rules`, but `RuleData` has no `rules` field since the wip commit rewrote `loader.py`, so it would raise `AttributeError`), `correction/transliterate.py` (127 lines, orphaned, complete), `terminology_rules.json` (20 KB, unloadable because `w1_data._DATASETS` excludes it), `git show main:tests/core/test_transliterate.py` (deleted in the wip commit, recoverable).
- Produces: an evidence-graded finding that settles **D1**.
- Output: `{IA}/mode-system-removal-investigation.md`

**Step 4. `bmad-technical-research`**
- Trigger: `produce a technical research report`
- Phase: 1-analysis
- Input: the questions that gate the whole architecture.
  - Local LLM options on Apple Silicon for Polish, Formal, Street, Prompt Engineer and meeting summarisation: MLX against llama.cpp, quantisation, RAM contention alongside `whisper-large-v3-turbo`. **w1 contains no text generation model today.** Runtime dependencies are `pydantic`, `rapidfuzz`, `jellyfish`, `pyyaml`, `numpy` plus the optional Whisper backends. Every model-driven mode in this plan requires an inference layer that does not exist yet. Treat that as a build, not an integration.
  - Chunked or streaming Whisper decode on MLX: feasibility, chunk boundary handling, and whether it is good enough to serve dictation as well as meetings. This gates **D4**.
  - Degenerate repetition on silence and near-silence: what actually triggers it in `mlx-whisper` and `faster-whisper`, and which of energy or VAD pre-gating, decoder parameters, and post-hoc n-gram repetition detection is the reliable guard. This is an **observed defect in w1 today**, not a hypothetical.
  - macOS system-audio capture: ScreenCaptureKit against CoreAudio process taps, permission surface, PyObjC reachability.
  - Local diarization for speaker labels: pyannote against sherpa-onnx against a channel-split heuristic.
  - WKWebView to Python bridge patterns.
  - Whether "join meeting" can exist without a cloud bot.
- Output: a research document under `{PA}/`.
- **SOR-2 note.** This report is the gate document. For every candidate dependency it must record publish age (must exceed one month), weekly download volume, install-script audit result, and the exact version to pin. **No install happens at this step.**

**Step 5. `bmad-forge-idea`** (core, `anytime`)
- Trigger: `pressure-test this idea`
- Input: the two hardest product questions, stated bluntly.
  1. *w1's differentiator is 100% on-device, and every mode Jay asked for except plain dictation is LLM-dependent.*
  2. *w1 is repositioning from a BAPS terminology tool to a general purpose dictation tool. What is the differentiator once the glossary is a feature rather than the identity?*
- Produces: a hardened position that becomes the PRD's opening constraint and the input to **D3**.
- Output: `{OF}/forge/{slug}/`

**Step 6. `bmad-product-brief`**
- Trigger: `create a product brief`
- Input: Jay's raw request verbatim, the Wispr Flow capability map, the tracker design-system extraction, Steps 1 to 5.
- Produces: `brief.md`
- Output: `{PA}/briefs/brief-w1-{date}/`
- Skip `bmad-prfaq`. It stress-tests a market launch narrative. w1 is a single-operator tool with a known user, so the brief is the right altitude.

### Phase 2: Planning

**Step 7. `bmad-prd`** (create intent)
- Trigger: `create a PRD for w1`
- Phase: 2-planning, **required**
- Input: the brief, the technical research report, the investigation, the Wispr parity scoping table (cloud-hard against locally computable), the raw user input including the full Prompt Engineer system prompt, the Polish / Formal / Street / Meeting / Auto-capture definitions, the language rule (English default, Gujarati and Mixed in the menu, transliteration always with **ā only and no other diacritic**), the summarisation routing to `jay@osx.earth`, `baps.solutions` and `sapio.health`, the Insights screen composition, and the general purpose repositioning.
- Produces: `prd.md`, `addendum.md` (rejected alternatives, options matrices, the local against cloud mechanism decision, personas, sizing) and `.memlog.md`.
- Output: `{PA}/prds/prd-w1-{date}/`
- Pin `project_name = "w1"` for this run so the folder is self-identifying. The tracker run proved `project_name` is supplied ad hoc rather than resolved from config, so folder names are not otherwise a reliable discriminator.
- **What Create actually does at Finalize, so Step 9 does not duplicate it:** step 2 runs input reconciliation and writes `reconcile-{slug}.md` per input, step 3 runs the Reviewer Gate and writes `review-{slug}.md` per reviewer, step 7 sets frontmatter `status: final`. All three effects are already banked when Step 7 closes.

**Step 8. `bmad-ux`**
- Trigger: `lets create UX design`
- Input: `prd.md` plus `addendum.md`, plus the full tracker design-system extraction as a hard constraint (Jay's instruction: *the new UI will be based on tracker.baps.solutions*).
- Produces the peer pair:
  - `DESIGN.md`: the 19 HSL semantic tokens verbatim for `:root` and `.dark` (warm-grey hue 50 dark, not shadcn blue-grey), the `@theme inline` `--color-*` namespace, the radius scale with the deliberate `rounded-xl` passthrough at 12px, Onest plus JetBrains Mono via variable axis with no weight array, the mono-mode weight shift and `-0.045em` tracking, the four glass recipes (`.card-glass`, `.liquid-glass`, `.liquid-glass-pill`, tint and pastel), the 18px dot-grid lattice with cursor spotlight, the `.app-tip` body-singleton tooltip, the arbitrary-px type scale (`text-[13px]` dominant), lucide at 14/16/18/20/22px with the 1.7/1.9/2/2.1/2.2 stroke-width convention, and the Tailwind stock shadow scale pinned to 4.1.4.
  - `EXPERIENCE.md`: the shell IA remapped from tracker's project model to w1's, widget states, mode switching, meeting live-transcript behaviour, permission onboarding, empty and error states, reduced-motion behaviour, keyboard-only operation, and the **new w1.osx.earth identity** (wordmark, favicon, About panel, menu-bar title row).
- Output: `{PA}/ux-designs/ux-w1-{date}/`
- Carry forward the recon's open questions as explicit design calls: retire the `--tracker-*` hex constants (they have no `.dark` override, so `bg-tracker-surface-sunken` renders near-white in dark mode), pick one avatar and priority palette rather than carrying both the v1 and demo-parity registries, and drop the dead `#root { height: 100% }` rule.

**Step 9. `bmad-prd`** (**update** intent, same skill) ← *was validate in the draft, which could not work*
- Trigger: `update the PRD with the UX findings`
- Input: `prd.md`, `addendum.md`, `.memlog.md`, plus `DESIGN.md` and `EXPERIENCE.md` as the change signal.
- **Why Update and not Validate.** `bmad-prd`'s Intent Modes section defines Validate as *"Critique without changing"*. Validate produces `review-{slug}.md` per reviewer plus a synthesis HTML and markdown report, and that is all: it does not edit the document, does not produce `reconcile-{slug}.md`, and does not touch frontmatter `status`. Only Finalize step 7 sets `status: final`, and Finalize runs under Create and Update, never under Validate. Step 7 above already ran the Reviewer Gate and already set `status: final`. So a Validate here would both duplicate work already banked and claim an effect it cannot have, and, more damaging, it would leave **no path at all for UX-discovered gaps to reach the PRD**. That is a live risk: writing `EXPERIENCE.md` against the tracker design system will surface real requirement gaps (mono mode, reduced-motion behaviour, the resizable rail, permission onboarding states, the empty state when retention is set to never-store).
- Produces: an updated `prd.md` and `addendum.md`, a fresh `reconcile-{slug}.md` per input at Finalize step 2, a fresh `review-{slug}.md` per reviewer at Finalize step 3, and `status: final` re-set at Finalize step 7 with `updated` bumped.
- Output: the same `{PA}/prds/prd-w1-{date}/` run folder.
- Run a separate `bmad-prd` **validate** pass afterwards only if an independent critique is wanted for its own sake. It is optional, it changes nothing, and its value is the synthesis report.

### Phase 3: Solutioning

**Step 10. `bmad-architecture`**
- Trigger: `create the architecture`
- Phase: 3-solutioning, **required**
- Input: `prd.md`, `addendum.md`, `DESIGN.md`, `EXPERIENCE.md`, the technical research report, and the existing import-linter contract.
- Produces `ARCHITECTURE-SPINE.md` carrying only invariants. The ones this project actually needs:
  - The **egress boundary**: exactly one module may perform network I/O, and `w1_core` may never import it. Enforced as a new import-linter contract, not by discipline.
  - The **inference adapter boundary**: one Protocol, three implementations (none, local, cloud), with per-mode policy resolved before the adapter is reached. Note this adapter does not exist today in any form.
  - The **diacritic invariant**: every text egress path passes a filter that permits `ā` (U+0101) and no other diacritic, applied **after** any generative stage, not only after the transliterator.
  - The **transcript sanity gate**: a single point through which every decode result passes before it can be inserted, carrying the artifact denylist, the confidence gate and the new degenerate-repetition guard. Today `pipeline.py` has the first two inline and the third not at all.
  - The **storage boundary**: history and stats live behind one store with a three-way retention policy, and nothing else in the app may persist transcripts.
  - The **Vault write boundary**: a path allowlist per destination, a hard denylist on `Secrets/` and any `.env`, and no writes to `~/Desktop/Repositories` or the iCloud archive.
  - The **UI transport boundary**: whatever D2 decides, the Python core exposes one message contract and the shell is a third platform adapter alongside `w1_macos`.
  - The **hot path rule**: plain dictation never touches the inference adapter.
- Output: `{PA}/architecture/architecture-w1-{date}/ARCHITECTURE-SPINE.md` plus `.memlog.md`
- **Then re-run Step 2** (`bmad-generate-project-context`, update path) so these invariants become persistent facts for everything after.

**Step 11. `bmad-spec`** (core, `anytime`)
- Trigger: `create a spec`
- Precondition: `_bmad/custom/bmad-spec.toml` from P3 exists and has been verified with `resolve_customization.py`. Without it this run silently loses every standing rule.
- Input: `ARCHITECTURE-SPINE.md` (adopted as a companion with stable `AD` ids), `prd.md` as a companion, the UX pair as adopted companions.
- Produces: `SPEC.md` with the five-field kernel (Why, Capabilities, Constraints, Non-goals, Success signal) and stable `CAP-N` capability ids that the epics reference, plus spec-authored companions: `glossary.md` for the BAPS terminology contract, `stack.md` for the exact pins, `brownfield.md` for the dead-code disposition, `failure-modes.md` (which is where the degenerate-repetition failure mode is written down formally).
- Output: `{OF}/specs/spec-w1/`
- `SPEC.md` is **derived, never hand-edited**. `bmad-spec` is its single writer and re-renders it from `.memlog.md` on every run.

**Step 12. `bmad-create-epics-and-stories`** ← *the shard step that used to sit here is dropped, see below*
- Trigger: `create the epics and stories list`
- Phase: 3-solutioning, **required**
- Input: at its step-01 "Ask the user if there are any other documents to include for analysis" halt, hand it the absolute paths to `prd.md`, `ARCHITECTURE-SPINE.md`, `SPEC.md`, `DESIGN.md` and `EXPERIENCE.md`. **This manual handoff is mandatory, not optional.** Its automatic discovery will find the UX pair and nothing else.
- Produces: `epics.md`
- Output: `{PA}/epics.md` (a flat file, not a run folder). This flat shape is why the *next* two hops work: `bmad-sprint-planning` and `bmad-create-story` both glob `{PA}/*epic*.md`, and that does match.

> #### Why `bmad-shard-doc` is dropped
>
> The draft used it to manufacture a `{PA}/prd-w1/index.md` so the epics skill's sharded glob would match. Three reasons to drop it, in order of weight:
>
> 1. **SOR-2.** `bmad-shard-doc/SKILL.md` lines 8, 40 and 105 execute `npx @kayvan/markdown-tree-parser explode`, with no version. `npx` fetches and executes an unpinned third-party npm package at run time. This plan asserts no npm or pip install occurs in Phases 1 to 3, and the shard step sat squarely in Phase 3. The assertion and the step could not both be true.
> 2. **It buys nothing that is not already hand-fed.** The step-01 halt is already mandatory for the architecture spine and SPEC.md, which have no working glob and cannot be sharded into one either. Handing over one more path at the same halt costs a line of typing.
> 3. **Its disposal prompt is a trap.** Step 6 of the skill asks what to do with the original and marks **Delete as recommended**, stating *"Keeping both the original and sharded versions defeats the purpose of sharding."* Accepting that deletes `prd.md` from the run folder, which breaks `bmad-prd`'s Create-intent resume scan (On Activation step 5 reads `prd.md` frontmatter `status` to find in-progress runs), breaks the Update intent (which source-extracts against `prd.md`, `addendum.md` and `.memlog.md`), and orphans the memlog derivation model.
>
> **If Jay keeps it anyway,** two answers are non-negotiable and must be given deliberately against the skill's own recommendations:
>
> - **At Step 2, the destination prompt: reject the default.** The default is "same location as source file, folder named after source file without `.md`", which for `{PA}/prds/prd-w1-{date}/prd.md` resolves to `{PA}/prds/prd-w1-{date}/prd/`. That `index.md` sits three levels below `planning_artifacts` and **does not match** `{PA}/*prd*/index.md`, so accepting the default silently fails to deliver the only thing the step exists for. Type `{PA}/prd-w1` explicitly.
> - **At Step 6, the disposal prompt: answer `[k]` keep, not `[d]` delete.** The sharded copy is a discovery shim for one glob. `prd.md` remains the canonical artefact of the run folder and every `bmad-prd` re-entry depends on it. The skill will print a warning about keeping both. Accept the warning.
> - And run the SOR-2 gate on `@kayvan/markdown-tree-parser` in Step 4's report first, then invoke it pinned as `npx @kayvan/markdown-tree-parser@<exact-version>`.
>
> The same destination caveat applies if the architecture spine is ever sharded.

**Step 13. `bmad-check-implementation-readiness`**
- Trigger: `check implementation readiness`
- Phase: 3-solutioning, **required**
- Input: PRD, UX pair, architecture spine, epics.
- Produces: a readiness report. **Treat a fail here as a hard stop, not advisory.** Add four project-specific checks to the run:
  1. Every epic touching text output references the ā-only invariant.
  2. Every epic touching network references the egress boundary.
  3. Every epic touching decode results references the transcript sanity gate.
  4. Every epic depending on a signed build names E3 as a dependency.
- Output: a readiness report under `{IA}/`

### Phase 4: Implementation

**Step 14. `bmad-sprint-planning`**
- Trigger: `run sprint planning`
- Phase: 4-implementation, **required**
- Input: `{PA}/epics.md`
- Produces: `sprint-status.yaml`
- Output: `{IA}/sprint-status.yaml`
- **Worktree note.** This file is shared mutable state across a parallel fleet. Update it on the integration branch only, never inside an epic worktree, or every merge fights over it.

**Step 15. The story cycle, repeated per story, one worktree per epic (SOR-1).**

| Order | Skill | Trigger | Consumes | Produces |
|---|---|---|---|---|
| a | `bmad-create-story` (create) | `create the next story` | `sprint-status.yaml`, `epics.md`, spine, `SPEC.md` | `{IA}/{story_key}.md`, for example `4-3-glass-materials.md` |
| b | `bmad-create-story` (validate) | `create story [id]`, then the validate action | the story file | a validated story file in place |
| c | `bmad-dev-story` | `dev this story [story file]` | the story file | code in an epic worktree, tests, **no commit without Jay's approval** |
| d | `bmad-code-review` | `run code review` | the diff | triaged findings. Issues route back to c |
| e | `bmad-qa-generate-e2e-tests` | `create qa automated tests for [feature]` | a shipped feature | end-to-end tests, scoped as below |
| f | `bmad-checkpoint-preview` | `checkpoint` | the epic's accumulated diff | a human-review walkthrough before the PR gate |
| g | `bmad-retrospective` | `run a retrospective` | the completed epic | lessons, feeding `bmad-correct-course` if scope moved |

**Step 15e is retargeted.** The draft pointed `bmad-qa-generate-e2e-tests` at "the golden corpora". That is the wrong instrument: the skill's own frontmatter and its `bmad-help.csv` row scope it to *"Generate automated API and E2E tests for implemented code. NOT for code review or story validation"*, and its role line says *"You generate tests ONLY."* A frozen correction-fixture corpus is not an E2E suite, it is a pytest fixture, and it belongs in E1 (see below). Point this skill instead at:

- the dictation loop end to end, from synthetic hotkey press to text landing in a target field;
- the insertion long-tail targets from E5 (IDEs, terminals, remote desktops, browser address bars, notification reply boxes);
- the **zero-network-egress assertion** on the local-only path from D3, which is the single most valuable automated test in this project;
- the Vault write denylist from E11, proving `Secrets/` and `.env` are unreachable;
- the signed-bundle smoke test from E3, proving the global key listener still receives events after signing.

**Sidecars, invoked as needed:**
- `bmad-sprint-status`, trigger `check sprint status`, for state across parallel worktrees.
- `bmad-correct-course`, trigger `correct course`, whenever a decision point reopens mid-sprint. D3 and D5 are the likely ones.
- `bmad-quick-dev`, reserved strictly for out-of-band fixes not in the sprint. Never used to bypass the story cycle for planned epic work.
- `bmad-review-edge-case-hunter` on four surfaces specifically: the correction chain, the diacritic filter, the transcript sanity gate, and the Vault write path. It is method-driven and orthogonal to `bmad-code-review`'s adversarial layers, so both are worth running there.
- `bmad-advanced-elicitation` (pre-mortem, red team) on the summarisation routing design before it is built.
- `bmad-agent-tech-writer` at the end of each epic to update `docs/`, and critically to correct `web/`, `README.md` and `ui/index.html`, which currently advertise four deleted modes and a BAPS-only identity to the public internet.
- `bmad-index-docs` once on `docs/` after the rebrand, so the superseded documents are visibly marked as such.

---

## 2. Epic breakdown

**UI** = presentation work against an existing or trivially-derived data source. **Engine** = new or substantially reworked `w1_core` or `w1_macos` capability. **Infra** = build, signing, CI, distribution, relocation.

The **Depends on** column is the ordering contract. Row order is a reading order, not a dependency order.

| # | Epic | Type | Depends on | Scope, and the specific things that make it non-trivial |
|---|---|---|---|---|
| **E1** | Repo truth reset, boundary hardening, CI and test fixtures | Engine (existing) + Infra | none. Blocks everything | Resolve **D1** and act: delete `rules.py` and `terminology_rules.json`, or rewire them. Fix `ingest_glossary_pdf.py` and `sync_rules_from_ts.py`, both of which hardcode `~/Desktop/Repositories/Mandir`, a path the workspace ground truth marks never-write, which means neither script can currently regenerate its own data (**D9**). Create the `.github/` CI that `PLAN.md` promised: headless core-only install, `lint-imports`, pytest, coverage gate. **Populate the empty `tests/data/` with pytest fixtures**, not E2E tests: the frozen 20-sentence golden set, the pure-English do-not-corrupt corpus that `PLAN.md` §8 makes a release gate, and a new silence and near-silence corpus (room tone, breath, clipped starts) that the degenerate-repetition guard in E5 is measured against. Clean the `.venv_old_w4k/`, `build/` and `.import_linter_cache/` w4k residue, and the `.coverage 2` and `web/vite.config 2.ts` duplicates currently sitting untracked in the tree. |
| **E2a** | Rebrand and relocation: identity and moves | Infra | E1 (or run as precondition P1, see **D14**) | Move the repo from `baps.solutions/w1.baps.solutions` to `osx.earth/w1.osx.earth` in the Vault, move the GitHub remote from the `bkt-baps-solutions` org to `osx-earth`, and update `~/Vault/index.md`. Rename the product surface: bundle id `health.baps.w1` becomes an `osx.earth`-namespaced id (which **invalidates every existing TCC grant**, so the first-run permission flow from E3 must handle a fresh grant cycle, and this is a real user-visible consequence, not a rename). Rewrite `README.md`: it currently opens with a Devanagari wordmark, points at `w1.baps.solutions`, and frames the product as "its one specialism: it knows BAPS Gujarati terminology". The new framing is general purpose dictation with the glossary as one capability. Update `install.sh` and the install instructions. Repoint `docs/PACKAGING.md`. |
| **E2b** | Rebrand: public website redesign | UI | E2a, E4 | Redesign and redeploy the `web/` marketing site on the ported design system at `w1.osx.earth`. The current site advertises four deleted modes and promises "nothing is stored", both of which are false today. The truthful two-tier storage and egress statement from **D3** and **D6** lands here, and this epic cannot ship before those are settled. Retire the `w1.baps.solutions` domain or redirect it. |
| **E3** | Signing, notarization, entitlements and permissions foundation | Infra | E1. **Blocked on a Developer ID certificate, see the box below** | Developer ID Application signing, `xcrun notarytool` submission, stapling. `packaging/build.sh:46` currently greps the keychain for the first `"Apple Development"` identity: that must change to select a **Developer ID Application** identity, and fail loudly rather than fall back to ad-hoc, because ad-hoc signing silently kills the global key listener (commit `9efd0ef` exists precisely because of that). `packaging/w1.entitlements` **already** grants what the hardened runtime needs for MLX (`allow-jit`, `allow-unsigned-executable-memory`, `disable-library-validation`) plus `device.audio-input`, so the entitlements work in this epic is **adding the system-audio capture entitlement for E9**, not re-deriving the MLX ones. Build the first-run permission wizard with re-check gating, covering microphone, accessibility, input monitoring and system audio. Add a signed-bundle smoke test asserting the key listener still receives events, run at every epic's PR gate rather than only at release. **This epic exists separately from E14 specifically so that the signed build and the new entitlements are validated before meeting capture ships, not after.** |
| **E4** | Design system port and app shell | **UI only** | E1, **D2** | Port tracker's `globals.css` wholesale: 19 tokens, the `@theme inline` namespace, the radius scale with the `rounded-xl` passthrough, the four glass recipes, the dot-grid lattice, the `.app-tip` singleton, mono mode with its weight shift, the reduced-motion neutraliser. Port the 13 shadcn primitives. **Port only the material and layout half of the 16-file `view/` primitive layer** (see the scoping note below). Adapt the three-column shell: sidebar (Home, History, Dictionary, Snippets, Modes, Meetings, Insights, Settings), opaque `rounded-3xl` content panel, resizable glass right rail. Two ports that are not copy-paste: tracker's dark mode is cookie-driven SSR under Next 15 and becomes localStorage plus the same synchronous boot script in a static build; and Tailwind must be pinned to **exactly 4.1.4**, because no shadow tokens are defined, so a minor bump silently drifts the shadow rendering. |
| **E5** | Dictation core hardening, sanity gate and latency instrumentation | Engine (hardening) | E1 | Keep the working pipeline: `transcribe_and_correct`, the artifact denylist, the confidence gate, the mask, fuzzy, unmask chain, clipboard paste with restore, the AX `editable_target()` conservative fallback, the paste panel. Add: Esc cancel; target-field tracking across app switches; insertion long-tail fixes (IDEs, terminals, remote desktops, browser address bars, notification reply boxes); the **degenerate-repetition guard** (see the box below); and latency instrumentation against the criterion **D4** sets. Remove any session cap: an on-device product has no per-request cost, which is a real differentiator over Wispr's 20-minute stop. If **D4** selects streaming, the chunked decoder is built here and E9 consumes it rather than the other way round. |
| **E6** | Local history and stats store | **Engine (new)** | E1, **D6** | The precondition for E12, and the epic where the zero-storage promise is formally renegotiated. Three-way retention policy: store, auto-delete every 24 hours, never store. Capture at insert time: word count, duration, WPM, corrections applied split into word-corrections and dictionary-fixes, target app bundle id mapped to a category (AI prompts, work messages, personal messages, emails, documents, other), mode used. Single writer, single reader, everything else goes through it. |
| **E7** | Mode system | **Engine (new)** + UI | E1, E5, **D1**, **D3** | Five modes. **Formal** and **Street** are largely deterministic and can extend the existing `cleanup.py` plus a new punctuation and capitalisation stage: Formal punctuates, capitalises and lightly formalises; Street keeps colloquialisms and suppresses capitalisation entirely. **Polish** (Opt+1) and **Prompt Engineer** are generative and require the inference adapter, which **does not exist in the codebase in any form today**, so this epic contains a from-scratch inference layer, not an integration. Prompt Engineer carries a fixed multi-section system prompt: Title, Role and stance, Task, Context, Inputs available, Output requirements, Constraints, Examples, Execution checklist, Conflict resolution. Plus the selection-based Transforms path: read highlighted text via AX, rewrite, offer a diff view before replacing. Plain dictation remains a mode that never reaches the adapter. |
| **E8** | Language menu, transliteration revival and the ā-only egress invariant | **Engine (part revival)** | E1, **D12** | English default; Gujarati and Mixed in the menu. Revive `transliterate.py`, whose 40-line test is recoverable via `git show main:tests/core/test_transliterate.py`. Restore Whisper `language="gu"` routing, which went away with `CorrectionMode.gujarati` and its `resolved_language()` method. Enforce the **ā-only** invariant as a filter on every egress path, including generative-mode output, backed by a property test that fuzzes generated text. **Explicitly out of scope here:** any Gujarati accuracy programme, model tuning, decoder work or evaluation harness. That is E15, later. This epic delivers the menu, the routing, the transliterator and the invariant, and nothing about how well Gujarati is recognised. |
| **E9** | Meeting mode: local dual-stream capture and live transcript | **Engine (new)** + UI | **E3** (signed build with the system-audio entitlement), E4, E5, **D3**, **D5** | Dual-stream capture: microphone plus system audio via ScreenCaptureKit or a CoreAudio process tap, which requires a **new macOS permission** and therefore hard-depends on E3 having shipped a signed build with the entitlement and the wizard. Live incremental transcript, which means chunked or streaming decode rather than the current record-then-transcribe loop, a genuine change to `controller.py`. Speaker labels via either local diarization or the cheap and surprisingly effective channel-split heuristic (mic stream is Jay, system stream is everyone else), with the heuristic as the shipping default and diarization behind **D3**. New live transcript surface in the shell. Persistent consent notice. |
| **E10** | Auto-capture meeting detection and Vault destination routing | Engine + integrations | E9, **D5** | Detect the active meeting by browser and app (Chrome, Edge, Brave for Meet; the Zoom client; the Teams client) and by calendar. Arm capture contextually. Ask for, or infer, the Vault destination folder at capture time. Naming follows **D5**: on the recommended answer this is "auto-capture", not "join". |
| **E11** | Post-meeting summarisation, Vault write-back and task generation | **Engine (new)** + integrations | E7 (inference adapter), E10, **D3**, **D7** | Route by destination: `jay@osx.earth`, `baps.solutions`, `sapio.health`. For each, read existing Vault context so the summary is contextualised rather than generic, update the relevant notes in place, and generate tasks. Needs a long-context model, so this is the sharpest point of **D3**. Needs the Vault write contract from the spine: a path allowlist per destination, a hard denylist on `Secrets/` and `.env` **with a test proving it**, tasks landing in an inbox for one-click promotion rather than direct insertion. The `sapio.health` destination inherits a stricter policy than the other two. |
| **E12** | Insights analytics surface | **UI only** (given E6) | E4, E6, **D8** | Rebuild the screenshotted screen on the ported material: a WPM radial gauge with `useCountUp`, a corrections tile split into words-corrected and dictionary-fixes, cumulative total words with a month-over-month badge, a horizontal app-category bar chart with light, moderate and power intensity bands, and a GitHub-style contribution heatmap with current and longest streak. Omit the global percentile and the leaderboard per **D8**. Add a graceful empty state when retention is set to never-store. |
| **E13** | Dictionary, snippets and glossary management | UI + light engine | E4, E6 | Surface the 201-entry glossary, the 948-entry master glossary, the 20 protected terms and the 74 bias-seed terms that already exist and are currently invisible to the user. Add auto-learning from typed corrections, misspelling replacement rules, and voice-triggered snippet expansion. In the general purpose framing this is the epic where a *user's own* vocabulary matters at least as much as the BAPS one, so build the management UI vocabulary-agnostic and ship the BAPS glossary as a preloaded pack. Not named in Jay's original request, but it is a large part of what makes Wispr feel useable. **Mark as the parity backlog epic, cut first if scope pressure arrives.** |
| **E14** | Distribution | Infra | E3, E2b, and every shipping epic | The notarized DMG, the install path, the update channel, and the documentation correction sweep. `docs/PACKAGING.md` still says "ship the unsigned .app" while `build.sh` always signs. This is the epic that puts a build on someone else's Mac, so it inherits E3's certificate prerequisite in full. |
| **E15** | Gujarati accuracy programme | **Engine (new)**, LATER | E8, plus Jay supplying training material | **Placeholder. Not near-term scope, not in the first sprint plan, not in the readiness gate.** Jay will supply transliterated text plus matched audio. When that arrives, this epic covers building the evaluation harness with a held-out set, establishing a WER and term-accuracy baseline on real Gujarati and mixed speech, and only then choosing between prompt and bias tuning, decoder parameter work, and fine-tuning. Nothing about this epic is designed now beyond leaving the seam: E8's language routing and the ā-only invariant are the interfaces it will attach to. Keep it in `epics.md` so it is visible and explicitly deferred, rather than absent and later mistaken for an oversight. |

**Summary by type.** UI-only: E2b, E4, E12, and the surfacing half of E13. New engine work: E6, E7, E9, E10, E11, E15, plus the revival half of E8. Existing engine hardening: E1, E5. Infrastructure: E2a, E3, E14.

> ### Blocking prerequisite on E3 and E14: a Developer ID Application certificate
>
> `security find-identity -v -p codesigning` on Jay's machine returns exactly one identity:
>
> ```
> 1) 1D62461FD1B6383A9428C6FA0EEE54A08E6A2FC4 "Apple Development: jayhpateluk@icloud.com (WALY2J97BF)"
>    1 valid identities found
> ```
>
> An **Apple Development** certificate signs builds that run on machines registered to that development team. **It cannot sign a build that will run on anyone else's Mac.** Distribution to testers requires a **Developer ID Application** certificate, and that certificate can only be issued to a member of the **paid Apple Developer Program**. Notarization via `xcrun notarytool` likewise requires that membership.
>
> Consequences, stated plainly so they are not discovered late:
>
> - **E3 cannot complete and E14 cannot start** until the membership exists and the certificate is in the keychain. Every downstream epic that depends on a signed build (E9 above all) inherits the block.
> - `packaging/build.sh:46` currently greps for `"Apple Development"` and falls back to leaving the ad-hoc signature in place. Both behaviours are wrong for distribution: it must select a `Developer ID Application` identity and **fail loudly** if none is found, because a silent ad-hoc fallback produces a bundle whose global key listener receives no events, which is the exact failure commit `9efd0ef` was written to fix.
> - `packaging/w1.entitlements` is **not** part of this problem. It already carries `com.apple.security.cs.allow-jit`, `allow-unsigned-executable-memory` and `disable-library-validation`, which is what MLX needs to JIT and `dlopen` Metal libraries under the hardened runtime, plus `com.apple.security.device.audio-input`. The only entitlement work E3 adds is system audio for E9.
> - Until the certificate exists, w1 is buildable and runnable on Jay's own machine only. That is a fine state for E1 through E8, and a hard wall for E9 onward. Settle **D13** early.

> ### Scoping note on E4: which tracker primitives are ported and which are dropped
>
> The draft said "port the 13 shadcn primitives and the 16-file `view/` primitive layer". Roughly half the `view/` layer encodes project-tracking domain concepts that are meaningless in a dictation tool, and porting them wholesale drags in the two competing colour registries the recon flagged as an open question.
>
> **Ported (material and layout primitives):** `tile.tsx`, `kpi-card.tsx` (with `useCountUp`), `empty-state.tsx`, `section-label.tsx`, `tint-badge.tsx`, `pastel-pill.tsx`, `progress-bar.tsx` (with its `clampPct` export), `user-avatar.tsx`. Plus the glass, tint and dot-grid recipes from `globals.css` and the 13 shadcn primitives.
>
> **Dropped, not ported:** `stage-badge.tsx`, `priority-pill.tsx`, `priority-dot.tsx`, `blocked-pill.tsx`, `urgency-chip.tsx`, `project-filter-chips.tsx`, `avatar-stack.tsx`, `sort-select.tsx`. All eight encode project-tracking semantics (stages, priorities, blockers, urgency, multi-assignee, project filtering) that w1 has no equivalent of. Dropping them also removes the reason to carry both the v1 and demo-parity colour registries: port whichever single registry the retained primitives need and delete the other.
>
> If a later epic genuinely needs one of the dropped shapes, port it then, against a real requirement.

> ### Degenerate repetition on silence: the guard, and where it lives
>
> This is an **observed defect in w1 today**, not a risk. Whisper decoding near-silence or clipped audio emits degenerate loops such as the same phrase repeated dozens of times. The existing defence in `pipeline.py` does not catch it:
>
> - `_ARTIFACTS` is a hardcoded 9-item **exact-match** set (`""`, `"."`, `"you"`, `"thank you."`, `"thanks for watching!"`, `"[blank_audio]"` and so on). `"thank you. thank you. thank you. thank you."` matches none of them.
> - `_is_low_confidence` averages `no_speech_prob` and `avg_logprob` across segments, and a confidently-decoded degenerate loop scores well on both. It also **never gates when `raw.segments` is empty**, which is exactly the shape some backends return on pathological input.
>
> The guard lands in **E5**, behind the spine's **transcript sanity gate** invariant so it sits in one place rather than being sprinkled through the controller. Three layers, cheapest first:
>
> 1. **Pre-decode.** An energy or VAD check on the captured buffer before the backend is invoked at all. If there is no speech, do not decode. This also saves the whole decode cost on an accidental hotkey press.
> 2. **Post-decode structural.** An n-gram repetition detector on the decoded text: if any token or short phrase n-gram accounts for more than a threshold share of the output, or repeats beyond a threshold count, gate the result with a new `gated_reason="repetition"` alongside the existing `"artifact"` and `"low_confidence"`.
> 3. **Normalised artifact matching.** Fold the exact-match `_ARTIFACTS` check into a case-folded, punctuation-stripped, whitespace-collapsed comparison, and apply it to the deduplicated form of the output so a repeated artifact still matches the single-instance entry.
>
> Thresholds are set empirically against the silence and near-silence fixture corpus added in **E1**, not guessed. `bmad-review-edge-case-hunter` runs on this surface. The failure mode is written into `failure-modes.md` at Step 11 so it is part of the spec contract, not folklore.

---

## 3. Decision points Jay must settle

### D0. BMAD scoping and the shape of a second install. Blocks Step 1.

- **(a)** Run from the Vault root. All w1 output collides with tracker's finalized PRD in one `_bmad-output` tree. Zero setup.
- **(b)** A second `npx bmad-method@6.9.0 install` inside the w1 repo, giving it a project-local `_bmad/` and `_bmad-output/`.
- **(c)** Override `output_folder` in `_bmad/custom/config.toml`. That is a team-wide, committed file, so it would repoint tracker's output too.

**Recommendation: (b),** but only with all four of the following specified up front. The draft recommended (b) and left them open, which is not a decision, it is a deferral.

1. **Version and SOR-2.** Re-install the identical pinned `bmad-method@6.9.0`. That exact version passed the SOR-2 gate on 2026-07-27 (no pre or post-install scripts, 17k weekly downloads, exact-pinned), so this is a no-cost repeat of a cleared decision rather than a new dependency admission. Do **not** take a newer version without re-running the gate.

2. **Project-root resolution, which is the part that actually breaks.** `resolve_config.py` requires its `--project-root` argument to be a path containing a `_bmad/` directory. After a second install, two such paths exist. Every skill activation resolves config and customization through these scripts, so an ambiguous or defaulted project root silently sends output to the wrong tree. **Rule: always pass `--project-root` explicitly and absolutely**, as `/Users/jaypatel/Vault/osx.earth/w1.osx.earth` (or the pre-move path if D14 goes the other way). Never rely on cwd inference.

3. **Skill name resolution when two sets are visible.** The installer materialises 46 skill directories into `.claude/skills/bmad-*`. After a second install, `bmad-prd` exists both at `/Users/jaypatel/Vault/.claude/skills/bmad-prd` and inside the w1 repo. **Which one a session picks is not documented anywhere in this install, and this plan does not assert a rule it has not observed.** Before Step 1 runs, verify empirically: from inside the w1 directory, invoke `bmad-help` once and confirm which skill root it reports and which `{project-root}` it resolves. If the two sets turn out to be indistinguishable in practice, fall back to **(c) scoped differently**: keep the single Vault-root install and add per-project overrides, accepting the shared tree. Do not proceed on an assumption here; one invocation settles it.

4. **The gitignore decision.** The w1 repo is live, tracked, and currently clean apart from three untracked paths. A second install adds `_bmad/`, `.claude/skills/` (46 vendored directories) and later `_bmad-output/`. Decide once:
   - **Commit `_bmad/`.** It is small, and `_bmad/custom/bmad-spec.toml` from P3 is load-bearing configuration that must travel with the repo. Note `_bmad/custom/.gitignore` already excludes `*.user.toml`, so personal overrides stay out automatically.
   - **Commit `_bmad-output/`.** The planning artefacts, the spec package and the `.memlog.md` files are the deliverable trail and the resume mechanism. Losing them loses the ability to resume any run.
   - **Gitignore `.claude/skills/bmad-*`.** 46 directories of vendored third-party skill text, fully regenerable by re-running the pinned installer. Record the exact install command in `README.md` or `docs/` so regeneration is a documented one-liner.
   - Add the ignore entry and the `_bmad/` addition in **one commit, asked for explicitly**, before Step 1. Parallel Claude sessions may be active on this repo.

Reject **(c)** as the primary answer: it silently repoints an unrelated project's output.

### D1. Is the multi-mode removal deliberate? Blocks E1 and E7.

- **(a)** Treat the removal as canonical. Delete `rules.py` and `terminology_rules.json`. Build the new modes fresh on the inference adapter.
- **(b)** Revert to `main`'s rule-based mode system and extend it.

**Recommendation: (a), with one carve-out.** The new mode set (Prompt Engineer, Polish, Formal, Street) is generative rewriting, not regex substitution, so the 64 terminology rules serve none of it, and the current engine's explicit no-substitution contract ("temple" stays "temple") is a correctness guarantee worth keeping, and one that matters more in the general purpose framing, not less. The carve-out: `transliterate.py` is complete, was tested, and is the repo's only Gujarati-script-to-Roman capability. Revive it under E8 with its recovered test rather than deleting it with the rest.

### D2. Shell technology. Blocks E4 and every UI epic.

- **(a)** Stay pure Python and PyObjC, build the hub as native AppKit. No reuse of tracker at all: 19 tokens, four glass materials, a dot lattice, a radial gauge and a contribution heatmap all hand-ported to AppKit. High cost, poor fidelity on exactly the surfaces Jay screenshotted.
- **(b)** Keep the Python core and macOS adapter, add an embedded WKWebView hosting a Vite plus React 19 plus Tailwind 4.1.4 static build of the tracker design system, bridged via `WKScriptMessageHandler`.
- **(c)** Tauri v2 shell with the Python core as a sidecar. Best web reuse, but adds a Rust toolchain, sidecar packaging, a second signing surface, and forces re-plumbing of pynput, the AX layer and ScreenCaptureKit across IPC.
- **(d)** Electron. Heaviest resident footprint for an always-on menu-bar app.

**Recommendation: (b).** All of w1's actual value is in `w1_core` plus the macOS AX, hotkey and inject layer, all working today, and the existing import-linter contract already treats platform code as a swappable adapter. A WKWebView is a third adapter, not a rewrite. Two adjustments the port needs: tracker is Next.js with cookie-driven SSR dark mode, so the static build swaps the cookie for localStorage while keeping the identical synchronous boot script; and the floating widget stays a native `NSPanel` regardless, because a webview cannot be click-through, non-activating, screensaver-level and joined to all Spaces. Revisit **(c)** only if E9's live transcript proves too heavy over the bridge.

### D3. Local model against any cloud call. The headline decision. Blocks E7, E9 and E11.

- **(a)** 100% on-device, local inference only. Preserves the promise absolutely. Costs quality on Prompt Engineer and meeting summarisation, adds RAM contention alongside `whisper-large-v3-turbo`, and adds cold-start latency to Polish.
- **(b)** Local by default, with per-mode and per-destination opt-in to a cloud model, a non-defeatable visible indicator while any cloud call is in flight, and an audit log.
- **(c)** Cloud for everything, Wispr's model.

**Recommendation: (b), with a hard, code-enforced split.**

- **Local only, permanently, no cloud path reachable in code:** dictation, the correction chain, the transcript sanity gate, Formal, Street, transliteration, and meeting transcription.
- **Local by default with explicit opt-in, off until enabled:** Polish, Prompt Engineer, meeting summarisation.

Reject **(c)**: it destroys the only differentiator over an app that is better funded and faster, and makes the tool unusable in any clinical context. Reject **(a)** as the sole option only because meeting summarisation over a long transcript with Vault context is where local models are genuinely weak, and Jay should have a switch rather than a silently degraded feature.

Two conditions attach. First, the boundary must be an architecture invariant enforced by an import-linter contract and an automated egress test, not by convention. Second, E2b must rewrite the Settings footer and the deployed marketing site from "nothing is stored" to a truthful two-tier statement, because the current copy is already false about four modes that no longer exist.

### D4. The latency criterion for dictation. Blocks E5's release criteria.

The draft set "a hard p99 gate from key-release to text-inserted, benchmarked against Wispr's published 700ms". **That criterion is unattainable by construction and the comparison is not like-for-like.** Two facts:

- w1 is **record-then-transcribe**. `controller.py` buffers the entire utterance in a `sounddevice` callback, and only on `stop_recording` does `_process` call `transcribe_and_correct` once. End-to-end time therefore scales with utterance length: a thirty-second dictation cannot finish in the same wall time as a three-second one, so no single fixed p99 from key release to insertion can be met.
- Wispr's sub-700ms figure is a **streamed cloud pipeline**, verified at the infrastructure source: ASR models plus fine-tuned Llama transcript enhancement served on TensorRT-LLM, with decode overlapping speech. It is not a record-then-transcribe number. `PLAN.md`'s Phase 2 live streaming insertion was never built.

Options:

- **(a)** Keep a fixed p99 from key release to insertion. Rejected: not achievable while the pipeline is record-then-transcribe, so the gate would either be met by only permitting short utterances or quietly ignored.
- **(b)** Express the criterion as **real-time factor plus fixed overhead**. Two numbers, both measurable: a decode RTF ceiling (decode wall time divided by audio duration), measured on a fixed corpus at a fixed model and backend; and a **fixed post-decode budget** covering the correction chain, the diacritic filter, the sanity gate, the clipboard swap, the paste and the clipboard restore, which does not scale with utterance length and therefore *is* a legitimate p99 gate.
- **(c)** Move chunked or streaming decode from E9 forward into E5 so dictation streams too, at which point a fixed time-to-first-token and a fixed tail-after-key-release both become meaningful.

**Decision: (b) now, with (c) as the named follow-on.** Adopt RTF plus fixed overhead as E5's release criterion immediately, because it can be measured on the pipeline that exists. Set both numbers from a **baseline measured in E5 on the current build**, not copied from Wispr: the criterion is "no regression against the measured baseline, and the fixed post-decode budget holds at p99". Then, when Step 4's research confirms chunked MLX decode is viable, build the chunked decoder **in E5** rather than E9, so dictation and meetings share one decoder and E9 consumes it. At that point, and only then, revisit whether a Wispr-comparable time-to-first-insertion is a fair gate.

Pair this with the spine's **hot path rule**: plain dictation never touches the inference adapter, so adding modes cannot regress it. Polish and Prompt Engineer get a "visible progress, never blocking, always cancellable" contract instead of a latency number. Meeting summarisation is explicitly asynchronous and backgrounded.

### D5. What "join meeting" actually means. Blocks E10.

- **(a)** A real bot participant joining via the Teams, Google and Zoom APIs. Requires cloud infrastructure, three OAuth integrations, and routes meeting audio through a third party.
- **(b)** Local system-audio capture with calendar awareness and no participant joining, which is Wispr Notetaker's model.
- **(c)** A locally driven headless browser that joins Google Meet from Jay's own machine.

**Recommendation: (b), and rename the mode.** Call it "auto-capture meeting", not "join meeting", so the product does not overclaim. **(a)** directly contradicts everything D3 protects. **(c)** is technically possible for Meet only, but raises consent and platform terms-of-service problems, and in any NHS or clinical setting recording others may be prohibited outright. If Jay genuinely needs capture of meetings he is not personally in, that is a separate later decision, not part of this build.

### D6. The zero-storage promise against history and Insights. Blocks E6 and E12.

- **(a)** Keep zero storage and drop Insights entirely.
- **(b)** Adopt a three-way local policy: store, auto-delete every 24 hours, never store. Insights degrades gracefully.
- **(c)** Always store.

**Recommendation: (b), defaulting to store-locally-only with no cloud sync ever.** This is the one place Wispr is a useful precedent rather than a foil: its transcript history is genuinely local by default and is not synced unless explicitly enabled. Add a single **clinical mode** preset that flips retention to never-store and disables every cloud tier from D3 in one switch, so the app can be hard-locked before a shift rather than relying on six separate toggles being right.

### D7. Vault write authority. Blocks E11.

- **(a)** w1 writes summaries and tasks directly into `~/Vault`.
- **(b)** w1 writes only into a staging inbox for review.
- **(c)** Tasks go through tracker's API rather than the filesystem.

**Recommendation: a hybrid.** Summaries write directly into a per-destination allowlisted folder, since a summary that needs manual filing is a summary that never gets filed. Generated tasks land in an inbox for one-click promotion, since a wrong task is worse than a missing one. Both paths sit behind a hard denylist on `Secrets/` and `.env` enforced in code with a test proving it, and never write to `~/Desktop/Repositories` or the iCloud archive. Defer **(c)** until tracker exposes a stable task API.

### D8. Percentile and leaderboard in Insights. Blocks E12.

- **(a)** Show a global percentile, which requires population data w1 does not have and cannot get without a server.
- **(b)** Omit it.
- **(c)** Replace it with a self-referential comparison.

**Recommendation: (c).** Wispr's "Top 0.2%" and the whole Leaderboard tab are a growth loop for a multi-tenant SaaS with an account system. w1 has one user and no account. Replace the percentile with a rolling personal baseline (this week against your 30-day median), keep the streak, keep the "you have written one book chapter" milestone framing since that needs no external data, and drop the leaderboard and the social share carousel entirely.

### D9. Glossary source of truth. Blocks E1.

- **(a)** Locate Mandir's new home in the Vault and re-point both ingestion scripts.
- **(b)** Freeze `master_glossary.json` as vendored data with a checksum test and retire the scripts.

**Recommendation: (a) if Mandir is findable in the Vault, otherwise (b).** Either way the hardcoded `~/Desktop/Repositories/Mandir` paths must go before E1 closes, because the workspace ground truth marks that location historical and never-write, which means neither script can currently regenerate its own data. In the general purpose framing, (b) is more attractive than it was: the BAPS glossary becomes a vendored, versioned **pack** shipped alongside a user-editable dictionary, rather than a live pipeline from another repo.

### D10. Dependency additions, all SOR-2 gated.

No install happens before Step 4's technical research report delivers, for each candidate: publish age (must exceed one month), weekly download volume, install-script audit, and the exact version to pin. Candidates this project will need:

- a local inference runtime (`mlx-lm` or `llama-cpp-python`), which is a **new capability**, since w1 today has no text generation model of any kind;
- possibly a diarization package, though the zero-dependency channel-split heuristic is preferred first;
- the web build chain pinned to tracker's exact versions: `tailwindcss` 4.1.4, `@tailwindcss/postcss` 4.1.4, `lucide-react` 0.468.0, `class-variance-authority` 0.7.1, `tailwind-merge` 3.5.0, the six Radix packages, plus Vite and React 19;
- `@kayvan/markdown-tree-parser` **only if** `bmad-shard-doc` is retained against the recommendation in Step 12.

Prefer native ScreenCaptureKit through PyObjC over any new capture dependency. Existing runtime pins stay exact and unchanged: pydantic 2.13.4, rapidfuzz 3.14.5, jellyfish 1.2.1, pyyaml 6.0.3, numpy 2.4.6.

### D11. The branch base for the worktree fleet. Blocks E1 and the entire SOR-1 fleet.

Fifteen epic worktrees cannot be cut from an ambiguous base, and this was left in the draft as a passing note rather than a decision.

**The current state, verified:**

```
  main                           9efd0ef  build: codesign .app with a real identity outside iCloud (fix key listener)
* wip/settings-ui                be59260  wip(rescue): settings UI, login item, master glossary + ingestion, macos tests, app icon
  remotes/origin/main            9efd0ef
  remotes/origin/wip/settings-ui be59260
```

Both branches are in sync with origin. `wip/settings-ui` is one commit ahead of `main`, and that single commit is a 34-file change carrying the entire multi-mode removal, the settings window, the login item, the 948-term master glossary with its ingestion script, macOS tests and the app icon, all together. The working tree is clean apart from `.coverage 2`, `web/vite.config 2.ts` and `docs/v2/`.

- **(a)** Fast-forward `main` to `be59260` and cut every worktree from `main`.
- **(b)** Keep `wip/settings-ui` as the integration branch and cut every worktree from it.
- **(c)** Split the 34-file wip commit into reviewable pieces before merging, then take (a).

**Recommendation: (a), conditional on D1 resolving to "the removal is deliberate".** This whole plan already treats the wip state as canonical: E1 acts on the removal, E8 revives `transliterate.py` from the wip tree, the recon inventory describes the wip tree. Leaving `main` a commit behind while every worktree branches from a branch named `wip/` is a naming lie that will cause a mistake later. Since `main` is one commit behind and the branches are in sync with origin, the merge is a fast-forward with no conflict surface at all.

Reject **(b)**: fifteen worktrees rooted on a branch named `wip` invites someone, including a future Claude session, to treat it as disposable. Reject **(c)** on cost: splitting a landed 34-file commit is archaeology with no consumer, since the investigation at Step 3 already produces the evidence-graded account of what that commit did, and that account is the artefact worth having.

**Order of operations, and every step needs explicit approval before it runs:** settle D1 at Step 3 → fast-forward `main` → push `main` → delete or archive `wip/settings-ui` → cut worktrees from `main`, one per epic, named `epic/<n>-<slug>`. Nothing here happens without Jay saying so.

### D12. Mixed language strategy. Blocks E8.

Promoted out of an epic row, because it materially changes E8's scope and touches the ā-only egress invariant.

- **(a)** Single-pass Gujarati decode plus transliteration for the whole utterance. Simple, matches how the removed `CorrectionMode.gujarati` worked, and matches the Wispr precedent: Wispr detects language once per session and **cannot alternate mid-sentence**.
- **(b)** Segment-level language detection, decoding each segment in its detected language and transliterating only the Gujarati ones. Handles genuine code-switching, but multiplies the decode cost, introduces boundary artefacts at every switch, and gives the degenerate-repetition guard a much harder job because short segments are exactly where Whisper degenerates.
- **(c)** Ship the menu with English and Gujarati only, and defer Mixed until E15 has real training material and a real evaluation harness.

**Recommendation: (c) for near-term, with (a) as the shape when Mixed does ship.** Given that Gujarati accuracy work is explicitly deferred, building segment-level detection now means tuning a code-switching pipeline with no evaluation set to tune against, which is exactly the failure mode E15 exists to avoid. Ship the menu with the Mixed entry present but marked as coming later, or absent, at Jay's preference. When it ships, do **(a)**: one language per utterance, transliterate the whole result, one egress filter pass. Whichever is chosen, the ā-only invariant applies to the final text and nothing upstream of it is permitted to emit another diacritic.

### D13. Apple Developer Program membership. Blocks E3 and E14.

- **(a)** Enrol in the paid Apple Developer Program as an individual, obtain a Developer ID Application certificate, sign and notarize.
- **(b)** Enrol as an organization. Requires a legal entity and a D-U-N-S number, and takes longer to clear, but the signing identity carries the entity name rather than a personal name, which matters if w1 is ever distributed publicly under the `osx.earth` identity.
- **(c)** Do not enrol. Distribute the unsigned or Apple Development-signed build with manual Gatekeeper override instructions.

**Recommendation: (a) now, revisit (b) only if w1 is ever distributed publicly at scale.** Reject **(c)** outright for anything leaving Jay's machine: an ad-hoc or development-signed bundle asks every recipient to bypass Gatekeeper, and, worse for this specific app, ad-hoc signing silently breaks the global key listener, which means the recipient's build appears installed and simply does not respond to the hotkey. That is the failure that produced commit `9efd0ef`. Until D13 resolves, **E9 through E14 are all blocked**, so this is worth settling early rather than at packaging time.

### D14. Rebrand sequencing. Blocks P1 and therefore every path in this document.

- **(a)** Perform the Vault folder move, the GitHub org move and the remote rename **before** the second BMAD install and before Step 1, as precondition P1.
- **(b)** Treat the move as epic E2a, executed mid-fleet.

**Recommendation: (a).** Every skill activation passes an absolute `--project-root`, every run folder path in this plan is absolute, and `.memlog.md` files record absolute paths as part of the run's canonical memory. Moving the repo after the ceremony has started invalidates all of that and forces a rewrite of the artefact trail, which is exactly the kind of churn `.memlog.md` was designed to make unnecessary. The move itself is mechanical: a directory move, a `git remote set-url`, a GitHub org transfer, an `~/Vault/index.md` edit. Do it first, then install BMAD in the final location, then run Step 1 against a path that never changes.

E2a then keeps everything that is *not* the physical move: the bundle identifier change and its TCC consequence, the README rewrite, the install instructions, `docs/PACKAGING.md`, and the in-app identity. Those are real work and belong in an epic. The `mv` does not.

**If (b) is chosen anyway,** schedule E2a immediately after E1 and before any other worktree is cut, and accept that every absolute path in the planning artefacts must be rewritten at that point.

---

## 4. Risks and how the workflow de-risks them

**R1 (headline). The on-device promise against inference-dependent modes.** Every mode except plain dictation is a rewriting task, and Wispr's own documentation is blunt that this is why it is cloud-only. Meanwhile w1's Settings footer and marketing site both promise nothing leaves the device, and there is no inference layer in the codebase at all today. De-risked by: Step 4 answering local-model feasibility **before** the PRD is written; Step 5 forging the tension explicitly; D3 splitting the modes into a permanently-local set and an opt-in set; the spine making that split an import-linter-enforced invariant; a `bmad-qa-generate-e2e-tests` run asserting zero network egress from the local-only path; and E2b correcting copy that is already false.

**R2. Scope explosion.** Wispr has roughly 25 distinct features and this plan has fifteen epics. De-risked by the `bmad-check-implementation-readiness` gate at Step 13, by E13 being explicitly labelled the cut-first backlog epic, by E15 being explicitly deferred rather than quietly carried, and by the parity scoping table being carried into the PRD so "not building this" is written down rather than assumed.

**R3. Building from stale specs.** `PLAN.md`, `docs/UI-PLAN.md`, `docs/base44-ui-prompt.md`, `ui/index.html`, `README.md` and the deployed `web/` site all describe a four-mode, BAPS-identity product that does not exist, and `docs/UI-PLAN.md` makes two false claims about `settings_window.py`. De-risked by `bmad-document-project` running first, by the PRD explicitly declaring those documents superseded, and by `bmad-index-docs` marking them as such in `docs/`.

**R4. BMAD's own install defects.** Output collision at the Vault root, the epics skill unable to discover the PRD or the architecture, `bmad-investigate` unroutable, and `bmad-spec` unable to load `project-context.md`. De-risked by D0 with all four sub-answers pinned, by P3's `_bmad/custom/bmad-spec.toml` override verified with `resolve_customization.py` before Step 11, by the hand-feed at Step 12's step-01 halt being mandatory, and by invoking `bmad-investigate` by name.

**R5. The standing rules never reaching the planning runs.** `persistent_facts` load once at activation. In the draft's ordering, `bmad-prd`, `bmad-architecture` and `bmad-spec` all ran before `project-context.md` existed, so every standing rule was absent from every planning run while Section 5 claimed the opposite. De-risked by moving `bmad-generate-project-context` to Step 2 and re-running it after Step 10, and by the P3 override making `bmad-spec` actually able to read it.

**R6. The diacritic invariant leaking through generative modes.** A local model will happily emit `é`, `ṇ` or other diacritics. De-risked by making the ā-only filter an egress-path invariant in the spine so it applies **after** any generative stage, and by a property test in E8 that fuzzes generated output.

**R7. Degenerate repetition reaching the user's document.** Already observed. The existing exact-match denylist and averaged-confidence gate both miss it, and the confidence gate does not fire at all when `raw.segments` is empty. De-risked by the transcript sanity gate invariant in the spine, the three-layer guard in E5, the silence corpus fixture in E1, `failure-modes.md` recording it at Step 11, and `bmad-review-edge-case-hunter` running on that surface.

**R8. macOS permission and packaging regression, and the certificate wall.** Ad-hoc signing silently kills the global key listener, proven by commit `9efd0ef`. E9 introduces a brand new system-audio permission. The rebrand changes the bundle identifier, which invalidates every existing TCC grant. And no distributable build is possible at all until D13 resolves. De-risked by E3 existing as a separate epic ahead of E9 rather than as a trailing packaging step, by the signed-bundle smoke test running at every epic's PR gate, by E2a owning the bundle-id consequence explicitly, and by D13 being surfaced now rather than at packaging time.

**R9. Latency regression on the hot path.** Adding mode dispatch in front of insertion is the obvious way to slow down the one thing that already works. De-risked by D4's RTF-plus-fixed-overhead criterion (which is measurable on the pipeline that exists, unlike the draft's fixed p99), the spine's hot-path invariant, and the baseline measurement in E5 being a named release criterion in the readiness check.

**R10. Parallel Claude sessions clobbering work.** De-risked by SOR-1's worktree-per-epic model with PR gates, by D11 settling a single unambiguous base first, by `bmad-sprint-status` as the cross-worktree state view, by keeping `sprint-status.yaml` mutations on the integration branch only, and by the ask-before-commit rule below.

**R11. Consent and legality of meeting capture.** Recording others, especially in NHS contexts, is not universally permissible. De-risked by D5 choosing the no-bot model, a persistent consent notice during capture, and the `sapio.health` destination inheriting a stricter never-store, never-cloud policy by default.

**R12. Memory contention on Apple Silicon.** `whisper-large-v3-turbo` plus a 7-8B model plus optional diarization on one machine, while the app is menu-bar resident. De-risked by Step 4 producing an explicit memory budget, and by that budget becoming an invariant in the architecture spine so model choices in E7, E9 and E11 are constrained rather than renegotiated per epic.

**R13. Rebranding mid-flight.** Moving repo, org, domain, bundle id and product framing at the same time as a large build is how absolute paths, TCC grants and artefact trails all break at once. De-risked by D14 recommending the physical move be done first, before anything depends on the path, and by E2a owning the consequences that follow rather than the move itself.

---

## 5. How the standing rules are baked in

**SOR-1 (plan, orchestrate, code, QA, parallel fleet).** The plan phase is Steps 1 to 13. Orchestration is Step 14's `sprint-status.yaml`. Code is `bmad-dev-story`. QA is `bmad-code-review` plus `bmad-qa-generate-e2e-tests` (retargeted per Step 15e) plus `bmad-review-edge-case-hunter` on the four highest-risk surfaces. The parallel fleet runs one git worktree per epic, each gated by a PR, with `bmad-checkpoint-preview` as the human review before the gate and `bmad-retrospective` after the merge. **E1 must land on its own before any fleet fans out**, because it changes the test and CI substrate everything else builds on, and **D11 must be settled before the first worktree is cut**.

**SOR-2 (dependency security gate).** No npm or pip install occurs anywhere in Phases 1 to 3, and that statement is now true, because `bmad-shard-doc` and its unpinned `npx @kayvan/markdown-tree-parser` have been dropped from Step 12. If Jay reinstates that step, the package goes through the gate in Step 4's report first and is invoked with an exact version. Step 4's report is the gate document for every other candidate: publish age over one month, weekly download volume, install-script audit, exact version to pin. D0's BMAD re-install is a repeat of an already-cleared decision on the identical pinned version, `bmad-method@6.9.0`. The web build chain is pinned to tracker's exact versions rather than a range, specifically because no shadow tokens are defined, so a Tailwind minor bump would silently change the rendering.

**Conventional Commits.** Encoded in `project-context.md` at Step 2, so every `bmad-dev-story` run inherits it from activation.

**Ask before any commit, push or branch operation.** Encoded in `project-context.md` and restated in every story file. `bmad-dev-story` produces code in a worktree and stops. The `_bmad/` and `.gitignore` commit from D0, the fast-forward and push from D11, the branch deletion of `wip/settings-ui`, every worktree creation, every commit and every push each require Jay's explicit go-ahead, because parallel sessions may be active on the same repo. The rebrand move in D14 likewise: the remote change and org transfer are asked for, not assumed.

**Exact pins.** Already the pattern in `pyproject.toml`: pydantic 2.13.4, rapidfuzz 3.14.5, jellyfish 1.2.1, pyyaml 6.0.3, numpy 2.4.6, with the optional extras pinned the same way (mlx-whisper 0.4.3, faster-whisper 1.2.1, rumps 0.4.0, pynput 1.8.2, sounddevice 0.5.5, pyperclip 1.11.0, py2app 0.28.10). Extended to the new web chain and to any inference runtime.

**Never touch `Secrets/` or `.env`. No PHI or PII in logs or test data.** Enforced three times over: as a persistent fact in `project-context.md` from Step 2, as a denylist in the Vault write boundary invariant in the architecture spine, and as an automated test in E11 that proves the denylist holds. Current corpora are synthetic and stay that way.

**No time estimates.** None appear in this plan. `project-context.md` carries the rule forward so no generated story, epic or sprint artefact introduces one. The latency figures in D4 and E5 are performance criteria measured against a baseline, not schedule estimates, and the RTF criterion is deliberately expressed as a ratio so it cannot be mistaken for one.

**No em-dashes.** Carried in `project-context.md` so every generated document inherits it. This document uses commas, colons and full stops throughout.
