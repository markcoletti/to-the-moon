# to-the-moon
To the Moon Survival Guide related code.

This code written by Mark "Piprrr" Coletti and Andy "Raptor" Berres.

Most of this code takes the output of Google forms, which is a spreadsheet, and outputs LaTeX code that can be
copied into the Survival Guide.

The directory `simple` contains older scripts that generates simple LaTeX for arts, events, and camps.  Basically,
just creates `\sections` and `\subsections` for each entry.  More recent versions in this directory level use 
additonal information to share additional information, such as event categories and theme camp attributes.

* `mk_art.py` - Generates LaTeX code for art
* `mk_camps.py` - Generates LaTeX code for theme camps
* `mk_events.py` - Generates LaTeX code for events
* `mk_keyfile.py` - Generates camp and art map keys

## Tooling setup (`mise` + `just`)

This project uses:

- `mise` to install and pin tool versions for the repo (`python`, `just`, `uv`)
- `uv` to install/manage Python dependencies from `pyproject.toml`
- `just` as a simple task runner (similar to `make`, but easier to read/use)

### 1) Install `mise`

On macOS (Homebrew):

```bash
brew install mise
```

### 2) Install project tools

From the repo root:

```bash
mise install
```

This reads `mise.toml` and installs the expected versions of `python`, `just`, and `uv`.

### 3) Verify setup

```bash
python3 --version
just --version
uv --version
```

### 4) Install Python dependencies

From the repo root:

```bash
mise exec -- uv sync
# or via just:
just setup-python
```

This installs project dependencies (including `pandas`) from `pyproject.toml` using the `mise`-managed toolchain, without using any mise tasks.

### 5) See available commands

```bash
just --list
```

If you skip `mise`, you can still run the project as long as you already have compatible `python3` and `just` installed.

## Events pipeline with Dust + Forms

This repo includes a `just` workflow that can be run end-to-end or step-by-step:

1. Export events CSV from Dust manually and save as `data/<year>/dust/events.csv`
2. Convert Dust event format into Forms format
3. Consolidate Forms + Grotto + Dust-converted events
4. Run `mk_events.py`

Event conversion behavior:

- One output row per event per day
- If an event has multiple time slots on the same day, the earliest slot is kept for that day

### List available commands

```bash
just --list
```

### Save a manual Dust export first

Export your events CSV from Dust manually, then place it at:

```bash
cp /path/to/dust-events.csv data/2026/dust/events.csv
```

Default year is `2026`. You can override it:

```bash
just events-convert 2027
```

### Run each step individually

```bash
just events-convert
just events-consolidate
just events-mk
```

`events-consolidate` also regenerates `data/<year>/dust/events_forms.csv` automatically, so it works even if that intermediate file does not exist yet.

If you get `ModuleNotFoundError: No module named 'pandas'`, run:

```bash
mise exec -- uv sync
# or:
just setup-python
```

### Run all steps

```bash
just events-all
```

You can run for another year:

```bash
just events-all 2027
```

## Camps pipeline with Dust + Forms

This repo also includes a camps workflow that mirrors the events flow:

1. Export camps CSV from Dust manually and save as `data/<year>/dust/camps.csv`
2. Convert Dust camp format into Forms format
3. Consolidate Forms + Dust-converted camps
4. Run `mk_camps.py`

### Run each camp step individually

```bash
just camps-convert
just camps-consolidate
just camps-mk
```

### Run full camp pipeline

```bash
just camps-all
```

You can run for another year:

```bash
just camps-all 2027
```

`camps-consolidate` also regenerates `data/<year>/dust/camps_forms.csv` automatically.

### Scripts (direct usage)

If you want to run scripts directly:

```bash
# Input should already exist at data/2026/dust/events.csv
python3 scripts/convert_dust_events_to_forms.py --year 2026
python3 scripts/consolidate_events.py --year 2026
python3 mk_events.py data/2026/consolidated/events.csv 2026

# Camps
python3 scripts/convert_dust_camps_to_forms.py --year 2026
python3 scripts/consolidate_camps.py --year 2026
python3 mk_camps.py data/2026/consolidated/camps.csv
```
