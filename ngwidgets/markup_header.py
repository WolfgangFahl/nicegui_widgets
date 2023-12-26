"""
Created on 2023-11-19

@author: wf
"""


class MarkupHeader:
    """
    Helper to generate tabulate compatible markup header lines.
    """

    @classmethod
    def get_markup(cls, title: str, markup_format: str, level: int = 1) -> str:
        """
        Generates a formatted header string based on the specified markup format.

        Args:
            title (str): The title to be formatted as the header.
            markup_format (str): The markup format for the header.
            level (int): The section level to generate a header for.

        Returns:
            str: The formatted header string.
        """
        if markup_format == "github":
            return f"{'#' * level} {title}\n"
        elif markup_format == "mediawiki":
            return f"{'=' * level} {title} {'=' * level}\n"
        elif markup_format == "html" or markup_format == "unsafehtml":
            return f"<h{level}>{title}</h{level}>"
        elif markup_format == "latex":
            if level == 1:
                return f"\\section{{{title}}}"
            elif level == 2:
                return f"\\subsection{{{title}}}"
            elif level == 3:
                return f"\\subsubsection{{{title}}}"
        elif markup_format == "textile":
            return f"h{level}. {title}"
        elif markup_format == "plain":
            return title
        else:
            # Default case for other formats
            return title
