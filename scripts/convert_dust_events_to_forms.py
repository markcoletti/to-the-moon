#!/usr/bin/env python3
"""
Convert Dust event-export rows into the Google Forms schema used by mk_events.py.
"""

import argparse
from pathlib import Path

import pandas as pd


FORM_COLUMNS = [
    "Who is hosting? Theme Camp or Your name",
    "What shall we call your Event?",
    "Not a Theme Camp? Please give us a location (art installation, lakeside, effigy, temple.. etc)",
    "Which day(s) will your event take place?",
    "What time will your event start?",
    "What time will your event end?",
    "Select a theme of your event for Pocket Guide!",
    "Description of your play-learn-workshop-event for the Pocket Guide!",
    "If Materials Are Used, Will You Provide Them?",
]


THEME_MAP = {
    "arts & crafts": "Workshop",
    "class/workshop": "Workshop",
    "workshop": "Workshop",
    "for kids": "Event",
    "gathering/party": "Party",
    "party": "Party",
    "live music": "Music",
    "music": "Music",
    "performance": "Performance",
    "ritual/ceremony": "Event",
    "fire/spectacle": "Fire",
    "food & drink": "Food",
    "food": "Food",
    "self care": "Chill",
    "repair": "Other",
    "miscellaneous": "Other",
    "games": "Game",
    "game": "Game",
    "tour": "Tour",
    "diversity & inclusion": "Event",
    "event": "Event",
}


def choose_theme(type_value):
    if pd.isna(type_value):
        return "Event"

    parts = [part.strip().lower() for part in str(type_value).split(",")]
    for part in parts:
        mapped = THEME_MAP.get(part)
        if mapped:
            return mapped
    return "Other"


def day_label(value):
    return value.strftime("%A, %B ") + str(value.day)


def to_form_time(value):
    return value.strftime("%I:%M:%S %p")


def main():
    parser = argparse.ArgumentParser(description="Convert Dust CSV into Forms schema")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument(
        "--input",
        default=None,
        help="Dust CSV input path (default: data/<year>/dust/events.csv)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Converted Forms CSV path (default: data/<year>/dust/events_forms.csv)",
    )
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else Path(f"data/{args.year}/dust/events.csv")
    output_path = (
        Path(args.output)
        if args.output
        else Path(f"data/{args.year}/dust/events_forms.csv")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    if df.empty:
        pd.DataFrame(columns=FORM_COLUMNS).to_csv(output_path, index=False)
        print(f"Input was empty. Wrote empty forms file to {output_path}")
        return

    df["start_dt"] = pd.to_datetime(df["startTime"], errors="coerce")
    df["end_dt"] = pd.to_datetime(df["endTime"], errors="coerce")
    df = df.dropna(subset=["title", "start_dt", "end_dt"])

    df["event_day"] = df["start_dt"].apply(day_label)

    # One row per day per event. If there are multiple times on the same day,
    # keep the first (earliest) slot for that day.
    group_cols = ["id", "title", "description", "type", "location", "event_day"]
    grouped = []

    for keys, chunk in df.groupby(group_cols, dropna=False):
        _event_id, title, description, type_value, location, event_day = keys
        chunk_sorted = chunk.sort_values(["start_dt", "end_dt"])

        start_dt = chunk_sorted.iloc[0]["start_dt"]
        end_dt = chunk_sorted.iloc[0]["end_dt"]

        grouped.append(
            {
                "Who is hosting? Theme Camp or Your name": "",
                "What shall we call your Event?": title,
                "Not a Theme Camp? Please give us a location (art installation, lakeside, effigy, temple.. etc)": (
                    "" if pd.isna(location) else str(location)
                ),
                "Which day(s) will your event take place?": event_day,
                "What time will your event start?": to_form_time(start_dt),
                "What time will your event end?": to_form_time(end_dt),
                "Select a theme of your event for Pocket Guide!": choose_theme(type_value),
                "Description of your play-learn-workshop-event for the Pocket Guide!": (
                    "" if pd.isna(description) else str(description)
                ),
                "If Materials Are Used, Will You Provide Them?": "",
                "_sort_date": start_dt.date().isoformat(),
                "_sort_start": start_dt.time().isoformat(timespec="seconds"),
            }
        )

    out_df = pd.DataFrame(grouped, columns=FORM_COLUMNS)
    out_df["_sort_date"] = [row["_sort_date"] for row in grouped]
    out_df["_sort_start"] = [row["_sort_start"] for row in grouped]
    out_df.sort_values(
        by=[
            "_sort_date",
            "_sort_start",
            "What shall we call your Event?",
        ],
        inplace=True,
    )
    out_df = out_df[FORM_COLUMNS]
    out_df.to_csv(output_path, index=False)
    print(f"Wrote converted Dust forms-format CSV to {output_path}")


if __name__ == "__main__":
    main()
