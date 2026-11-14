#!/usr/bin/env python3
"""Normalize PDF page furniture and footnote syntax in converted markdown.

PDF → HTML → Markdown often dumps:
  - original page numbers (arabic AND roman) as standalone lines
  - running headers repeated on every page
  - footnote bodies as mid-paragraph fragments or a trailing 12: url list

This module restores Markdown footnotes (`[^N]` / `[^N]:`) and strips source
page furniture so those artifacts never reach translators or the Word body.
Output page numbers belong in the Word footer, not in the prose.
"""

from __future__ import annotations

import re
from collections import Counter

_ROMAN_RE = re.compile(
    r"^(?:m{0,3}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3}))$",
    re.I,
)
_END_NOTE_RE = re.compile(r"^(\d{1,3})[:.]\s+(\S.*)$")
_MD_FN_DEF_RE = re.compile(r"^\[\^(\d+)\]:\s*(.*)$")
_MD_FN_REF_RE = re.compile(r"\[\^(\d+)\]")
_BIB_FRAG_RE = re.compile(
    r"^(?:See |参见 )?"
    r"(?:"
    r"[A-Z][A-Za-z'’\-]{1,40},(?:\s+[A-Z]\.)+"  # Tyrrell, I.
    r"|\d{1,3}\s+[A-Z][A-Za-z'’\-]+,"  # 56 Doshi,
    r"|\*?[A-Z][A-Za-z .]{2,40}Journal"
    r")"
)
_SENTENCE_END = set(".!?。！？」』…\"'")


def _is_roman_numeral(text: str) -> bool:
    s = text.strip()
    if not s or len(s) > 6:
        return False
    if not _ROMAN_RE.match(s):
        return False
    # Single-letter "I" / "V" / "X" can be part titles; only drop them as
    # page numbers when they sit in a roman page sequence (see detector).
    return True


def _roman_to_int(text: str) -> int:
    vals = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
    s = text.strip().lower()
    total = 0
    prev = 0
    for ch in reversed(s):
        v = vals[ch]
        if v < prev:
            total -= v
        else:
            total += v
            prev = v
    return total


def _detect_roman_page_lines(lines: list[str], min_length: int = 4, min_ratio: float = 0.5) -> set[int]:
    """Drop standalone roman numerals that form a monotonic page sequence."""
    idxs = []
    values = []
    for i, line in enumerate(lines):
        s = line.strip()
        if _is_roman_numeral(s):
            idxs.append(i)
            values.append(_roman_to_int(s))
    n = len(values)
    if n < min_length:
        return set()

    # Longest non-decreasing subsequence (same idea as arabic page detector).
    import bisect

    tails: list[int] = []
    tails_idx: list[int] = []
    parents = [-1] * n
    for i, v in enumerate(values):
        pos = bisect.bisect_right(tails, v)
        if pos > 0:
            parents[i] = tails_idx[pos - 1]
        if pos == len(tails):
            tails.append(v)
            tails_idx.append(i)
        else:
            tails[pos] = v
            tails_idx[pos] = i
    lnds = []
    cur = tails_idx[-1]
    while cur != -1:
        lnds.append(cur)
        cur = parents[cur]
    lnds.reverse()
    if len(lnds) < min_length or len(lnds) / n < min_ratio:
        return set()
    return {idxs[i] for i in lnds}


def _detect_running_header_values(lines: list[str], min_count: int = 5) -> set[str]:
    counts = Counter()
    for line in lines:
        s = line.strip()
        if not (3 <= len(s) <= 70):
            continue
        if s.startswith(("#", "!", "[", "http", "```", "|")):
            continue
        if s.isdigit() or _is_roman_numeral(s):
            continue
        counts[s] += 1
    return {s for s, c in counts.items() if c >= min_count}


def strip_source_page_furniture(content: str) -> str:
    """Remove original PDF page numbers and repeated running headers from body.

    Output documents get their own page numbers in the Word footer. Source
    page labels (1, 2, vii, viii, 'Book Title  47') must not sit in the prose.
    """
    lines = content.split("\n")
    roman_pages = _detect_roman_page_lines(lines)
    headers = _detect_running_header_values(lines)
    seen_headers: set[str] = set()
    kept: list[str] = []
    for i, line in enumerate(lines):
        s = line.strip()
        if i in roman_pages:
            continue
        if s in headers:
            if s in seen_headers:
                continue
            seen_headers.add(s)
        kept.append(line)
    text = "\n".join(kept)
    return re.sub(r"\n{3,}", "\n\n", text)


def _cjk_ratio(text: str) -> float:
    if not text:
        return 0.0
    n = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return n / max(len(text), 1)


def _is_bib_fragment(text: str) -> bool:
    s = text.strip()
    if not s or len(s) > 400:
        return False
    if _MD_FN_DEF_RE.match(s) or _MD_FN_REF_RE.search(s):
        return False
    return bool(_BIB_FRAG_RE.match(s))


def reattach_split_footnote_fragments(content: str) -> str:
    """Join body paragraphs split by a leaked bibliographic footnote line.

    PDF page breaks often produce:

        …protect those politically

        Tyrrell, I. (2021). American exceptionalism...

        sensitive sectors from import competition.

    The middle line belongs in a footnote, not the body.
    """
    lines = content.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if _is_bib_fragment(s) and out:
            prev_idx = len(out) - 1
            while prev_idx >= 0 and not out[prev_idx].strip():
                prev_idx -= 1
            nxt = i + 1
            while nxt < len(lines) and not lines[nxt].strip():
                nxt += 1
            prev = out[prev_idx].strip() if prev_idx >= 0 else ""
            nxt_s = lines[nxt].strip() if nxt < len(lines) else ""
            prev_open = bool(prev) and prev[-1] not in _SENTENCE_END
            nxt_cont = bool(nxt_s) and (
                nxt_s[0].islower() or (_cjk_ratio(prev) > 0.25 and _cjk_ratio(nxt_s) > 0.25)
            )
            if prev_open and nxt_cont and prev_idx >= 0:
                # Drop the bibliographic fragment; stitch the split sentence.
                out[prev_idx] = out[prev_idx].rstrip() + nxt_s
                i = nxt + 1
                continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def promote_trailing_endnotes(content: str) -> str:
    """Turn a trailing '12: url' / '12. citation' dump into Markdown footnotes."""
    lines = content.split("\n")
    i = len(lines) - 1
    first_note = None
    count = 0
    while i >= 0:
        s = lines[i].strip()
        if not s:
            i -= 1
            continue
        if _END_NOTE_RE.match(s) or _MD_FN_DEF_RE.match(s):
            first_note = i
            count += 1
            i -= 1
            continue
        break
    if first_note is None or count < 4:
        return content

    new_lines = list(lines)
    for j in range(first_note, len(lines)):
        m = _END_NOTE_RE.match(lines[j].strip())
        if m and not _MD_FN_DEF_RE.match(lines[j].strip()):
            new_lines[j] = f"[^{m.group(1)}]: {m.group(2)}"
    return "\n".join(new_lines)


def normalize_layout(content: str) -> str:
    """Full cleanup pass used after Calibre/Pandoc markdown conversion."""
    content = strip_source_page_furniture(content)
    content = reattach_split_footnote_fragments(content)
    content = promote_trailing_endnotes(content)
    return re.sub(r"\n{3,}", "\n\n", content)
