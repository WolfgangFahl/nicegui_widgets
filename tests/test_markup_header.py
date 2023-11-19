"""
Created on 2023-11-19

@author: wf
"""
from ngwidgets.markup_header import MarkupHeader
from ngwidgets.basetest import Basetest

class TestsMarkupHeader(Basetest):
    """
    Test markup header handling.
    """

    def test_markup_header(self):
        """
        Test all available tabulate markup formats to create
        valid headers for different levels.
        """
        test_title = "Test Title"
        formats = [
            ("plain", 1, f"{test_title}"),
            ("simple", 1, f"{test_title}"),
            ("github", 1, f"# {test_title}"),
            ("github", 2, f"## {test_title}"),
            ("github", 3, f"### {test_title}"),
            ("grid", 1, f"{test_title}"),
            ("simple_grid", 1, f"{test_title}"),
            ("rounded_grid", 1, f"{test_title}"),
            ("heavy_grid", 1, f"{test_title}"),
            ("mixed_grid", 1, f"{test_title}"),
            ("double_grid", 1, f"{test_title}"),
            ("fancy_grid", 1, f"{test_title}"),
            ("outline", 1, f"{test_title}"),
            ("simple_outline", 1, f"{test_title}"),
            ("rounded_outline", 1, f"{test_title}"),
            ("heavy_outline", 1, f"{test_title}"),
            ("mixed_outline", 1, f"{test_title}"),
            ("double_outline", 1, f"{test_title}"),
            ("fancy_outline", 1, f"{test_title}"),
            ("pipe", 1, f"{test_title}"),
            ("orgtbl", 1, f"{test_title}"),
            ("asciidoc", 1, f"{test_title}"),
            ("jira", 1, f"{test_title}"),
            ("presto", 1, f"{test_title}"),
            ("pretty", 1, f"{test_title}"),
            ("psql", 1, f"{test_title}"),
            ("rst", 1, f"{test_title}"),
            ("mediawiki", 1, f"= {test_title} ="),
            ("mediawiki", 2, f"== {test_title} =="),
            ("mediawiki", 3, f"=== {test_title} ==="),
            ("moinmoin", 1, f"{test_title}"),
            ("youtrack", 1, f"{test_title}"),
            ("html", 1, f"<h1>{test_title}</h1>"),
            ("html", 2, f"<h2>{test_title}</h2>"),
            ("html", 3, f"<h3>{test_title}</h3>"),
            ("unsafehtml", 1, f"<h1>{test_title}</h1>"),
            ("unsafehtml", 2, f"<h2>{test_title}</h2>"),
            ("unsafehtml", 3, f"<h3>{test_title}</h3>"),
            ("latex", 1, f"\\section{{{test_title}}}"),
            ("latex", 2, f"\\subsection{{{test_title}}}"),
            ("latex", 3, f"\\subsubsection{{{test_title}}}"),
            ("latex_raw", 1, f"{test_title}"),
            ("latex_booktabs", 1, f"{test_title}"),
            ("latex_longtable", 1, f"{test_title}"),
            ("textile", 1, f"h1. {test_title}"),
            ("textile", 2, f"h2. {test_title}"),
            ("textile", 3, f"h3. {test_title}"),
            ("tsv", 1, f"{test_title}")
        ]

        for markup_format, level, expected_content in formats:
            with self.subTest(f"Testing format: {markup_format}, level: {level}"):
                header = MarkupHeader.get_markup(test_title, markup_format, level)
                self.assertEqual(header.strip(), expected_content)

