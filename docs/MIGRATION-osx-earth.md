# Migration runbook: w1.baps.solutions to w1.osx.earth

Moving w1 from a BAPS-branded product to a general purpose personal dictation tool under
`osx.earth`. The BAPS glossary stays as a shipped capability; only the identity moves.

**Nothing in this document has been executed.** It is a plan. Per the workspace standing rule,
ask before any commit, push, branch operation, file move or DNS change.

## Contents

1. [Ground truth as verified](#1-ground-truth-as-verified)
2. [Identity changes: the file:line checklist](#2-identity-changes-the-fileline-checklist)
3. [Do not touch: BAPS feature references](#3-do-not-touch-baps-feature-references)
4. [The GitHub move](#4-the-github-move)
5. [The Vault folder move](#5-the-vault-folder-move)
6. [DNS and Vercel](#6-dns-and-vercel)
7. [The bundle identifier question](#7-the-bundle-identifier-question)
8. [Suggested order of operations](#8-suggested-order-of-operations)
9. [Rollback plan](#9-rollback-plan)

---

## 1. Ground truth as verified

Checked on disk before writing this runbook:

| Fact | Value |
|---|---|
| Actual git remote | `https://github.com/bkt-baps-solutions/w1.baps.solutions.git` |
| Current branch | `wip/settings-ui` (also `main`; both pushed) |
| Bundle identifier | `health.baps.w1` |
| LaunchAgent label | `solutions.baps.w1.login` |
| Vercel link on disk | `web/.vercel/project.json`, projectName `web`, org `deployment-sapio-health` |
| Vercel link status | **dead**; that projectId returns 404 and the team's only project is `jp-life-os` |
| Version | 1.1.0 |

Two things worth flagging up front, because they change the shape of the work:

- **The `jp-sapio-health` URLs in the repo are already broken.** `README.md:26` and
  `web/src/App.tsx:27` point at an org the repo does not live in. The site's "GitHub" link and
  "View source" button 404 for everyone today, independent of this rebrand.
- **The Vercel project no longer exists.** There is no deployment to migrate and no traffic to
  preserve. The rebrand can claim a fresh project name at zero cost.

---

## 2. Identity changes: the file:line checklist

30 lines across 11 tracked text files, plus one binary asset and two stale build-output copies.

### 2.1 Web app, highest visibility

- [ ] `web/src/App.tsx:27` `const REPO = "https://github.com/jp-sapio-health/w1.baps.solutions"` becomes the `osx-earth` URL
- [ ] `web/src/App.tsx:29-30` code comment naming the Sapio design system and "the BAPS logo + W1 wordmark in place of the Sapio mark"
- [ ] `web/src/App.tsx:45` navbar `<img src="/baps-logo.svg" alt="BAPS" />` becomes the new mark
- [ ] `web/src/App.tsx:48` wordmark `<span className="nav-sub">.baps.solutions</span>` becomes `.osx.earth`
- [ ] `web/src/App.tsx:74` "Corrects BAPS Gujarati sacred terms to their canonical spelling" is the borderline case: it describes real behaviour, so it may survive as a feature description in a vocabulary section, but not as a top-level mode identity
- [ ] `web/src/App.tsx:118` hero lede "English and BAPS Gujarati sacred terms, fully on-device"
- [ ] `web/src/App.tsx:225` About tab "knows BAPS Gujarati sacred terminology"
- [ ] `web/src/App.tsx:227` tagline "Built for sewa. Private by design."
- [ ] `web/src/App.tsx:293` footer `<img src="/baps-logo.svg" alt="BAPS" />`
- [ ] `web/src/App.tsx:296` tagline, second occurrence
- [ ] `web/index.html:9` meta description "English + BAPS Gujarati sacred terms, fully on-device."
- [ ] `web/index.html:11` favicon `href="/baps-logo.svg"`
- [ ] `web/src/index.css:23` comment "Sapio design-system neutrals"
- [ ] `web/public/baps-logo.svg` delete and replace with a new monochrome `currentColor` mark
- [ ] `web/dist/index.html:11` and `web/dist/baps-logo.svg` stale build output; simplest fix is `rm -rf web/dist` and rebuild

Two content decisions to make while in here, both flagged by the audit:

- The site sells "Four modes, one keypress" while the newer README says "One mode". The site is
  describing a superseded product model. Pick one story.
- "Download for macOS" only raises a toast with no link. Make it a real link to Releases.

### 2.2 Package and app identity

- [ ] `pyproject.toml:11` description "Local, privacy-first bilingual dictation that replaces Wispr Flow, English + BAPS Gujarati sacred terms, fully on-device." This is publicly distributed metadata, so it is identity even though it reads as a feature.
- [ ] `packaging/setup_app.py:56` `"CFBundleIdentifier": "health.baps.w1"` see [section 7](#7-the-bundle-identifier-question) before changing
- [ ] `packaging/build.sh:58` `--identifier health.baps.w1` **must stay byte-identical to setup_app.py:56 or codesigning breaks**
- [ ] `src/w1_macos/login_item.py:13` `_LABEL = "solutions.baps.w1.login"` see [section 7](#7-the-bundle-identifier-question)
- [ ] `docs/PACKAGING.md:11` and `docs/PACKAGING.md:70` both document `health.baps.w1`; :70 is the paragraph explaining why the identifier must be stable

Note the two schemes are already inconsistent: `health.baps.w1` versus `solutions.baps.w1.login`.
If they change, unify them.

### 2.3 Documentation

- [ ] `README.md` replace wholesale from `README.new.md` (already drafted). Lines carrying identity: `:1` the `वाणी · W1` lockup, `:5` `w1.baps.solutions`, `:12` "its one specialism", `:26` the wrong-org clone URL
- [ ] `docs/base44-ui-prompt.md` lines 13, 18, 28, 45, 54, 78. Line 28 asks for a Devanagari `वाणी` lockup; line 78 is the sewa tagline
- [ ] `docs/UI-PLAN.md:3` "the W1/वाणी companion UI"
- [ ] `PLAN.md` lines 6, 17, 19, 20, 166, 268, 287, 306. Strategy document, ships in no artifact, so lowest priority

**On the Devanagari wordmark.** Remove it. It was already dropped from the website in commit
`3c7e0fc` but survives in the README and design docs. Beyond the identity argument, it was in
the wrong script: the Gujarati is **વાણી**, not the Devanagari **वाणी**. A mark meant to signal
care about the language signalled the opposite. If a script nod is wanted later, use Gujarati
**વાણી** as a label inside the Gujarati language mode, where it is correct and scoped.

### 2.4 The `ui/` prototype

`ui/index.html` is a 290-line self-contained saffron-themed prototype, superseded by the
darwin-ui site. It carries 13 identity hits at lines 147, 154, 155, 183, 209, 210, 211, 220,
238, 251, 253, 286, 287, including a fake demo row "Investor update, Sapio seed" that leaks the
other brand.

- [ ] **Recommended: delete `ui/` entirely.** It is dead weight and removing it clears 13 hits at
  a stroke. If it is kept for reference, it must be rebranded like everything else.

### 2.5 Dead weight, safe to drop in the same pass

- [ ] `web/public/fonts/` 367 KB of Ubuntu Sans Mono that the site never loads; there is no `@font-face` and the site uses Inter from the Google CDN. Git-tracked. Leftover from `ui/`
- [ ] `ui/fonts/` duplicate copy of the same
- [ ] `web/vite.config 2.ts` and `.coverage 2` iCloud conflict duplicates, untracked
- [ ] `.venv_old_w4k/` from the pre-w1 naming era
- [ ] `web/.vercel/project.json` stale dead link, gitignored

### 2.6 Broken paths worth fixing while in here

Not branding, but they are broken today and the same commit can fix them:

- [ ] `scripts/ingest_glossary_pdf.py:22` hardcodes `/Users/jaypatel/Desktop/Repositories/Mandir/NEW INFORMATION MASTER THE MOST `
- [ ] `src/w1_data/_meta.json:2` records source `/Users/jaypatel/Desktop/Repositories/Mandir/web/lib/rules`
- [ ] `scripts/sync_rules_from_ts.py:32-33` computes `_REPOS = _HERE.parents[2]` then `DEFAULT_SRC = _REPOS / "Mandir" / "web" / "lib" / "rules"`. Under the Vault layout this resolves to a path that does not exist, and after the folder move it will resolve somewhere different again

Both the PDF ingestion and the one-way TS to JSON sync are non-functional today. The folder move
in [section 5](#5-the-vault-folder-move) changes what `parents[2]` means, so if these are not
fixed they break differently rather than getting worse.

---

## 3. Do not touch: BAPS feature references

Roughly 960 matches across 13 files are the glossary feature, its data provenance, or engine
documentation. **These survive the rebrand unchanged.** Rewriting them would either break the
ingestion contract or falsify attribution.

| Path | What it is |
|---|---|
| `src/w1_data/master_glossary.json` | 948 entries each stamped `"source": "Master Glossary (BAPS)"`. Attribution to the source PDF. **Never rewrite.** |
| `src/w1_data/glossary.json` | 201 entries; BAPS named in three definitions at :246, :290, :741 |
| `src/w1_data/bias_seed.json:19` | "sewa" as a decoding bias term |
| `src/w1_data/__init__.py:1,17` | data-module docstrings |
| `src/w1_core/correction/loader.py:40` | comment explaining the master glossary's role |
| `src/w1_core/correction/engine.py:7` | docstring describing what the engine does |
| `src/w1_core/correction/transliterate.py:3,8` | "House Rules §2.2 (BAPS): keep the long-a macron ā". A named orthographic rule |
| `scripts/ingest_glossary_pdf.py:1,103` | ingestion docstrings |
| `scripts/sync_rules_from_ts.py:5` | sync docstring |
| `tests/core/test_master_glossary.py:1` | test docstring |
| `tests/core/test_correction.py:4` | test docstring |
| `README.md:74` | glossary source section; carried into `README.new.md` |

The framing to hold throughout: **BAPS was the hardest test, not the target market.** Move BAPS
from identity slots (wordmark, favicon, meta description, hero, package description, tagline)
into feature slots (vocabulary section, glossary docs, mode descriptions).

---

## 4. The GitHub move

**Current:** `bkt-baps-solutions/w1.baps.solutions`
**Target:** `osx-earth/w1.osx.earth`

This is two operations: a transfer between orgs, and a rename. Do them as separate steps so each
is independently reversible.

### 4.1 Preconditions

```bash
gh auth status                                   # confirm the account
gh api /orgs/osx-earth -q .login                 # confirm the target org exists and is visible
gh repo view bkt-baps-solutions/w1.baps.solutions --json name,visibility,isPrivate
gh api repos/bkt-baps-solutions/w1.baps.solutions/issues --paginate -q 'length'   # issue count
```

Push all local work first. `wip/settings-ui` is the working branch and is already pushed;
confirm nothing is unpushed before transferring, since a transfer while you hold local-only
commits is recoverable but confusing.

### 4.2 Transfer, then rename

The GitHub API has no single "transfer and rename" call. Transfer first:

```bash
gh api -X POST repos/bkt-baps-solutions/w1.baps.solutions/transfer \
  -f new_owner=osx-earth
```

Then rename in the new org:

```bash
gh api -X PATCH repos/osx-earth/w1.baps.solutions \
  -f name=w1.osx.earth
```

Web equivalent: **Settings ▸ General ▸ Danger Zone ▸ Transfer ownership**, then
**Settings ▸ General ▸ Repository name**.

You need admin on the source repo and repo-creation rights in `osx-earth`. If `gh` lacks the
scope, run `gh auth refresh -h github.com -s admin:org`.

### 4.3 What is preserved automatically

A transfer carries everything: **full git history, all branches and tags, issues, pull requests,
labels, milestones, wiki, releases, stars and watchers**. There is nothing to export or
re-import. Issues do not need preserving by hand; that is the point of using transfer rather
than creating a fresh repo and pushing.

Two things do **not** carry:

- **Actions secrets and variables** are not transferred. There are none in this repo (no
  `.github/` directory exists), so nothing to do.
- **Org-level settings** such as branch protection rules inherited from org defaults are
  re-evaluated against the new org.

### 4.4 What happens to existing clones

GitHub sets up a **redirect** from the old path to the new one, for both the transfer and the
rename. Existing clones keep working: `git fetch` and `git push` against
`bkt-baps-solutions/w1.baps.solutions` follow the redirect, and git prints a warning telling you
the remote moved.

The redirect is not permanent in one important sense: **it breaks the moment anything new is
created at the old path.** If a repo named `w1.baps.solutions` is later created in
`bkt-baps-solutions`, every old clone silently starts talking to the wrong repository. So treat
the redirect as a grace period, not a permanent alias.

Update local remotes explicitly:

```bash
git remote set-url origin https://github.com/osx-earth/w1.osx.earth.git
git remote -v                                    # verify
git fetch origin                                 # confirm it resolves
```

Do this in every clone, including any worktrees and the parked copies under `_inbox/`.

---

## 5. The Vault folder move

**From:** `~/Vault/baps.solutions/w1.baps.solutions`
**To:** `~/Vault/osx.earth/w1.osx.earth`

`~/Vault/osx.earth/` already exists and holds the other personal projects
(`jay.osx.earth`, `annie.osx.earth`, `life-os`, `transcribe`, and others), so the destination
convention is established.

```bash
git -C ~/Vault/baps.solutions/w1.baps.solutions status --porcelain   # must be clean-ish first
mv ~/Vault/baps.solutions/w1.baps.solutions ~/Vault/osx.earth/w1.osx.earth
```

### 5.1 What else in the Vault references the old path

Verified by grep across `~/Vault`, excluding `.git`, `node_modules` and `.venv`:

| File | Reference |
|---|---|
| `~/Vault/index.md:27` | table row `` `w1.baps.solutions` `` under the BAPS domain. Move the row to the osx.earth section and rename |
| `~/Vault/CLAUDE.md:37` | "w1 canonical copy: `baps.solutions/w1.baps.solutions`" in Known state |
| `~/Vault/PATHS.md:46` | lists `w1.baps.solutions (CANONICAL w1)` alongside tracker and parsec under baps.solutions |
| `~/Vault/PATHS.md:86` | migration table row mapping the old `~/Desktop/Repositories/W1` locations to `~/Vault/baps.solutions/w1.baps.solutions` |
| `~/Vault/PATHS.md:26,28` | `_inbox` entries for `w1-home` and `w1-developer-cli.patch`. Path text only; leave the parked copies alone until an off-disk backup exists |
| `~/Vault/_platform/finalize-claude-migration.sh` | contains the old path string. Check whether it is still live before editing |

Claude session transcripts under `~/Vault/_platform/claude/projects/` and `history.jsonl` also
contain the old path. **Leave them alone.** They are an append-only historical record; rewriting
them would falsify history and they are not read as configuration.

### 5.2 In-repo path assumptions that the move affects

`scripts/sync_rules_from_ts.py:32-33` derives a sibling-repo path from `__file__` via
`parents[2]`. After the move it points into `~/Vault/osx.earth/` instead of
`~/Vault/baps.solutions/`, so the Mandir rules source, which lives in the BAPS domain, gets
further away. Since the script is already broken (see [2.6](#26-broken-paths-worth-fixing-while-in-here)),
fix it with an explicit configurable path rather than a relative walk.

Nothing else in the repo hardcodes its own location: `src/w1_macos/paths.py` resolves assets
from `__file__` relative to the package, and `w1` and `install.sh` both resolve `$DIR` from
`BASH_SOURCE`. The `.venv` will contain absolute paths from the editable install and should be
rebuilt after the move (`rm -rf .venv && ./install.sh`).

---

## 6. DNS and Vercel

### 6.1 The Vercel side

There is nothing to migrate. `web/.vercel/project.json` points at projectId
`prj_3Kpdc6nGJg3jL5HE39Ak2Bu1THB0` in team `deployment-sapio-health`, and that project returns
404. No `vercel.json`, no CI, no deploy script, and both `.vercel/` and `dist/` are gitignored,
so no deployment configuration is versioned at all.

- [ ] Delete the stale `web/.vercel/` directory
- [ ] Create a fresh Vercel project. Name it `w1-osx-earth`, not the directory-default `web` that
      the dead link inherited
- [ ] Decide the team. The dead link was under a Sapio team; a personal tool belongs under a
      personal scope. Choose deliberately rather than accepting the CLI's `currentTeam`
- [ ] Set the root directory to `web/`, framework Vite, build `vite build`, output `dist`
- [ ] Connect it to the transferred GitHub repo so pushes deploy

### 6.2 DNS

Add `w1.osx.earth` as a domain on the new Vercel project, then create the record at whichever
registrar or DNS provider holds `osx.earth`, following the values Vercel shows. For a subdomain
that is normally a `CNAME` to `cname.vercel-dns.com`.

Verify before announcing:

```bash
dig +short w1.osx.earth
curl -sI https://w1.osx.earth | head -1
```

### 6.3 Redirect from the old domain

**Recommendation: do not bother.**

`w1.baps.solutions` has no live deployment behind it, so there is no working URL to redirect
from. Anyone with the old link is already getting nothing. Setting up a redirect would mean
standing up new infrastructure on a BAPS domain purely to point away from itself, which is more
work than telling the handful of existing testers directly.

The audience is "early users and testers, real people on their own Macs", a group small enough to
message. Do that instead.

**If a redirect is wanted anyway** (for example if `w1.baps.solutions` DNS still resolves
somewhere and you want no dead link): the cheapest form is a tiny Vercel project on the
`baps.solutions` domain with a `vercel.json` containing a permanent redirect:

```json
{
  "redirects": [
    { "source": "/(.*)", "destination": "https://w1.osx.earth/$1", "permanent": true }
  ]
}
```

Keep it for a defined window, then retire the subdomain. A permanent redirect is cached
aggressively by browsers, so use `"permanent": false` if you might want the subdomain back.

- [ ] Check what `w1.baps.solutions` currently resolves to before deciding
- [ ] Remove the `w1` DNS record from `baps.solutions` once the redirect window closes

---

## 7. The bundle identifier question

**This is the highest-consequence decision in the migration. It is the one thing here that can
degrade the experience of people already running w1.**

### 7.1 Current state

| Where | Value |
|---|---|
| `packaging/setup_app.py:56` | `CFBundleIdentifier` = `health.baps.w1` |
| `packaging/build.sh:58` | `codesign --identifier health.baps.w1` |
| `src/w1_macos/login_item.py:13` | `_LABEL` = `solutions.baps.w1.login` |
| `docs/PACKAGING.md:11,70` | documents `health.baps.w1` and why it must be stable |

`docs/PACKAGING.md:70` states the constraint plainly: *"A stable bundle identifier
(`health.baps.w1`) matters here: macOS keys granted permissions to the bundle ID, so re-signed
rebuilds keep their grants."*

### 7.2 Does changing it break existing users' permissions?

**Yes.** macOS TCC keys authorisation records to the app's code identity, principally the bundle
identifier together with the code signing identity. Change the bundle identifier and the new
build is, as far as TCC is concerned, a different application with no history.

Concretely, every existing user of `health.baps.w1` would have to re-grant:

- **Microphone.** Re-prompts automatically on first use, so this one self-heals with a click.
- **Accessibility.** Does **not** re-prompt usefully. The user must open System Settings and add
  the app manually. Until they do, w1 transcribes and then silently fails to paste.
- **Input Monitoring.** Same. Until granted, the app launches, appears healthy, and never
  responds to the hotkey. `README.md` and `docs/PACKAGING.md` both call this out as the confusing
  failure mode.

The two silent failures are the problem. A user who updates and finds nothing happens when they
hold Right-Option has no signal telling them why.

Additionally, the stale entries for the old identifier linger in the TCC database, so the
Privacy panes will show two `w1` entries, which is its own support burden.

The LaunchAgent label is a smaller but real version of the same issue.
`~/Library/LaunchAgents/solutions.baps.w1.login.plist` is written by `login_item.set_enabled()`.
Renaming `_LABEL` orphans that file: the old agent stays loaded and keeps launching
`/Applications/W1.app` at login, while `is_enabled()` reports false because it looks for the new
filename. The user gets a launch-at-login they cannot turn off from Settings.

### 7.3 Recommendation

**Change the bundle identifier, and do it now, in this migration.** Then never change it again.

Reasoning:

1. **The blast radius is at its smallest today.** Distribution is "early users and testers", and
   the current build is not even notarized, so it has been hand-delivered. That population is
   messageable. Every month of adoption makes this more expensive.
2. **`health.baps.w1` is wrong in two ways.** It names the wrong domain and it is inconsistent
   with `solutions.baps.w1.login`. Carrying a misleading reverse-DNS identifier forever, in the
   one string that must never change, to avoid a one-time cost paid by a handful of testers, is
   the wrong trade.
3. **There is a real forcing function coming.** Moving to a Developer ID certificate for
   notarization (a pending task) changes the signing identity anyway, which is itself a TCC
   identity change for some grant types. Better to take both disruptions in one release than in
   two.

Proposed values, unified under one scheme:

| Setting | New value |
|---|---|
| `CFBundleIdentifier` | `earth.osx.w1` |
| `codesign --identifier` | `earth.osx.w1` (must match exactly) |
| LaunchAgent `_LABEL` | `earth.osx.w1.login` |

**If you would rather not.** Keeping `health.baps.w1` is defensible and costs nothing technically.
The app is `w1` to the user; the identifier is invisible. Choose this only as a deliberate
decision, and record it in `docs/PACKAGING.md` so a future pass does not "tidy" the string and
break everyone.

### 7.4 If changing it, do these too

- [ ] Change `setup_app.py:56` and `build.sh:58` **in the same commit**. They must be byte-identical or the signature will not verify
- [ ] Update `docs/PACKAGING.md:11,70`
- [ ] Add a **migration shim to `login_item.py`**: on startup, if
      `~/Library/LaunchAgents/solutions.baps.w1.login.plist` exists, `launchctl unload -w` it and
      unlink it before installing the new label. Without this, orphaned agents persist. This is
      the one code change the rename actually requires
- [ ] Update `_APP` in `login_item.py` if the app bundle name changes from `W1.app`. If the
      wordmark becomes lowercase `w1`, decide whether the bundle is `w1.app` or stays `W1.app`,
      and keep `CFBundleName`, `build.sh`'s output path, and `_APP` consistent. Note macOS is
      case-insensitive by default here but the LaunchAgent path string is not forgiving if the
      bundle is genuinely renamed
- [ ] `tests/macos/test_login_item.py` exercises this module; check whether it asserts the label
- [ ] **Write release notes that lead with the re-grant step**, naming Accessibility and Input
      Monitoring specifically and describing the symptom (app runs, hotkey does nothing) so
      testers self-diagnose
- [ ] Tell testers to remove the old entries from the Privacy panes to avoid duplicate rows

---

## 8. Suggested order of operations

Each step is independently reversible, and the risky ones come last.

1. **Content and docs first, in the current repo.** Replace `README.md` from `README.new.md`,
   rebrand the web app, delete `ui/`, delete the dead fonts, fix the wrong-org URLs. Commit.
   Nothing external has moved, so this is pure text and fully revertible.
2. **New brand mark.** Produce the monochrome `currentColor` glyph, wire it into navbar, footer
   and favicon, delete `baps-logo.svg`, delete `web/dist/`.
3. **GitHub transfer, then rename.** Update `origin` in every clone.
4. **Vault folder move.** Update `index.md`, `CLAUDE.md`, `PATHS.md`. Rebuild `.venv`.
5. **Vercel project and DNS.** Verify `https://w1.osx.earth` serves before announcing.
6. **Bundle identifier, as its own release.** With the `login_item.py` shim, the release notes,
   and a direct message to testers. Do not bundle this with anything else, so that if permission
   problems appear the cause is unambiguous.

Verify after steps 1 to 4:

```bash
grep -rniE "baps\.solutions|jp-sapio-health|वाणी|Built for sewa" \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=dist .
```

Expected remaining hits: only the [section 3](#3-do-not-touch-baps-feature-references) feature
references, which contain `BAPS` but not `baps.solutions`. A hit on `baps.solutions`,
`jp-sapio-health`, the Devanagari lockup or the sewa tagline after step 4 is a miss.

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/lint-imports
./w1 doctor
```

---

## 9. Rollback plan

### Per step

| Step | How to undo |
|---|---|
| **1 and 2, content** | `git revert` the commits, or reset the branch if unpushed. Keep the new mark's source file so a redo is cheap |
| **3, GitHub** | Transfer and rename are both reversible. Rename back via `gh api -X PATCH repos/osx-earth/w1.osx.earth -f name=w1.baps.solutions`, then transfer back to `bkt-baps-solutions`. History, issues and PRs survive both directions. **Caveat:** the reverse redirect only works if nothing new has been created at the intermediate path, so do not create anything at `osx-earth/w1.osx.earth` if a rollback is still plausible |
| **4, folder move** | `mv` it back and revert the three Vault doc edits. Rebuild `.venv` again |
| **5, Vercel and DNS** | Delete the new project and remove the DNS record. Nothing was live at the old address, so there is no service to restore. Allow for DNS TTL |
| **6, bundle id** | See below |

### Rolling back the bundle identifier

This is the only step that cannot be cleanly undone, because **the damage is on users' machines,
not in the repo.**

Reverting `setup_app.py`, `build.sh` and `login_item.py` and shipping a build with the old
identifier restores the *old* TCC grants, which are still in the database. So a user who never
re-granted goes back to working. But a user who **did** re-grant under the new identifier now has
to grant a third time, and both identifiers are left sitting in their Privacy panes.

Practical consequences:

- **Decide before shipping, not after.** Once a build with a new identifier is in testers' hands,
  reverting costs more than continuing.
- If a rollback is genuinely needed, ship it fast, before most testers have re-granted, and say
  explicitly in the notes that the old permissions apply again.
- Keep the `login_item.py` shim in place through a rollback, and extend it to clean up the new
  label too, so no orphaned agent survives in either direction.

### Keeping a rollback possible

- [ ] Tag the pre-migration state: `git tag pre-osx-earth-migration` before step 1
- [ ] Do not delete `ui/`, `web/public/fonts/` or `baps-logo.svg` in the same commit as the
      content rewrite. Separate commits so one can be reverted without the other
- [ ] Do not create anything at `bkt-baps-solutions/w1.baps.solutions` after the transfer. That
      is what makes the GitHub redirect, and the reverse path, stop working
- [ ] No off-disk backup exists yet per `CLAUDE.md`. Until one does, prefer `mv` over `rm` and do
      not touch the `_inbox` parked copies
