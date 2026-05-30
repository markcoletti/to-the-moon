#!/usr/bin/env python3
"""
Consolidate forms + grotto + Dust-converted events into a single forms-shaped CSV.
"""

import argparse
from pathlib import Path

import pandas as pd

from consolidate_common import (
    cluster_rows,
    fill_missing_fields,
    load_source_rows,
    normalize_key,
    pick_prioritized_row,
)


FORM_RENAME_MAP = {
    "What shall we call your Event?": "title",
    "Who is hosting? Theme Camp or Your name": "host",
    "Which day(s) will your event take place?": "days",
    "What time will your event start?": "start",
    "What time will your event end?": "end",
    "Description of your play-learn-workshop-event for the Pocket Guide!": "description",
    "Select a theme of your event for Pocket Guide!": "theme",
    "If Materials Are Used, Will You Provide Them?": "bring",
    "Not a Theme Camp? Please give us a location (art installation, lakeside, effigy, temple.. etc)": "location",
}

OUTPUT_RENAME_MAP = {v: k for k, v in FORM_RENAME_MAP.items()}
FORM_COLUMNS = ["title", "host", "location", "days", "start", "end", "theme", "description", "bring"]
REQUIRED_CORE_COLUMNS = ["title", "days", "start", "end", "theme"]
SOURCE_FLAGS = {
    "forms/events.csv": "present_in_forms_events_csv",
    "forms/grotto_events.csv": "present_in_forms_grotto_events_csv",
    "dust/events_forms.csv": "present_in_dust_events_csv",
}

FALLBACK_COLUMN_RULES = {
    "location": {
        "exact": [],
        "prefix": [],
    },
    "description": {
        "exact": ["How do you plan to use the Grotto Space?", "Type of Event"],
        "prefix": [],
    },
    "bring": {
        "exact": [],
        "prefix": ["If you plan to bring any structures"],
    },
}


def read_source(path, source_name):
    source_defaults = {}
    if source_name == "forms/grotto_events.csv":
        source_defaults["location"] = "Grotto - Open Community Space"

    return load_source_rows(
        path=path,
        source_name=source_name,
        target_columns=FORM_COLUMNS,
        key_column="title",
        rename_map=FORM_RENAME_MAP,
        required_core_columns=REQUIRED_CORE_COLUMNS,
        fallback_rules=FALLBACK_COLUMN_RULES,
        source_defaults=source_defaults,
    )


def main():
    parser = argparse.ArgumentParser(description="Consolidate events across event sources")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--forms", default=None, help="Path to forms/events.csv")
    parser.add_argument("--grotto", default=None, help="Path to forms/grotto_events.csv")
    parser.add_argument("--dust-forms", default=None, help="Path to converted Dust forms CSV")
    parser.add_argument("--output", default=None, help="Consolidated output path")
    parser.add_argument("--audit-output", default=None, help="Audit output path")
    parser.add_argument(
        "--fuzzy-threshold",
        type=float,
        default=0.93,
        help="Title fuzzy-match threshold for cluster merges",
    )
    args = parser.parse_args()

    forms_path = Path(args.forms) if args.forms else Path(f"data/{args.year}/forms/events.csv")
    grotto_path = (
        Path(args.grotto) if args.grotto else Path(f"data/{args.year}/forms/grotto_events.csv")
    )
    dust_forms_path = (
        Path(args.dust_forms)
        if args.dust_forms
        else Path(f"data/{args.year}/dust/events_forms.csv")
    )
    output_path = (
        Path(args.output)
        if args.output
        else Path(f"data/{args.year}/consolidated/events.csv")
    )
    audit_output_path = (
        Path(args.audit_output)
        if args.audit_output
        else Path(f"data/{args.year}/consolidated/events_audit.csv")
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)

    source_priority = ["dust/events_forms.csv", "forms/events.csv", "forms/grotto_events.csv"]
    rows = []
    rows.extend(read_source(forms_path, "forms/events.csv"))
    rows.extend(read_source(grotto_path, "forms/grotto_events.csv"))
    rows.extend(read_source(dust_forms_path, "dust/events_forms.csv"))

    clusters = cluster_rows(rows, args.fuzzy_threshold)

    consolidated_rows = []
    audit_rows = []
    output_columns = [OUTPUT_RENAME_MAP[column] for column in FORM_COLUMNS]
    flag_columns = list(SOURCE_FLAGS.values())

    for cluster in clusters:
        primary, by_source = pick_prioritized_row(cluster, source_priority)
        merged = fill_missing_fields(primary.data, cluster, FORM_COLUMNS)

        output_row = {OUTPUT_RENAME_MAP[key]: merged[key] for key in FORM_COLUMNS}
        for source_name, flag_name in SOURCE_FLAGS.items():
            output_row[flag_name] = source_name in by_source
        output_row["prioritized_source"] = primary.source
        consolidated_rows.append(output_row)

        canonical_title = primary.key
        audit = {
            "consolidated_event_title": canonical_title,
            "canonical_normalized_key": normalize_key(canonical_title),
            "prioritized_source": primary.source,
        }
        for source_name, flag_name in SOURCE_FLAGS.items():
            audit[flag_name] = source_name in by_source
            source_rows = by_source.get(source_name, [])
            title_key = source_name.replace("/", "_").replace(".csv", "") + "_title_matched"
            match_type_key = source_name.replace("/", "_").replace(".csv", "") + "_match_type"
            match_score_key = source_name.replace("/", "_").replace(".csv", "") + "_match_score"
            if source_rows:
                matched = source_rows[0]
                audit[title_key] = matched.key
                audit[match_type_key] = matched.data.get("_match_type", "source_only")
                audit[match_score_key] = float(matched.data.get("_match_score", "1.0"))
            else:
                audit[title_key] = ""
                audit[match_type_key] = "none"
                audit[match_score_key] = 0.0
        audit_rows.append(audit)

    consolidated_df = pd.DataFrame(consolidated_rows)
    consolidated_df.sort_values(
        by=["What shall we call your Event?", "Which day(s) will your event take place?"],
        inplace=True,
    )
    consolidated_df.to_csv(
        output_path,
        columns=output_columns + flag_columns + ["prioritized_source"],
        index=False,
    )

    audit_df = pd.DataFrame(audit_rows)
    audit_df.sort_values(by=["consolidated_event_title"], inplace=True)
    audit_df.to_csv(audit_output_path, index=False)

    print(f"Wrote consolidated events CSV to {output_path}")
    print(f"Wrote consolidation audit CSV to {audit_output_path}")


if __name__ == "__main__":
    main()
