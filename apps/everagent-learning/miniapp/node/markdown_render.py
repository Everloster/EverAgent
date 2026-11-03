#!/usr/bin/env python3
"""Zero-dependency Markdown renderer for the EverAgent learning Mini App.

The Mini App payload must stay dependency-free: the Host neither installs
packages nor runs a build step, so a third-party Markdown library cannot be
assumed to exist at runtime. This module implements the Markdown subset that
the public repository's learning reports actually use.

Safety contract:

* every character taken from a report is HTML-escaped before any markup is
  emitted, so raw HTML inside a report is displayed as text;
* link and image URLs are restricted to ``http``, ``https``, ``mailto``,
  in-document anchors and repository-relative paths;
* the returned string can therefore only contain tags produced here.
"""

from __future__ import annotations

import html
import posixpath
import re
from typing import Callable, List, Optional, Sequence, Tuple

__all__ = ["render_markdown"]

_FENCE_RE = re.compile(r"^(\s{0,3})(`{3,}|~{3,})[ \t]*(.*)$")
_HEADING_RE = re.compile(r"^(\s{0,3})(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_HR_RE = re.compile(r"^\s{0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$")
_SETEXT_H1_RE = re.compile(r"^\s{0,3}=+[ \t]*$")
_SETEXT_H2_RE = re.compile(r"^\s{0,3}-{2,}[ \t]*$")
_UL_RE = re.compile(r"^(\s*)([-*+])([ \t]+)(.*)$")
_OL_RE = re.compile(r"^(\s*)(\d{1,9})([.)])([ \t]+)(.*)$")
_QUOTE_RE = re.compile(r"^\s{0,3}>[ \t]?(.*)$")
_TASK_RE = re.compile(r"^\[([ xX])\][ \t]+(.*)$")
_TABLE_DELIM_RE = re.compile(
    r"^\s*\|?[ \t]*:?-+:?[ \t]*(?:\|[ \t]*:?-+:?[ \t]*)*\|?[ \t]*$"
)

_CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
_IMAGE_RE = re.compile(r"!\[([^\]]*)\][ \t]*\([ \t]*([^)\s]+)(?:[ \t]+\"[^\"]*\")?[ \t]*\)")
_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\][ \t]*\([ \t]*([^)\s]+)(?:[ \t]+\"[^\"]*\")?[ \t]*\)")
_AUTOLINK_RE = re.compile(r"<((?:https?|mailto):[^>\s]+)>")
_DETAILS_OPEN_RE = re.compile(r"^<details(\s[^>]*)?>$", re.IGNORECASE)
_DETAILS_CLOSE_RE = re.compile(r"^</details>$", re.IGNORECASE)
_SUMMARY_RE = re.compile(r"^<summary>(.*)</summary>$", re.IGNORECASE)
_RAW_SIMPLE_TAG_RE = re.compile(r"<(/?(?:strong|em|b|i|code))>", re.IGNORECASE)
_RAW_ANCHOR_RE = re.compile(r"<a\s+id=([\"'])([A-Za-z0-9_-]+)\1\s*>\s*</a>", re.IGNORECASE)
_BOLD_RE = re.compile(r"\*\*([^*\n]+)\*\*")
_BOLD_UNDER_RE = re.compile(r"__([^_\n]+)__")
_ITALIC_RE = re.compile(r"(?<![*\w])\*([^*\n]+?)(?<!\s)\*(?!\*)")
_ITALIC_UNDER_RE = re.compile(r"(?<![\w_])_([^_\n]+?)_(?![\w_])")
_STRIKE_RE = re.compile(r"~~([^~\n]+)~~")

_SAFE_SCHEMES = ("http", "https", "mailto")
_SLUG_STRIP_RE = re.compile(r"[^\w\u4e00-\u9fff-]+")
_LANG_RE = re.compile(r"^[A-Za-z0-9_+.-]+$")


def _safe_url(url: str) -> str:
    """Return the URL when it is safe to emit, otherwise an empty string."""
    candidate = url.strip()
    if not candidate:
        return ""
    if any(ord(char) < 32 for char in candidate) or "\\" in candidate:
        return ""
    lowered = candidate.lower()
    if lowered.startswith("//"):
        return ""
    if candidate.startswith("#") or candidate.startswith("/"):
        return candidate
    scheme = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*):", lowered)
    if scheme:
        if scheme.group(1) in _SAFE_SCHEMES:
            return candidate
        return ""
    return candidate


class _Renderer:
    def __init__(
        self,
        image_resolver: Optional[Callable[[str], str]] = None,
        allow_raw_html: bool = False,
        link_resolver: Optional[Callable[[str], str]] = None,
    ) -> None:
        self._image_resolver = image_resolver
        self._link_resolver = link_resolver
        self._allow_raw_html = allow_raw_html
        self._slug_counts: dict[str, int] = {}

    # -- inline ----------------------------------------------------------

    def _inline(self, text: str) -> str:
        tokens: List[str] = []

        def stash(fragment: str) -> str:
            tokens.append(fragment)
            return "\x00%d\x00" % (len(tokens) - 1)

        def code_span(match: re.Match[str]) -> str:
            code = match.group(2).strip()
            return stash("<code>%s</code>" % html.escape(code, quote=False))

        working = _CODE_SPAN_RE.sub(code_span, text)

        if self._allow_raw_html:
            # These documents are HTML-flavored: their entities are already
            # written for a markup context. Decode once here so the escape
            # below does not turn "&amp;" into a literal "&amp;" on screen.
            working = html.unescape(working)

        def image(match: re.Match[str]) -> str:
            alt = match.group(1)
            raw = match.group(2)
            url = _safe_url(raw)
            if not url:
                return stash(html.escape(match.group(0), quote=False))
            if url.startswith("http"):
                return stash(
                    '<img src="%s" alt="%s" loading="lazy" referrerpolicy="no-referrer">'
                    % (html.escape(url, quote=True), html.escape(alt, quote=True))
                )
            resolved = self._image_resolver(url) if self._image_resolver else ""
            if resolved:
                return stash(
                    '<img src="%s" alt="%s" loading="lazy">'
                    % (html.escape(resolved, quote=True), html.escape(alt or "图片", quote=True))
                )
            return stash(html.escape(match.group(0), quote=False))

        working = _IMAGE_RE.sub(image, working)

        def link(match: re.Match[str]) -> str:
            label = match.group(1)
            url = _safe_url(match.group(2))
            if url and self._link_resolver:
                url = _safe_url(self._link_resolver(url))
            if not url:
                return stash(html.escape(match.group(0), quote=False))
            return stash(
                '<a href="%s" target="_blank" rel="noreferrer noopener">%s</a>'
                % (html.escape(url, quote=True), html.escape(label, quote=False))
            )

        working = _LINK_RE.sub(link, working)
        working = _AUTOLINK_RE.sub(
            lambda match: stash(
                '<a href="%s" target="_blank" rel="noreferrer noopener">%s</a>'
                % (html.escape(match.group(1), quote=True), html.escape(match.group(1), quote=False))
            ),
            working,
        )

        if self._allow_raw_html:
            # A small, attribute-free tag set, only for the repository's own
            # living lists. These tags cannot load anything or run code, and
            # the anchor id is restricted to word characters.
            def raw_tag(match: re.Match[str]) -> str:
                tag = match.group(1).lower()
                if tag.startswith("/"):
                    return stash("</%s>" % tag[1:])
                return stash("<%s>" % tag)

            def raw_anchor(match: re.Match[str]) -> str:
                return stash('<a id="%s"></a>' % html.escape(match.group(2), quote=True))

            working = _RAW_SIMPLE_TAG_RE.sub(raw_tag, working)
            working = _RAW_ANCHOR_RE.sub(raw_anchor, working)

        working = html.escape(working, quote=False)
        working = _BOLD_RE.sub(r"<strong>\1</strong>", working)
        working = _BOLD_UNDER_RE.sub(r"<strong>\1</strong>", working)
        working = _ITALIC_RE.sub(r"<em>\1</em>", working)
        working = _ITALIC_UNDER_RE.sub(r"<em>\1</em>", working)
        working = _STRIKE_RE.sub(r"<del>\1</del>", working)

        return re.sub(r"\x00(\d+)\x00", lambda match: tokens[int(match.group(1))], working)

    # -- blocks ----------------------------------------------------------

    def _slug(self, text: str) -> str:
        base = _SLUG_STRIP_RE.sub("-", text.strip().lower()).strip("-") or "section"
        count = self._slug_counts.get(base, 0)
        self._slug_counts[base] = count + 1
        return base if count == 0 else "%s-%d" % (base, count)

    def _is_block_start(self, line: str) -> bool:
        if _FENCE_RE.match(line):
            return True
        if _HEADING_RE.match(line):
            return True
        if _HR_RE.match(line):
            return True
        if _QUOTE_RE.match(line):
            return True
        if _UL_RE.match(line) or _OL_RE.match(line):
            return True
        if _SETEXT_H1_RE.match(line) or _SETEXT_H2_RE.match(line):
            return True
        if self._allow_raw_html and _DETAILS_OPEN_RE.match(line.strip()):
            return True
        return False

    def _blocks(self, lines: Sequence[str]) -> List[str]:
        out: List[str] = []
        index = 0
        total = len(lines)
        while index < total:
            line = lines[index]
            if not line.strip():
                index += 1
                continue

            fence = _FENCE_RE.match(line)
            if fence:
                index = self._fenced_code(lines, index, out)
                continue

            heading = _HEADING_RE.match(line)
            if heading:
                level = len(heading.group(2))
                raw = heading.group(3).strip()
                out.append(
                    '<h%d id="%s">%s</h%d>'
                    % (level, self._slug(raw), self._inline(raw), level)
                )
                index += 1
                continue

            if _HR_RE.match(line):
                out.append("<hr>")
                index += 1
                continue

            if _QUOTE_RE.match(line):
                index = self._blockquote(lines, index, out)
                continue

            if (
                "|" in line
                and index + 1 < total
                and "|" in lines[index + 1]
                and _TABLE_DELIM_RE.match(lines[index + 1])
            ):
                index = self._table(lines, index, out)
                continue

            if _UL_RE.match(line) or _OL_RE.match(line):
                index = self._list(lines, index, out)
                continue

            if self._allow_raw_html and _DETAILS_OPEN_RE.match(line.strip()):
                index = self._details(lines, index, out)
                continue

            index = self._paragraph(lines, index, out)

        return out

    def _fenced_code(self, lines: Sequence[str], index: int, out: List[str]) -> int:
        match = _FENCE_RE.match(lines[index])
        assert match is not None
        fence = match.group(2)
        info = (match.group(3) or "").strip()
        language = info.split()[0] if info else ""
        body: List[str] = []
        index += 1
        while index < len(lines):
            closing = _FENCE_RE.match(lines[index])
            if (
                closing
                and closing.group(2)[0] == fence[0]
                and len(closing.group(2)) >= len(fence)
                and not (closing.group(3) or "").strip()
            ):
                index += 1
                break
            body.append(lines[index])
            index += 1
        attribute = ""
        if language and _LANG_RE.match(language):
            attribute = ' class="language-%s"' % html.escape(language, quote=True)
        out.append(
            "<pre><code%s>%s</code></pre>"
            % (attribute, html.escape("\n".join(body), quote=False))
        )
        return index

    def _blockquote(self, lines: Sequence[str], index: int, out: List[str]) -> int:
        body: List[str] = []
        while index < len(lines):
            quoted = _QUOTE_RE.match(lines[index])
            if quoted:
                body.append(quoted.group(1))
                index += 1
                continue
            if lines[index].strip() and not self._is_block_start(lines[index]):
                body.append(lines[index].strip())
                index += 1
                continue
            break
        out.append("<blockquote>%s</blockquote>" % "".join(self._blocks(body)))
        return index

    def _split_row(self, row: str) -> List[str]:
        text = row.strip()
        if text.startswith("|"):
            text = text[1:]
        if text.endswith("|") and not text.endswith("\\|"):
            text = text[:-1]
        cells: List[str] = []
        buffer: List[str] = []
        position = 0
        while position < len(text):
            char = text[position]
            if char == "\\" and position + 1 < len(text) and text[position + 1] == "|":
                buffer.append("|")
                position += 2
                continue
            if char == "|":
                cells.append("".join(buffer).strip())
                buffer = []
                position += 1
                continue
            buffer.append(char)
            position += 1
        cells.append("".join(buffer).strip())
        return cells

    def _table(self, lines: Sequence[str], index: int, out: List[str]) -> int:
        header = self._split_row(lines[index])
        delimiters = self._split_row(lines[index + 1])
        aligns: List[str] = []
        for cell in delimiters:
            stripped = cell.strip()
            if stripped.startswith(":") and stripped.endswith(":"):
                aligns.append("center")
            elif stripped.endswith(":"):
                aligns.append("right")
            elif stripped.startswith(":"):
                aligns.append("left")
            else:
                aligns.append("")
        index += 2
        rows: List[List[str]] = []
        while index < len(lines) and lines[index].strip() and "|" in lines[index]:
            rows.append(self._split_row(lines[index]))
            index += 1

        head = "".join(
            "<th%s>%s</th>"
            % (
                ' style="text-align:%s"' % align if align else "",
                self._inline(cell),
            )
            for cell, align in zip(header, aligns + [""] * max(0, len(header) - len(aligns)))
        )
        body = ""
        for row in rows:
            cells = ""
            for position, cell in enumerate(row):
                align = aligns[position] if position < len(aligns) else ""
                cells += "<td%s>%s</td>" % (
                    ' style="text-align:%s"' % align if align else "",
                    self._inline(cell),
                )
            body += "<tr>%s</tr>" % cells
        out.append(
            '<div class="md-table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (head, body)
        )
        return index

    def _list(self, lines: Sequence[str], index: int, out: List[str]) -> int:
        first_ordered = _OL_RE.match(lines[index])
        first_unordered = _UL_RE.match(lines[index])
        ordered = first_ordered is not None
        base_indent = len(
            (first_ordered or first_unordered).group(1)  # type: ignore[union-attr]
        )

        block: List[str] = []
        cursor = index
        total = len(lines)
        while cursor < total:
            line = lines[cursor]
            if not line.strip():
                lookahead = cursor
                while lookahead < total and not lines[lookahead].strip():
                    lookahead += 1
                if lookahead >= total:
                    break
                following = lines[lookahead]
                indent = len(following) - len(following.lstrip())
                marker = _UL_RE.match(following) or _OL_RE.match(following)
                if indent > base_indent or (marker and len(marker.group(1)) >= base_indent):
                    block.extend([""] * (lookahead - cursor))
                    cursor = lookahead
                    continue
                break
            indent = len(line) - len(line.lstrip())
            marker = _UL_RE.match(line) or _OL_RE.match(line)
            if marker:
                if indent < base_indent:
                    break
                if (_OL_RE.match(line) is not None) != ordered:
                    break
                block.append(line)
                cursor += 1
                continue
            if indent > base_indent:
                block.append(line)
                cursor += 1
                continue
            if self._is_block_start(line):
                break
            block.append(line.strip())
            cursor += 1

        while block and not block[-1].strip():
            block.pop()

        items: List[Tuple[int, List[str]]] = []
        current: Optional[List[str]] = None
        current_indent = 0
        for line in block:
            marker = _UL_RE.match(line) or _OL_RE.match(line)
            if marker and len(marker.group(1)) == base_indent:
                ordered_match = _OL_RE.match(line)
                if (ordered_match is not None) != ordered:
                    break
                ordered_match = _OL_RE.match(line)
                if ordered_match:
                    content_indent = (
                        len(ordered_match.group(1))
                        + len(ordered_match.group(2))
                        + len(ordered_match.group(3))
                        + len(ordered_match.group(4))
                    )
                    first_text = ordered_match.group(5)
                else:
                    content_indent = (
                        len(marker.group(1)) + len(marker.group(2)) + len(marker.group(3))
                    )
                    first_text = marker.group(4)
                if current is not None:
                    items.append((current_indent, current))
                current = [first_text]
                current_indent = content_indent
                continue
            if current is None:
                continue
            if not line.strip():
                current.append("")
                continue
            indent = len(line) - len(line.lstrip())
            if indent >= current_indent:
                current.append(line[current_indent:])
            else:
                current.append(line.strip())
        if current is not None:
            items.append((current_indent, current))

        rendered: List[str] = []
        for _, content in items:
            body = list(content)
            task = ""
            if body:
                task_match = _TASK_RE.match(body[0].strip())
                if task_match:
                    checked = " checked" if task_match.group(1).lower() == "x" else ""
                    task = '<input type="checkbox" disabled%s> ' % checked
                    body[0] = task_match.group(2)
            blocks = self._blocks(body)
            if blocks and blocks[0].startswith("<p>") and blocks[0].endswith("</p>"):
                inner = blocks[0][3:-4] + "".join(blocks[1:])
            else:
                inner = "".join(blocks)
            rendered.append("<li>%s%s</li>" % (task, inner))

        tag = "ol" if ordered else "ul"
        out.append("<%s>%s</%s>" % (tag, "".join(rendered), tag))
        return cursor

    def _details(self, lines: Sequence[str], index: int, out: List[str]) -> int:
        """Render one ``<details>`` block, keeping the fold behaviour.

        Only the ``<details>`` and ``<summary>`` elements survive as markup;
        everything inside stays on the escaped, sanitized path. The ``open``
        attribute is the only one carried over.
        """
        opening = _DETAILS_OPEN_RE.match(lines[index].strip())
        assert opening is not None
        raw_attributes = opening.group(1) or ""
        attributes = " open" if "open" in raw_attributes.split() else ""
        index += 1

        summary = ""
        while index < len(lines):
            line = lines[index].strip()
            index += 1
            if not line:
                continue
            match = _SUMMARY_RE.match(line)
            if match:
                summary = match.group(1)
                break
            # A summary is optional; anything else starts the body.
            index -= 1
            break

        body: List[str] = []
        depth = 0
        while index < len(lines):
            line = lines[index]
            stripped = line.strip()
            if _DETAILS_CLOSE_RE.match(stripped):
                index += 1
                if depth == 0:
                    break
                depth -= 1
                body.append(line)
                continue
            if _DETAILS_OPEN_RE.match(stripped):
                depth += 1
            body.append(line)
            index += 1

        inner = self._blocks(body)
        summary_html = "<summary>%s</summary>" % self._inline(summary) if summary else ""
        out.append("<details%s>%s%s</details>" % (attributes, summary_html, "".join(inner)))
        return index

    def _paragraph(self, lines: Sequence[str], index: int, out: List[str]) -> int:
        buffer = [lines[index].strip()]
        index += 1
        level = 0
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                break
            if _SETEXT_H1_RE.match(line):
                level = 1
                index += 1
                break
            if _SETEXT_H2_RE.match(line):
                level = 2
                index += 1
                break
            if self._is_block_start(line):
                break
            buffer.append(line.strip())
            index += 1
        content = self._inline(" ".join(buffer))
        if level:
            out.append('<h%d id="%s">%s</h%d>' % (level, self._slug(content), content, level))
        else:
            out.append("<p>%s</p>" % content)
        return index


def render_markdown(
    body: str,
    image_resolver: Optional[Callable[[str], str]] = None,
    allow_raw_html: bool = False,
    link_resolver: Optional[Callable[[str], str]] = None,
) -> str:
    """Render Markdown to sanitized HTML.

    ``image_resolver`` maps a repository-relative image path to an absolute URL
    so relative images can become links instead of broken images.

    ``allow_raw_html`` keeps ``<details>``/``<summary>`` folds as real markup
    instead of escaped text. It is opt-in and meant for the repository's own
    living lists, where the fold is the navigation. Everything inside a fold
    still goes through the escaped, sanitized path.
    """
    normalized = body.replace("\r\n", "\n").replace("\r", "\n")
    renderer = _Renderer(image_resolver=image_resolver, allow_raw_html=allow_raw_html, link_resolver=link_resolver)
    return "\n".join(renderer._blocks(normalized.split("\n")))
