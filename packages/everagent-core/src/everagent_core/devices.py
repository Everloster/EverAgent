"""Generic registry matching. Callers supply their own private registration facts."""
from __future__ import annotations

import re


def match_device(registry: list[dict], signals: tuple[str | None, str, str],
                 *, expected: str | None = None) -> dict | None:
    computer_name, hostname, platform = signals
    eligible = [row for row in registry if row.get("platform") == platform]
    matches = []
    for field, value in (("computername", computer_name), ("hostname_regex", hostname),
                         ("computername", hostname)):
        if not value:
            continue
        for row in eligible:
            pattern = row.get("hostname_regex")
            hit = (re.search(pattern, value, re.IGNORECASE) is not None
                   if field == "hostname_regex" and pattern else
                   value.casefold() in [name.casefold() for name in row.get("computername", [])]
                   if field == "computername" else False)
            if hit:
                matches.append(row)
        if matches:
            break
    unique = {row["id"]: row for row in matches}
    result = next(iter(unique.values())) if len(unique) == 1 else None
    if expected and (result is None or result["id"].casefold() != expected.casefold()):
        return None
    return result
