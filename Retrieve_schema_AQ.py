#!/usr/bin/env python3
"""
Retrieve and save BigQuery table schemas to Markdown.

Defaults (tailored for Olist dbt staging):
- project: dsai-468212
- dataset: dbt_olist_stg
- tables (by default): only fact_/dim_ tables in the dataset
- out: artifacts/bq_schemas_dbt_olist_stg_dim_fact.md

Quick usage:
    # Use defaults (project/dataset and dim/fact tables listed below)
    python Retrieve_schema_AQ.py

    # Auto-discover tables by prefix (comma-separated, defaults to "dim_,fact_")
    python Retrieve_schema_AQ.py --discover
    python Retrieve_schema_AQ.py --discover --prefixes dim_,fact_

    # Custom project/dataset and explicit table list
    python Retrieve_schema_AQ.py --project my-proj --dataset my_ds \
        --tables dim_customer,fact_order_items --out artifacts/my_schemas.md
"""
from __future__ import annotations

import argparse
from typing import Iterable, List, Sequence
from pathlib import Path
from datetime import datetime

from google.cloud import bigquery


DEFAULT_PROJECT = "dsai-468212"
DEFAULT_DATASET = "dbt_olist_stg"
# Default to only dim_*/fact_* tables provided in the dataset
DEFAULT_TABLES = [
    "dim_customer",
    "dim_date",
    "dim_geolocation",
    "dim_order_reviews",
    "dim_orders",
    "dim_payment",
    "dim_product",
    "dim_seller",
    "fact_order_items",
]


def _print_fields(fields: Iterable[bigquery.SchemaField], indent: int = 2) -> None:
    pad = " " * indent
    for f in fields:
        # Example line: - order_id (STRING, REQUIRED)
        print(f"{pad}- {f.name} ({f.field_type}, {f.mode})")
        # Recurse into RECORDs
        if f.field_type.upper() == "RECORD" and f.fields:
            _print_fields(f.fields, indent=indent + 2)


def _fields_to_markdown_lines(fields: Iterable[bigquery.SchemaField], indent: int = 0) -> List[str]:
    pad = "  " * indent
    lines: List[str] = []
    for f in fields:
        lines.append(f"{pad}- {f.name} ({f.field_type}, {f.mode})")
        if f.field_type.upper() == "RECORD" and f.fields:
            lines.extend(_fields_to_markdown_lines(f.fields, indent=indent + 1))
    return lines


def print_table_schema(client: bigquery.Client, project: str, dataset: str, table: str) -> None:
    full_id = f"{project}.{dataset}.{table}"
    try:
        table_obj = client.get_table(full_id)
    except Exception as exc:  # Broad by design to surface helpful context without stacktrace
        print(f"ERROR: Failed to retrieve schema for {full_id}: {exc}")
        return

    print("\n" + "=" * 80)
    print(f"Schema for {full_id}")
    print("=" * 80)
    if not table_obj.schema:
        print("(No fields found)")
        return
    _print_fields(table_obj.schema, indent=2)


def table_schema_to_markdown(client: bigquery.Client, project: str, dataset: str, table: str) -> str:
    full_id = f"{project}.{dataset}.{table}"
    try:
        table_obj = client.get_table(full_id)
    except Exception as exc:
        return f"## Schema for {full_id}\n\n> ERROR: Failed to retrieve schema: {exc}\n"

    if not table_obj.schema:
        return f"## Schema for {full_id}\n\n(No fields found)\n"

    lines = _fields_to_markdown_lines(table_obj.schema, indent=0)
    body = "\n".join(lines)
    return f"## Schema for {full_id}\n\n```text\n{body}\n```\n"


def list_tables_by_prefix(
    client: bigquery.Client,
    project: str,
    dataset: str,
    prefixes: Sequence[str],
) -> List[str]:
    """Return table IDs in dataset that start with any of the given prefixes.

    Notes:
    - Only includes permanent TABLEs (excludes views/snapshots if present).
    - Sorted alphabetically for stable output.
    """
    ds_fqn = f"{project}.{dataset}"
    try:
        tables_iter = client.list_tables(ds_fqn)
    except Exception as exc:
        print(f"ERROR: Failed to list tables for {ds_fqn}: {exc}")
        return []

    pfx = tuple(prefixes)
    results: List[str] = []
    for t in tables_iter:
        # BigQuery TableListItem has .table_id and .table_type
        if getattr(t, "table_type", "TABLE") != "TABLE":
            continue
        if t.table_id.startswith(pfx):
            results.append(t.table_id)
    return sorted(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve and print BigQuery table schemas, and save to Markdown.")
    parser.add_argument("--project", default=DEFAULT_PROJECT, help="GCP Project ID")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="BigQuery dataset ID")
    parser.add_argument(
        "--tables",
        default=",".join(DEFAULT_TABLES),
        help="Comma-separated list of table IDs (no dataset prefix)",
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Auto-discover tables in the dataset by prefixes (see --prefixes). Overrides --tables if set.",
    )
    parser.add_argument(
        "--prefixes",
        default="dim_,fact_",
        help="Comma-separated list of prefixes to include when using --discover (default: dim_,fact_)",
    )
    parser.add_argument(
        "--out",
        default=str(Path("artifacts") / "bq_schemas_dbt_olist_stg_dim_fact.md"),
        help="Path to output Markdown file",
    )
    args = parser.parse_args()

    project = args.project
    dataset = args.dataset
    tables = [t.strip() for t in args.tables.split(",") if t.strip()]
    out_path = Path(args.out)

    client = bigquery.Client(project=project)

    if args.discover:
        prefixes = [p.strip() for p in args.prefixes.split(",") if p.strip()]
        discovered = list_tables_by_prefix(client, project, dataset, prefixes)
        if discovered:
            tables = discovered
        else:
            print("WARNING: --discover yielded no tables; falling back to --tables or defaults.")

    print(f"Project: {project}")
    print(f"Dataset: {dataset}")
    print(f"Tables: {', '.join(tables) if tables else '(none)'}")

    for t in tables:
        print_table_schema(client, project, dataset, t)

    # Build Markdown document
    now = datetime.now().isoformat(timespec="seconds")
    header = [
        "# BigQuery Table Schemas",
        "",
        f"- Generated: {now}",
        f"- Project: {project}",
        f"- Dataset: {dataset}",
        f"- Tables: {', '.join(tables)}",
        "",
        "---",
        "",
    ]

    sections: List[str] = []
    for t in tables:
        sections.append(table_schema_to_markdown(client, project, dataset, t))

    doc = "\n".join(header + sections)

    # Ensure directory exists and write file
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    print(f"\nSaved schema Markdown to: {out_path}")


if __name__ == "__main__":
    main()
