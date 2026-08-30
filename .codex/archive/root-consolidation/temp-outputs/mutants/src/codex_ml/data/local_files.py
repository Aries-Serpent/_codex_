"""Local CSV/JSON/JSONL loaders (offline).

Simple utilities for loading local data files without requiring network access.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL file line-by-line.

    Parameters
    ----------
    path : str | Path
        Path to JSONL file

    Returns
    -------
    list[dict]
        List of JSON objects, one per line

    Examples
    --------
    >>> records = load_jsonl("data/train.jsonl")
    >>> len(records)
    1000
    >>> records[0]["text"]
    'example text'
    """
    records = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                records.append(json.loads(line))

    return records


def load_json(path: str | Path) -> dict[str, Any] | list[Any]:
    """Load single JSON object or array.

    Parameters
    ----------
    path : str | Path
        Path to JSON file

    Returns
    -------
    dict | list
        Parsed JSON content

    Examples
    --------
    >>> config = load_json("config.json")
    >>> config["model_name"]
    'gpt2'
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_csv(
    path: str | Path, *, delimiter: str = ",", encoding: str = "utf-8"
) -> list[dict[str, str]]:
    """Load CSV as list of row dicts.

    Parameters
    ----------
    path : str | Path
        Path to CSV file
    delimiter : str
        Column delimiter (default: ',')
    encoding : str
        File encoding (default: 'utf-8')

    Returns
    -------
    list[dict[str, str]]
        List of row dictionaries with column names as keys

    Examples
    --------
    >>> rows = load_csv("data/dataset.csv")
    >>> rows[0]["text"]
    'example text'
    >>> rows[0]["label"]
    '1'
    """
    records = []

    with open(path, encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            records.append(dict(row))

    return records


def save_jsonl(records: list[dict[str, Any]], path: str | Path) -> None:
    """Save records to JSONL file.

    Parameters
    ----------
    records : list[dict]
        Records to save
    path : str | Path
        Output path

    Examples
    --------
    >>> records = [{"text": "hello"}, {"text": "world"}]
    >>> save_jsonl(records, "output.jsonl")
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_json(data: dict[str, Any] | list[Any], path: str | Path, *, indent: int = 2) -> None:
    """Save data to JSON file.

    Parameters
    ----------
    data : dict | list
        Data to save
    path : str | Path
        Output path
    indent : int
        JSON indentation (default: 2)

    Examples
    --------
    >>> config = {"model": "gpt2", "lr": 0.001}
    >>> save_json(config, "config.json")
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def save_csv(
    records: list[dict[str, Any]],
    path: str | Path,
    *,
    fieldnames: list[str] | None = None,
    delimiter: str = ",",
) -> None:
    """Save records to CSV file.

    Parameters
    ----------
    records : list[dict]
        Records to save
    path : str | Path
        Output path
    fieldnames : list[str] | None
        Column names (default: keys from first record)
    delimiter : str
        Column delimiter (default: ',')

    Examples
    --------
    >>> records = [{"text": "hello", "label": "1"}, {"text": "world", "label": "0"}]
    >>> save_csv(records, "output.csv")
    """
    if not records:
        return

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fieldnames is None:
        fieldnames = list(records[0].keys())

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(records)
