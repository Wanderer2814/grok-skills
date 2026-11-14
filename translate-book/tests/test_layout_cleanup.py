import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import convert  # noqa: E402
import layout_cleanup as lc  # noqa: E402


class RomanPageNumberTests(unittest.TestCase):
    def test_drops_roman_front_matter_sequence(self):
        content = "\n".join(
            [
                "Preface paragraph.",
                "",
                "vii",
                "",
                "More preface.",
                "",
                "viii",
                "",
                "Still preface.",
                "",
                "ix",
                "",
                "Last preface.",
                "",
                "x",
                "",
                "Chapter starts.",
            ]
        )
        cleaned = lc.strip_source_page_furniture(content)
        for n in ("vii", "viii", "ix", "x"):
            self.assertNotIn(f"\n{n}\n", f"\n{cleaned}\n")
        self.assertIn("Preface paragraph.", cleaned)
        self.assertIn("Chapter starts.", cleaned)

    def test_keeps_lone_part_title_i(self):
        content = "\n".join(["Part heading follows.", "", "I", "", "The argument begins."])
        cleaned = lc.strip_source_page_furniture(content)
        self.assertIn("\nI\n", f"\n{cleaned}\n")


class RunningHeaderTests(unittest.TestCase):
    def test_keeps_first_running_header_drops_rest(self):
        lines = []
        for i in range(6):
            lines.extend([f"Paragraph {i}.", "", "World War Trade", ""])
        cleaned = lc.strip_source_page_furniture("\n".join(lines))
        self.assertEqual(cleaned.count("World War Trade"), 1)


class FootnoteNormalizeTests(unittest.TestCase):
    def test_promotes_trailing_endnotes(self):
        body = "\n".join(
            [
                "Main claim here.[^1]",
                "Another claim.[^2]",
                "",
                "36: https://example.com/a",
                "37: https://example.com/b",
                "38: Baldwin, R. (2025). The Great Trade Hack.",
                "39: https://example.com/c",
            ]
        )
        out = lc.promote_trailing_endnotes(body)
        self.assertIn("[^36]: https://example.com/a", out)
        self.assertNotIn("\n36: https://", out)

    def test_reattaches_bib_fragment_between_cjk_halves(self):
        content = "\n".join(
            [
                "华盛顿从不犹豫去保护那些在政治上",
                "",
                "Tyrrell, I. (2021). American exceptionalism: A new history of an old idea. University of Chicago Press.",
                "",
                "敏感的部门免受进口竞争。",
            ]
        )
        out = lc.reattach_split_footnote_fragments(content)
        self.assertIn("在政治上敏感的部门免受进口竞争。", out)
        self.assertNotIn("Tyrrell, I. (2021).", out)


class FootnoteBlockParseTests(unittest.TestCase):
    def test_footnote_def_is_its_own_block(self):
        content = "\n".join(
            [
                "Body with a mark.[^13]",
                "",
                "[^13]: Tyrrell, I. (2021). American exceptionalism.",
                "    University of Chicago Press.",
                "",
                "Next paragraph.",
            ]
        )
        blocks = convert.parse_structural_blocks(content)
        types = [b[1] for b in blocks]
        self.assertIn("footnote_def", types)
        fn = [t for t, b in blocks if b == "footnote_def"][0]
        self.assertIn("[^13]:", fn)
        self.assertIn("University of Chicago Press.", fn)
