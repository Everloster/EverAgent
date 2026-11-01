#!/usr/bin/env python3
"""Check only root README local links/anchors/media; never crawl old reports.

The context evaluator's relative-link check does not cover HTML, references,
code fences or self anchors. This standard-library checker adds that scope
without changing the historical report contract or requiring network tools.
"""
from __future__ import annotations

import html
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def blank(match: re.Match) -> str:
    return "".join("\n" if char == "\n" else " " for char in match.group())


def prose(text: str, *, inline: bool = False) -> str:
    """Mask comments and code while preserving diagnostic line numbers."""
    text = re.sub(r"<!--[\s\S]*?-->", blank, text)
    lines = []
    fence = ""
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            lines.append(re.sub(r"[^\n]", " ", line))
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", line):
                fence = ""
        elif marker:
            fence = marker.group(1)
            lines.append(re.sub(r"[^\n]", " ", line))
        elif line.startswith(("    ", "\t")) and not line.lstrip().startswith("<"):
            lines.append(re.sub(r"[^\n]", " ", line))
        else:
            lines.append(line)
    result = "".join(lines)
    return re.sub(r"(`+)(?!`)(.*?)\1(?!`)", blank, result) if inline else result


class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[int, str]] = []
        self.anchors: set[str] = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if not value:
                continue
            if key == "id" or (tag == "a" and key == "name"):
                self.anchors.add(value)
            if key in {"href", "src", "poster"}:
                self.links.append((self.getpos()[0], value))
            elif key == "srcset":
                # A data URL's comma is not a candidate separator.
                for token in value.split():
                    if token.startswith("data:"):
                        continue
                    for candidate in token.split(","):
                        if candidate and not re.fullmatch(r"[\d.]+[wx]", candidate):
                            self.links.append((self.getpos()[0], candidate))

    handle_startendtag = handle_starttag


def heading_slug(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]*>", "", text)).lower()
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*~]", "", text)
    text = "".join(char for char in text if char in "-_" or unicodedata.category(char)[0] not in {"P", "S", "C"})
    return text.replace(" ", "-")


def markdown_anchors(text: str) -> set[str]:
    text = prose(text)
    parser = HTMLLinks()
    parser.feed(text)
    anchors = set(parser.anchors)
    used: set[str] = set()
    previous = ""
    for line in text.splitlines():
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$", line)
        heading = match.group(1) if match else None
        if previous.strip() and re.fullmatch(r" {0,3}(?:=+|-+)\s*", line):
            heading = previous.strip()
        if heading is not None:
            base = heading_slug(heading)
            slug = base
            count = 0
            while slug in used:
                count += 1
                slug = f"{base}-{count}"
            used.add(slug)
            anchors.add(slug)
        previous = line
    return anchors


def destination(text: str) -> str:
    text = text.lstrip()
    if text.startswith("<"):
        return text[1:text.find(">")]
    # Parentheses may be nested or escaped; a title follows whitespace.
    return re.split(r"\s", text, maxsplit=1)[0]


def local_links(text: str) -> list[tuple[int, str]]:
    text = prose(text, inline=True)
    parser = HTMLLinks()
    parser.feed(text)
    links = parser.links
    definitions: dict[str, str] = {}

    def key(value: str) -> str:
        return " ".join(value.split()).casefold()

    def definition(match):
        definitions[key(match.group(1))] = destination(match.group(2))
        return blank(match)

    text = re.sub(r"^ {0,3}\[([^\]]+)\]:\s*(.+)$", definition, text, flags=re.M)
    for match in re.finditer(r"\]\(", text):
        start = match.end()
        index = start
        depth = 1
        in_angle = text[start:start + 1] == "<"
        while index < len(text) and depth:
            char = text[index]
            if char == "\\":
                index += 2
                continue
            if char == ">" and in_angle:
                in_angle = False
            elif not in_angle:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
            index += 1
        if not depth:
            links.append((text.count("\n", 0, start) + 1, destination(text[start:index - 1])))
    for match in re.finditer(r"!?\[([^\]\n]+)\](?:\[([^\]\n]*)\])?(?!\()", text):
        label = key(match.group(2) or match.group(1))
        if label in definitions:
            links.append((text.count("\n", 0, match.start()) + 1, definitions[label]))
        elif match.group(2) is not None:
            links.append((text.count("\n", 0, match.start()) + 1, "<unresolved-reference>"))
    return links


def check_readme(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    readme = root / "README.md"
    if readme.is_symlink() or not readme.is_file():
        return ["README.md:0 MISSING_README"]
    try:
        text = readme.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ["README.md:0 UNREADABLE_README"]
    errors = []
    cache: dict[Path, set[str]] = {}
    for line, raw in local_links(text):
        target = html.unescape(re.sub(r"\\([() ])", r"\1", raw))
        try:
            url = urlsplit(target)
            if url.scheme or url.netloc or target.startswith("//"):
                continue
            path = unquote(url.path)
            resolved = (root / path.lstrip("/")).resolve() if path else readme
            if not resolved.is_relative_to(root):
                raise ValueError("OUTSIDE_REPOSITORY")
            if not resolved.exists():
                raise ValueError("MISSING_TARGET")
            if url.fragment:
                if resolved.is_dir():
                    resolved = (resolved / "README.md").resolve()
                    if not resolved.is_relative_to(root):
                        raise ValueError("OUTSIDE_REPOSITORY")
                if resolved.suffix.lower() in {".md", ".markdown", ".html", ".htm"}:
                    if resolved not in cache:
                        cache[resolved] = markdown_anchors(resolved.read_text(encoding="utf-8"))
                    if unquote(url.fragment) not in cache[resolved]:
                        raise ValueError("MISSING_ANCHOR")
        except (ValueError, OSError, UnicodeError):
            errors.append(f"README.md:{line} INVALID_LOCAL_LINK")
    return sorted(set(errors))


def main() -> int:
    errors = check_readme()
    for error in errors:
        print(error)
    print(f"README links: errors={len(errors)}")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
