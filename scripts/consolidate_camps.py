#!/usr/bin/env python3
"""
Consolidate forms + Dust-converted camps into a single forms-shaped CSV.
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
    "Theme Camp Name": "camp",
    'In what "genres" would you classify your camp? Check all that apply.': "theme",
    "Public Camp Description": "description",
}

OUTPUT_RENAME_MAP = {v: k for k, v in FORM_RENAME_MAP.items()}
FORM_COLUMNS = ["camp", "theme", "description"]
REQUIRED_CORE_COLUMNS = ["camp", "description"]
SOURCE_FLAGS = {
    "forms/camps.csv": "present_in_forms_camps_csv",
    "dust/camps_forms.csv": "present_in_dust_camps_csv",
}


def read_source(path, source_name):
    return load_source_rows(
        path=path,
        source_name=source_name,
        target_columns=FORM_COLUMNS,
        key_column="camp",
        rename_map=FORM_RENAME_MAP,
        required_core_columns=REQUIRED_CORE_COLUMNS,
    )


def main():
    parser = argparse.ArgumentParser(description="Consolidate camps across source files")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--forms", default=None, help="Path to forms/camps.csv")
    parser.add_argument("--dust-forms", default=None, help="Path to converted Dust camps CSV")
    parser.add_argument("--output", default=None, help="Consolidated output path")
    parser.add_argument("--audit-output", default=None, help="Audit output path")
    parser.add_argument(
        "--fuzzy-threshold",
        type=float,
        default=0.93,
        help="Camp-name fuzzy-match threshold for cluster merges",
    )
    args = parser.parse_args()

    forms_path = Path(args.forms) if args.forms else Path(f"data/{args.year}/forms/camps.csv")
    dust_forms_path = (
        Path(args.dust_forms)
        if args.dust_forms
        else Path(f"data/{args.year}/dust/camps_forms.csv")
    )
    output_path = (
        Path(args.output)
        if args.output
        else Path(f"data/{args.year}/consolidated/camps.csv")
    )
    audit_output_path = (
        Path(args.audit_output)
        if args.audit_output
        else Path(f"data/{args.year}/consolidated/camps_audit.csv")
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)

    source_priority = ["dust/camps_forms.csv", "forms/camps.csv"]
    rows = []
    rows.extend(read_source(forms_path, "forms/camps.csv"))
    rows.extend(read_source(dust_forms_path, "dust/camps_forms.csv"))

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

        canonical_name = primary.key
        audit = {
            "consolidated_camp_name": canonical_name,
            "canonical_normalized_key": normalize_key(canonical_name),
            "prioritized_source": primary.source,
        }
        for source_name, flag_name in SOURCE_FLAGS.items():
            audit[flag_name] = source_name in by_source
            source_rows = by_source.get(source_name, [])
            title_key = source_name.replace("/", "_").replace(".csv", "") + "_camp_matched"
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
    consolidated_df.sort_values(by=["Theme Camp Name"], inplace=True)
    consolidated_df.to_csv(
        output_path,
        columns=output_columns + flag_columns + ["prioritized_source"],
        index=False,
    )

    audit_df = pd.DataFrame(audit_rows)
    audit_df.sort_values(by=["consolidated_camp_name"], inplace=True)
    audit_df.to_csv(audit_output_path, index=False)

    print(f"Wrote consolidated camps CSV to {output_path}")
    print(f"Wrote consolidation audit CSV to {audit_output_path}")


if __name__ == "__main__":
    main()
