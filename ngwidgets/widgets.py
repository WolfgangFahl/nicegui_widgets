"""
Created on 2023-09-10

common nicegui widgets and tools

@author: wf


"""
from nicegui import ui

class Link:
    '''
    a link
    '''
    @staticmethod
    def create(url,text,tooltip=None,target=None,style:str=None):
        '''
        create a link for the given url and text
        
        Args:
            url(str): the url
            text(str): the text
            tooltip(str): an optional tooltip
            target(str): e.g. _blank
            style(str): any style to be applied
        '''
        title="" if tooltip is None else f" title='{tooltip}'"
        target="" if target is None else f" target=' {target}'"
        style="" if style is None else f" style='{style}'" 
        link=f"<a href='{url}'{title}{target}{style}>{text}</a>"
        return link
    
class About(ui.element):
    """
    About Div for a given version
    """
    
    def __init__(self,version,**kwargs):
        """
        construct an about Div for the given version
        """
        super().__init__(tag='div',**kwargs)
        with self: 
            ui.label(f"{version.description}")
            ui.label(f"version: {version.version}")
            ui.label(f"updated: {version.updated}")
            ui.label(f"authors: {version.authors}")
            ui.html(Link.create(url=version.doc_url,text="documentation",target="_blank"))
            ui.html(Link.create(url=version.chat_url,text="discussion",target="_blank"))
            ui.html(Link.create(url=version.cm_url,text="source",target="_blank"))
    