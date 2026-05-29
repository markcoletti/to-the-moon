#!/usr/bin/env python3
"""
Convert Dust camp-export rows into the minimal Google Forms schema used by mk_camps.py.
"""

import argparse
from pathlib import Path

import pandas as pd


FORM_COLUMNS = [
    "Theme Camp Name",
    'In what "genres" would you classify your camp? Check all that apply.',
    "Public Camp Description",
]


def main():
    parser = argparse.ArgumentParser(description="Convert Dust camps CSV into forms schema")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument(
        "--input",
        default=None,
        help="Dust CSV input path (default: data/<year>/dust/camps.csv)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Converted Forms CSV path (default: data/<year>/dust/camps_forms.csv)",
    )
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else Path(f"data/{args.year}/dust/camps.csv")
    output_path = (
        Path(args.output) if args.output else Path(f"data/{args.year}/dust/camps_forms.csv")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    if df.empty:
        pd.DataFrame(columns=FORM_COLUMNS).to_csv(output_path, index=False)
        print(f"Input was empty. Wrote empty forms file to {output_path}")
        return

    out_df = pd.DataFrame(
        {
            "Theme Camp Name": df.get("name", "").fillna("").astype(str).str.strip(),
            'In what "genres" would you classify your camp? Check all that apply.': "",
            "Public Camp Description": df.get("description", "").fillna("").astype(str).str.strip(),
        }
    )
    out_df = out_df[out_df["Theme Camp Name"] != ""]
    out_df.sort_values(by=["Theme Camp Name"], inplace=True)
    out_df.to_csv(output_path, columns=FORM_COLUMNS, index=False)
    print(f"Wrote converted Dust camps forms-format CSV to {output_path}")


if __name__ == "__main__":
    main()
