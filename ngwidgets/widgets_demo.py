'''
Created on 2023-09-13

@author: wf
'''
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from ngwidgets.version import Version
from ngwidgets.pdfviewer import pdfviewer
from nicegui import ui,Client

class Webserver(InputWebserver):
    '''
    webserver to demonstrate ngwidgets capabilities
    '''

    @classmethod
    def get_config(cls)->WebserverConfig:
        copy_right="(c)2023 Wolfgang Fahl"
        config=WebserverConfig(copy_right=copy_right,version=Version(),default_port=9859)
        return config
    
    def __init__(self):
        '''
        Constructor
        '''
        InputWebserver.__init__(self,config=Webserver.get_config())
 
        @ui.page('/')
        async def home(client: Client):
            return await self.home(client)
    
    def setup_pdf_viewer(self):   
        """
        try pdf view
        """
        viewer = pdfviewer().classes('w-full h-96')
        pdf_url = "https://www.africau.edu/images/default/sample.pdf"
        viewer.load_pdf(pdf_url)
    #    slider = ui.slider(min=1, max=max_pages, value=1)  # PDF pages usually start from 1
    #    slider_label = ui.label().bind_text_from(slider, 'value')
    #def update_page(e):
    #    viewer.set_page(e.value)   
         
 
    async def home(self,_client:Client):
        """
        home page
        """    
        self.setup_menu()
        with ui.element("div").classes("w-full h-full"):
            self.setup_pdf_viewer()
        await self.setup_footer()
    
        