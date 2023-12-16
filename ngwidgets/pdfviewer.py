"""
Created on 2023-09-17

@author: wf
"""

from dataclasses import dataclass

from nicegui import ui


@dataclass
class pdfjs_urls:
    """
    see https://mozilla.github.io/pdf.js/getting_started/#download

    setup the content delivery network urls
    """

    cdn: str = "jsdelivr"
    version: str = "3.10.111"
    debug: bool = False
    url = {}

    def configure(self):
        """ """
        version = self.version
        dot_min = "" if self.debug else ".min"
        # where to find library, css and
        l = "build/"
        c = "web/"
        v = l
        js = "pdf"
        if self.cdn == "github":
            self.base_url = "https://raw.githubusercontent.com/mozilla/pdf.js/master"
            l = c
            v = c
            # no minimized version available
            dot_min = ""
            js = "pdfjs"
        elif self.cdn == "cdnjs":
            self.base_url = f"https://cdnjs.cloudflare.com/ajax/libs/pdf.js/{version}"
            c = ""
            v = ""
            l = ""
        elif self.cdn == "jsdelivr":
            self.base_url = f"https://cdn.jsdelivr.net/npm/pdfjs-dist@{version}"
            v = c
        elif self.cdn == "unpkg":
            # no minimized version available
            dot_min = ""
            v = c
            self.base_url = f"https://unpkg.com/pdfjs-dist@{version}"
        else:
            raise ValueError(f"unknown cdn {self.cdn}")
        css = f"pdf_viewer{dot_min}.css"
        lib = f"{js}{dot_min}.js"
        viewer = f"pdf_viewer{dot_min}.js"
        self.url["css"] = f"{self.base_url}/{c}{css}"
        self.url["js_lib"] = f"{self.base_url}/{l}{lib}"
        self.url["js_viewer"] = f"{self.base_url}/{v}{viewer}"


class pdfviewer(ui.element, component="pdfviewer.js"):
    """
    nicegui PDF.js integration

    see https://mozilla.github.io/pdf.js/
    """

    def __init__(
        self, version: str = "3.11.174", cdn="cdnjs", debug: bool = False
    ) -> None:
        """
        constructor
        """
        super().__init__()

        self.version = version
        self.debug = debug
        self.urls = pdfjs_urls(cdn, version, debug)
        self.urls.configure()

        ui.add_head_html(f"""<link href="{self.urls.url['css']}" rel="stylesheet"/>""")
        ui.add_head_html(f"""<script src="{self.urls.url['js_lib']}"></script>""")
        ui.add_head_html(f"""<script src="{self.urls.url['js_viewer']}"></script>""")
        viewer_container_style = """<style>
  .pdfViewerContainer {
    overflow: auto;
    position: absolute;
    width: 100%;
    height: 100%;
  }
</style>"""
        ui.add_head_html(viewer_container_style)

    def load_pdf(self, pdf_url: str) -> None:
        self.run_method("load_pdf", pdf_url)

    def set_page(self, page_number: int) -> None:
        self.run_method("set_page", page_number)
