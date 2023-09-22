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
    
    def __init__(self,version,font_size=24,font_family="Helvetica, Arial, sans-serif",**kwargs):
        """
        construct an about Div for the given version
        """
        def add(html,l,code):
            html += f'<div class="about_row"><div class="about_column1">{l}:</div><div class="about_column2">{code}</div></div>'
            return html
        super().__init__(tag='div',**kwargs)
        with self: 
            doc_link=Link.create(url=version.doc_url,text="documentation",target="_blank")
            disc_link=Link.create(url=version.chat_url,text="discussion",target="_blank")
            cm_link=Link.create(url=version.cm_url,text="source",target="_blank")
            max_label_length=7 # e.g. updated
            column1_width = font_size * max_label_length  # Approximate width calculation
            
            html = f'''<style>
                    .about_row {{
                        display: flex;
                        align-items: baseline;
                    }}
                    .about_column1 {{
                        font-weight: bold;
                        font-size: {font_size}px;
                        text-align: right;
                        width: {column1_width}px; 
                        padding-right: 10px;
                        font-family: {font_family};
                    }}
                    .about_column2 {{
                        font-size: {font_size}px;
                        font-family: {font_family};
                    }}
                    .about_column2 a {{
                        color: blue;
                        text-decoration: underline;
                    }}
               </style>'''
            html=add(html,"name",f"{version.name}")
            html=add(html,"purpose",f"{version.description}")
            html=add(html,"version",f"{version.version}")
            html=add(html,"since",f"{version.date}")
            html=add(html,"updated",f"{version.updated}")
            html=add(html,"authors",f"{version.authors}")
            html=add(html,"docs",doc_link)
            html=add(html,"chat",disc_link)
            html=add(html,"source",cm_link)
            ui.html(html)
    