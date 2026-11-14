#!/usr/bin/env python3
"""Ensure a translated DOCX keeps footnotes as Word footnotes and page numbers in the footer.

Calibre HTML→DOCX often flattens Markdown footnotes into a body-end dump.
Pandoc markdown→DOCX creates a real word/footnotes.xml. This module:
  - inspects a .docx
  - adds a centered PAGE field in the footer if none exists
  - never writes original source page numbers into the body
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
R_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
FOOTER_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
FOOTNOTES_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", REL_NS)


def _q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def inspect_docx(path: str) -> dict:
    info = {
        "path": path,
        "has_footnotes_xml": False,
        "footnote_count": 0,
        "body_footnote_refs": 0,
        "has_footer": False,
        "body_endnote_dump": False,
    }
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        info["has_footnotes_xml"] = "word/footnotes.xml" in names
        info["has_footer"] = any(n.startswith("word/footer") for n in names)
        if "word/footnotes.xml" in names:
            root = ET.fromstring(zf.read("word/footnotes.xml"))
            notes = [
                el
                for el in root.findall(_q(W_NS, "footnote"))
                if el.get(_q(W_NS, "id")) not in ("-1", "0")
            ]
            info["footnote_count"] = len(notes)
        if "word/document.xml" in names:
            doc = ET.fromstring(zf.read("word/document.xml"))
            info["body_footnote_refs"] = len(doc.findall(".//" + _q(W_NS, "footnoteReference")))
            texts = []
            for t in doc.findall(".//" + _q(W_NS, "t")):
                if t.text:
                    texts.append(t.text.strip())
            dump_hits = 0
            for t in texts[-40:]:
                if re.match(r"^\d{1,3}[:.]\s+\S", t):
                    dump_hits += 1
            info["body_endnote_dump"] = dump_hits >= 5
    return info


def _footer_xml() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:ftr xmlns:w="{W_NS}">'
        "<w:p>"
        "<w:pPr><w:jc w:val=\"center\"/></w:pPr>"
        "<w:r><w:fldChar w:fldCharType=\"begin\"/></w:r>"
        "<w:r><w:instrText xml:space=\"preserve\"> PAGE </w:instrText></w:r>"
        "<w:r><w:fldChar w:fldCharType=\"end\"/></w:r>"
        "</w:p>"
        "</w:ftr>"
    ).encode("utf-8")


def ensure_page_footer(path: str) -> bool:
    """Add a centered PAGE footer if the document has none. Returns True if written."""
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        if any(n.startswith("word/footer") for n in names):
            return False
        parts = {n: zf.read(n) for n in names}

    # Content types
    ct = ET.fromstring(parts["[Content_Types].xml"])
    ct_ns = ct.tag.split("}")[0].strip("{") if ct.tag.startswith("{") else CT_NS
    override = ET.SubElement(ct, f"{{{ct_ns}}}Override")
    override.set("PartName", "/word/footer1.xml")
    override.set(
        "ContentType",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml",
    )
    parts["[Content_Types].xml"] = ET.tostring(ct, xml_declaration=True, encoding="UTF-8")

    # document.xml.rels
    rels_name = "word/_rels/document.xml.rels"
    rels = ET.fromstring(parts[rels_name])
    rels_ns = rels.tag.split("}")[0].strip("{") if rels.tag.startswith("{") else R_NS
    existing_ids = []
    for rel in rels:
        rid = rel.get("Id") or ""
        m = re.match(r"rId(\d+)$", rid)
        if m:
            existing_ids.append(int(m.group(1)))
    next_id = (max(existing_ids) + 1) if existing_ids else 1
    rid = f"rId{next_id}"
    rel = ET.SubElement(rels, f"{{{rels_ns}}}Relationship")
    rel.set("Id", rid)
    rel.set("Type", FOOTER_TYPE)
    rel.set("Target", "footer1.xml")
    parts[rels_name] = ET.tostring(rels, xml_declaration=True, encoding="UTF-8")

    # sectPr footerReference
    doc = ET.fromstring(parts["word/document.xml"])
    body = doc.find(_q(W_NS, "body"))
    if body is None:
        raise ValueError("document.xml has no w:body")
    sect = body.find(_q(W_NS, "sectPr"))
    if sect is None:
        sect = ET.SubElement(body, _q(W_NS, "sectPr"))
    ref = ET.SubElement(sect, _q(W_NS, "footerReference"))
    ref.set(_q(REL_NS, "id"), rid)
    ref.set(_q(W_NS, "type"), "default")
    parts["word/document.xml"] = ET.tostring(doc, xml_declaration=True, encoding="UTF-8")
    parts["word/footer1.xml"] = _footer_xml()

    tmp = path + ".tmp.docx"
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in parts.items():
            zf.writestr(name, data)
    os.replace(tmp, path)
    return True


def generate_docx_via_pandoc(md_file: str, docx_file: str, title: str, lang_attr: str) -> bool:
    """Markdown → DOCX through pandoc so [^N] become real Word footnotes."""
    import subprocess

    cmd = [
        "pandoc",
        md_file,
        "-o",
        docx_file,
        "--from",
        "markdown+smart+east_asian_line_breaks+footnotes",
        "--to",
        "docx",
        "--metadata",
        f"title={title}",
        "--metadata",
        f"lang={lang_attr}",
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"Pandoc markdown→docx failed: {exc}")
        return False
    if not os.path.isfile(docx_file):
        return False
    try:
        ensure_page_footer(docx_file)
    except Exception as exc:
        print(f"Warning: could not add page-number footer: {exc}")
    info = inspect_docx(docx_file)
    print(
        "DOCX layout: footnotes.xml={has_footnotes_xml} notes={footnote_count} "
        "refs={body_footnote_refs} footer={has_footer} body_dump={body_endnote_dump}".format(
            **info
        )
    )
    if info["body_endnote_dump"] and not info["has_footnotes_xml"]:
        print(
            "WARNING: footnote-like numbered lines remain in the Word body. "
            "They should be Markdown [^N] definitions so pandoc can place them at page bottom."
        )
    return True


def main():
    parser = argparse.ArgumentParser(description="Inspect or repair translated DOCX layout")
    parser.add_argument("docx")
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--ensure-footer", action="store_true")
    args = parser.parse_args()
    if args.ensure_footer:
        changed = ensure_page_footer(args.docx)
        print("footer added" if changed else "footer already present")
    info = inspect_docx(args.docx)
    for k, v in info.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
