"""Stdlib-only client for an append-only TSV coordination log.

The log is a tab-separated file with columns:
    timestamp<TAB>sender<TAB>recipient<TAB>type<TAB>message

`message` is the only field that may contain tabs/newlines; they are escaped on
write and unescaped on read. All operations are local-file and dependency-free.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

Row = tuple[str, str, str, str, str]


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def _unescape(s: str) -> str:
    return s.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def append_row(path: str | Path, sender: str, recipient: str, type_: str, message: str, timestamp: str | None = None) -> str:
    ts = timestamp or now()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow([ts, sender, recipient, type_, _escape(message)])
    return ts


def read_rows(path: str | Path) -> list[Row]:
    rows: list[Row] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) < 5:
                    continue
                rows.append((parts[0], parts[1], parts[2], parts[3], _unescape("\t".join(parts[4:]))))
    except OSError:
        return []
    return rows


def tail(path: str | Path, n: int) -> list[Row]:
    return read_rows(path)[-n:]


def search(path: str | Path, pattern: str, case_insensitive: bool = True) -> list[Row]:
    needle = pattern.lower() if case_insensitive else pattern
    out: list[Row] = []
    for row in read_rows(path):
        hay = "\t".join(row)
        hay = hay.lower() if case_insensitive else hay
        if needle in hay:
            out.append(row)
    return out


def status(path: str | Path) -> dict[str, object]:
    rows = read_rows(path)
    return {"lines": len(rows), "last_timestamp": rows[-1][0] if rows else None}
