set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

year := env_var_or_default("YEAR", "2026")
py := ".venv/bin/python3"

default:
    @just --list

# Install Python dependencies from pyproject.toml.
setup-python:
    uv sync

# Convert Dust format into Forms-compatible format.
events-convert year_arg=year:
    {{py}} scripts/convert_dust_events_to_forms.py --year "{{year_arg}}"

# Consolidate Forms + Grotto + converted Dust events.
events-consolidate year_arg=year:
    {{py}} scripts/convert_dust_events_to_forms.py --year "{{year_arg}}"
    {{py}} scripts/consolidate_events.py --year "{{year_arg}}"

# Generate events_raw.tex from consolidated data.
events-mk year_arg=year:
    {{py}} mk_events.py "data/{{year_arg}}/consolidated/events.csv" "{{year_arg}}"

# Run full event pipeline using data/<year>/dust/events.csv.
events-all year_arg=year:
    {{py}} scripts/convert_dust_events_to_forms.py --year "{{year_arg}}"
    {{py}} scripts/consolidate_events.py --year "{{year_arg}}"
    {{py}} mk_events.py "data/{{year_arg}}/consolidated/events.csv" "{{year_arg}}"

# Convert Dust camps into Forms-compatible format.
camps-convert year_arg=year:
    {{py}} scripts/convert_dust_camps_to_forms.py --year "{{year_arg}}"

# Consolidate Forms + converted Dust camps.
camps-consolidate year_arg=year:
    {{py}} scripts/convert_dust_camps_to_forms.py --year "{{year_arg}}"
    {{py}} scripts/consolidate_camps.py --year "{{year_arg}}"

# Generate camps_raw.tex from consolidated camp data.
camps-mk year_arg=year:
    {{py}} mk_camps.py "data/{{year_arg}}/consolidated/camps.csv" "data/{{year_arg}}/output/camps_raw.tex"

# Run full camp pipeline using data/<year>/dust/camps.csv.
camps-all year_arg=year:
    {{py}} scripts/convert_dust_camps_to_forms.py --year "{{year_arg}}"
    {{py}} scripts/consolidate_camps.py --year "{{year_arg}}"
    {{py}} mk_camps.py "data/{{year_arg}}/consolidated/camps.csv" "data/{{year_arg}}/output/camps_raw.tex"
