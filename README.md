<h1 align="center">वाणी · W1</h1>

<p align="center"><em>Local, privacy-first dictation. Press a key, speak, it types.</em></p>

<p align="center"><a href="https://w1.baps.solutions">w1.baps.solutions</a></p>

> **Is my voice private?** Yes. W1 runs OpenAI's Whisper **entirely on your Mac** via Apple
> MLX. Nothing — no audio, no text — ever leaves your computer. No cloud, no account, no
> subscription.

W1 transcribes your speech accurately and **never changes your words**. Its one specialism: it
knows **BAPS Gujarati terminology**. When you say a term like *Akshardham, Vachanamrut, satsang,
murti, darshan*, it comes out in the correct canonical spelling — while every ordinary English
word is transcribed exactly as you said it. It does **not** substitute words: "temple" stays
"temple", "saint" stays "saint".

```
   speak  ──▶  Whisper (MLX, on-device)  ──▶  canonical-spelling pass  ──▶  pasted into any app
                                              (fixes spelling of terms you say · never your words)
```

## Quickstart
Apple Silicon Mac, [uv](https://docs.astral.sh/uv/) installed:

```bash
git clone https://github.com/jp-sapio-health/w1.baps.solutions.git w1 && cd w1
./install.sh          # venv + deps + model download + permission links
./w1 app              # launch the menu-bar app + floating widget
```

Then grant **Microphone**, **Accessibility**, and **Input Monitoring** to your terminal
(System Settings ▸ Privacy & Security — the installer prints the direct links). Hold
**Right-Option** and speak.

> The global hotkey needs **Input Monitoring**; without it the app runs but never hears the
> key. The hotkey is rebindable in **Settings**.

## How it works
- **One mode.** Accurate transcription + correct spelling of the specialised terms you say.
  No word substitution, no editorialising — your ordinary English is verbatim.
- **Hotkey:** hold **Right-Option** to talk (push-to-talk), or double-tap to toggle. Rebindable
  in Settings (press-to-capture). Text is inserted into whatever app is focused.
- **Canonical spelling:** a mis-heard term snaps to its glossary spelling
  (e.g. *vachanamrit → Vachanamrut*); a correctly-spoken term, and all ordinary English, is left
  untouched.
- **Confidence gate:** if Whisper isn't confident the audio was real speech, nothing is pasted —
  the widget flashes a red ✕ instead of inserting noise.
- **Model:** `whisper-large-v3-turbo`, swappable in one config line.

## CLI
| Command | What it does |
|---------|--------------|
| `./w1 app` | Launch the menu-bar app + floating widget |
| `./w1 dictate` | Record from the mic and paste the corrected text |
| `./w1 transcribe FILE` | Transcribe an audio file |
| `./w1 correct "text"` | Run text through the correction engine only |
| `./w1 doctor` | Check environment (deps, model, glossary, permission hints) |

`./w1` runs against the live source tree (no reinstall needed while developing).

## Tests
```bash
.venv/bin/python -m pytest tests/ -q                      # unit tests
.venv/bin/python -m pytest tests/ --cov=w1_core          # with coverage
.venv/bin/lint-imports                                    # platform-boundary contract
```

## Layout
`src/w1_core` — portable engine · `src/w1_data` — glossary data ·
`src/w1_macos` — the macOS app · `scripts/` — glossary ingestion, accuracy harness,
widget-frame generator · `docs/` — setup & packaging.

## Glossary source
The large canonical term list is ingested from the BAPS Master Glossary PDF via
`scripts/ingest_glossary_pdf.py` into `src/w1_data/master_glossary.json`. These spellings feed
the canonical-spelling pass and the known-word set; no word-substitution rules are derived from
them.
