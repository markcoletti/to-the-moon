#!/usr/bin/env python3
"""
Shared helpers for consolidation pipelines.
"""

from dataclasses import dataclass
from difflib import SequenceMatcher
import re

import pandas as pd


@dataclass
class SourceRow:
    source: str
    key: str
    normalized_key: str
    data: dict


def normalize_key(value):
    text = str(value or "").strip().lower()
    text = text.replace("’", "'")
    text = re.sub(r"[^a-z0-9\s']", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def fuzzy_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_fallback_column(df, exact=None, prefix=None):
    exact = exact or []
    prefix = prefix or []

    for candidate in exact:
        if candidate in df.columns:
            return candidate

    for candidate_prefix in prefix:
        match = next((column for column in df.columns if column.startswith(candidate_prefix)), None)
        if match:
            return match

    return None


def load_source_rows(
    path,
    source_name,
    target_columns,
    key_column,
    rename_map=None,
    required_core_columns=None,
    fallback_rules=None,
    source_defaults=None,
):
    rename_map = rename_map or {}
    required_core_columns = required_core_columns or []
    fallback_rules = fallback_rules or {}
    source_defaults = source_defaults or {}

    df = pd.read_csv(path).fillna("")
    df.rename(columns=rename_map, inplace=True)

    unresolved_core = []
    for column in target_columns:
        if column in df.columns:
            continue

        rules = fallback_rules.get(column, {})
        fallback_column = find_fallback_column(
            df,
            exact=rules.get("exact"),
            prefix=rules.get("prefix"),
        )
        if fallback_column:
            df[column] = df[fallback_column]
        else:
            df[column] = ""
            if column in required_core_columns:
                unresolved_core.append(column)

    for column, value in source_defaults.items():
        if column in df.columns:
            df[column] = df[column].replace("", value)

    if unresolved_core:
        raise ValueError(
            f"{source_name} is missing required columns with no fallback: {sorted(set(unresolved_core))}"
        )

    rows = []
    for row in df[target_columns].to_dict(orient="records"):
        key = str(row[key_column]).strip()
        if not key:
            continue
        clean = {k: ("" if pd.isna(v) else str(v).strip()) for k, v in row.items()}
        rows.append(
            SourceRow(
                source=source_name,
                key=key,
                normalized_key=normalize_key(key),
                data=clean,
            )
        )

    return rows


def cluster_rows(rows, fuzzy_threshold):
    clusters = []

    for row in rows:
        chosen_cluster = None
        best_ratio = 0.0
        match_type = "source_only"

        for cluster in clusters:
            exact_hit = next(
                (candidate for candidate in cluster if candidate.normalized_key == row.normalized_key),
                None,
            )
            if exact_hit:
                chosen_cluster = cluster
                best_ratio = 1.0
                match_type = "exact"
                break

            cluster_best = max(
                fuzzy_ratio(row.normalized_key, candidate.normalized_key) for candidate in cluster
            )
            if cluster_best > best_ratio:
                best_ratio = cluster_best
                if cluster_best >= fuzzy_threshold:
                    chosen_cluster = cluster
                    match_type = "fuzzy"

        if chosen_cluster is None:
            clusters.append([row])
        else:
            row.data["_match_type"] = match_type
            row.data["_match_score"] = f"{best_ratio:.4f}"
            chosen_cluster.append(row)

    return clusters


def pick_prioritized_row(cluster, source_priority):
    by_source = {}
    for row in cluster:
        by_source.setdefault(row.source, []).append(row)

    for source in source_priority:
        if source in by_source:
            return by_source[source][0], by_source
    return cluster[0], by_source


def fill_missing_fields(base, candidates, target_columns):
    merged = dict(base)
    for candidate in candidates:
        for key in target_columns:
            if not merged.get(key) and candidate.data.get(key):
                merged[key] = candidate.data[key]
    return merged
