"""
Created on 2023-09-13

@author: wf
"""
from nicegui import Client, ui

from ngwidgets.dict_edit import DictEdit
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.lod_grid import ListOfDictsGrid
from ngwidgets.pdfviewer import pdfviewer
from ngwidgets.version import Version
from ngwidgets.webserver import WebserverConfig
from ngwidgets.widgets import HideShow 

class NiceGuiWidgetsDemoWebserver(InputWebserver):
    """
    webserver to demonstrate ngwidgets capabilities
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        copy_right = "(c)2023 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right, version=Version(), default_port=9856
        )
        return config

    def __init__(self):
        """
        Constructor
        """
        InputWebserver.__init__(self, config=NiceGuiWidgetsDemoWebserver.get_config())
        # pdf_url = "https://www.africau.edu/images/default/sample.pdf"
        self.pdf_url = "https://raw.githubusercontent.com/mozilla/pdf.js/ba2edeae/web/compressed.tracemonkey-pldi-09.pdf"
        self.timeout = 6.0

        @ui.page("/dictedit")
        async def show_dictedit(client: Client):
            await client.connected(timeout=self.timeout)
            return await self.show_dictedit()

        @ui.page("/grid")
        async def show_grid(client: Client):
            await client.connected(timeout=self.timeout)
            return await self.show_grid()

        @ui.page("/hideshow")
        async def show_hide_show(client: Client):
            await client.connected(timeout=self.timeout)
            return await self.show_hide_show_demo()

        @ui.page("/pdfviewer")
        async def show_pdf_viewer(client: Client):
            await client.connected(timeout=self.timeout)
            return await self.show_pdf_viewer()

    async def load_pdf(self):
        self.pdf_viewer.load_pdf(self.pdf_url)

    #    slider = ui.slider(min=1, max=max_pages, value=1)  # PDF pages usually start from 1
    #    slider_label = ui.label().bind_text_from(slider, 'value')
    # def update_page(e):
    #    viewer.set_page(e.value)

    async def show_pdf_viewer(self):
        def show():
            self.pdf_viewer = pdfviewer(debug=self.args.debug).classes("w-full h-96")
            self.tool_button(tooltip="reload", icon="refresh", handler=self.load_pdf)

        await self.setup_content_div(show)

    async def show_grid(self):
        lod = [
            {"name": "Alice", "age": 18, "parent": "David"},
            {"name": "Bob", "age": 21, "parent": "Eve"},
            {"name": "Carol", "age": 42, "parent": "Frank"},
        ]

        def show():
            self.lod_grid = ListOfDictsGrid(lod=lod, key_col="name")

        await self.setup_content_div(show)

    async def show_dictedit(self):
        """
        show the DictEdit example
        """
        sample_dict = {"name": "Alice", "age": 30, "is_student": False}

        def show():
            with ui.card() as _card:
                DictEdit(sample_dict)

        await self.setup_content_div(show)

    async def show_hide_show_demo(self):
        """
        Demonstrate the HideShow component.
        """

        def show():
            hide_show_section = HideShow(("Hide", "Show More"))
            with hide_show_section.content_div:
                ui.label("This is the hidden content. Click the button to hide/show this text.")

        await self.setup_content_div(show)

    async def home(self, _client: Client):
        """
        provide the main content page
        """

        def setup_home():
            ui.html(
                    """<ul>
        <li><a href='/dictedit'>dictedit</a></li>
        <li><a href='/grid'>grid</a></li>
        <li><a href='/hideshow'>HideShow Demo</a></li>
        <li><a href='/pdfviewer'>pdfviewer</a></li>
        </ul>
        """
            )

        await self.setup_content_div(setup_home)
