'''
Created on 2023-09-17

@author: wf
'''

from nicegui import ui
from typing import Tuple, List

class pdfviewer(ui.element, component='pdfviewer.js'):
    """
    nicegui PDF.js integration

    see https://mozilla.github.io/pdf.js/
    """

    def __init__(self) -> None:
        super().__init__()
        ui.add_head_html(f'<link href="https://mozilla.github.io/pdf.js/build/pdf_viewer.css" rel="stylesheet"/>')
        ui.add_head_html(f'<script src="https://mozilla.github.io/pdf.js/build/pdf.js"></script>')
        ui.add_head_html(f'<script src="https://mozilla.github.io/pdf.js/build/pdf_viewer.js"></script>')

    def load_pdf(self, pdf_url: str) -> None:
        self.run_method('load_pdf', pdf_url)

    def set_page(self, page_number: int) -> None:
        self.run_method('set_page', page_number)

