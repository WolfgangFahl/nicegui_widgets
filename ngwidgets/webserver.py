'''
Created on 2023-09-10

@author: wf
'''
from nicegui import ui, core
import os
import sys
import traceback
from typing import Optional, Union, Any, Dict, List
import urllib.request
from dataclasses import dataclass
from ngwidgets.version import Version
from ngwidgets.color_schema import ColorSchema
from pydevd_file_utils import setup_client_server_paths

@dataclass
class WebserverConfig:
    """
    configuration of a webserver
    """
    copy_right:str="(c) 2023 Wolfgang Fahl"
    default_port:int=9860
    version:Version=None
    color_schema:ColorSchema=ColorSchema.indigo()
    
class NiceGuiWebserver(object):
    '''
    a basic NiceGuiWebserver
    '''

    def __init__(self,config:WebserverConfig=None):
        '''
        Constructor
        '''
        self.debug=False
        self.log_view=None
        self.do_trace=True
        if config is None:
            config=WebserverConfig()
        self.config=config
        self.app=core.app
        
    @classmethod    
    def optionalDebug(self,args):   
        '''
        start the remote debugger if the arguments specify so
        
        Args:
            args(): The command line arguments
        '''
        if args.debugServer:
            import pydevd
            print (f"remotePath: {args.debugRemotePath} localPath:{args.debugLocalPath}",flush=True)
            if args.debugRemotePath and args.debugLocalPath:
                MY_PATHS_FROM_ECLIPSE_TO_PYTHON = [
                    (args.debugRemotePath, args.debugLocalPath),
                ]
                setup_client_server_paths(MY_PATHS_FROM_ECLIPSE_TO_PYTHON)
                    #os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]='[["%s", "%s"]]' % (remotePath,localPath)
                    #print("trying to debug with PATHS_FROM_ECLIPSE_TO_PYTHON=%s" % os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]);
         
            pydevd.settrace(args.debugServer, port=args.debugPort,stdoutToServer=True, stderrToServer=True)
            print(f"command line args are: {str(sys.argv)}")
        
    def run(self, args):
        """
        Runs the UI of the web server.

        Args:
            args (list): The command line arguments.
        """
        self.args=args
        self.debug=args.debug
        self.optionalDebug(args)
        # allow app specific configuration steps
        self.configure_run()
        storage_secret=getattr(args, "storage_secret",None)
        ui.run(title=self.config.version.name, host=args.host, port=args.port, show=args.client,reload=False,storage_secret=storage_secret)
 
    def stop(self):
        """
        stop the server
        """       
        
    def handle_exception(self, e: BaseException, trace: Optional[bool] = False):
        """Handles an exception by creating an error message.

        Args:
            e (BaseException): The exception to handle.
            trace (bool, optional): Whether to include the traceback in the error message. Default is False.
        """
        if trace:
            self.error_msg = str(e) + "\n" + traceback.format_exc()
        else:
            self.error_msg = str(e)
        if self.log_view:
            self.log_view.push(self.error_msg)
        print(self.error_msg,file=sys.stderr)
        
    def link_button(self, name: str, target: str, icon_name: str,new_tab:bool=True):
        """
        Creates a button with a specified icon that opens a target URL upon being clicked.
    
        Args:
            name (str): The name to be displayed on the button.
            target (str): The target URL that should be opened when the button is clicked.
            icon_name (str): The name of the icon to be displayed on the button.
            new_tab(bool): if True open link in new tab
    
        Returns:
            The button object.
            
            
        see https://fonts.google.com/icons?icon.set=Material+Icons for potential icon names
        """
        with ui.button(name,icon=icon_name) as button:
            button.on("click",lambda: (ui.open(target,new_tab=new_tab)))
        return button
        
    
    def tool_button(self,tooltip:str,icon:str,handler:callable=None,toggle_icon:str=None)->ui.button:
        """
        Creates an  button with icon that triggers a specified function upon being clicked.
    
        Args:
            tooltip (str): The tooltip to be displayed.
            icon (str): The name of the icon to be displayed on the button.
            handler (function): The function to be called when the button is clicked.
            toggle_icon (str): The name of an alternative icon to be displayed when the button is clicked.
    
        Returns:
            ui.button: The icon button object.
            
        valid icons may be found at:    
            https://fonts.google.com/icons
        """
        icon_button=ui.button("",icon=icon, color='primary').tooltip(tooltip).on("click",handler=handler)  
        icon_button.toggle_icon=toggle_icon
        return icon_button   
    
    def toggle_icon(self,button:ui.button):
        """
        toggle the icon of the given button
        
        Args:
            ui.button: the button that needs the icon to be toggled
        """
        if hasattr(button,"toggle_icon"):
            # exchange icon with toggle icon
            toggle_icon=button._props["icon"]
            icon=button.toggle_icon
            button._props["icon"]=icon
            button.toggle_icon=toggle_icon
        button.update()

    def add_select(self, title: str, selection: Union[List[Any], Dict[str, Any]],background_color:str="#e6e6e6") -> Any:
        """
        Add a select widget.
    
        Args:
            title (str): The title/label for the select widget.
            selection (Union[List[Any], Dict[str, Any]]): The options available for selection.
                It can either be a list of options or a dictionary with option labels as keys
                and values as the corresponding values.
    
        Returns:
            Any: The created select widget.
        """
        with ui.element('div').style("display: flex; align-items: center;"):
            if background_color:
                background_style=f"background-color:{background_color};"
            else:
                background_style=""
            ui.label(title).classes("rounded p-2").style(f"margin-right:10px;{background_style}")  # add some space between label and select
            s = ui.select(selection)
            return s
       
    def do_read_input(self, input_str: str)->str:
        """Reads the given input.

        Args:
            input_str (str): The input string representing a URL or local path.
            
        Returns:
            str: the input content as a string
        """
        if input_str.startswith('http://') or input_str.startswith('https://'):
            with urllib.request.urlopen(input_str) as response:
                text= response.read().decode('utf-8')
                return text
        else:
            if os.path.exists(input_str):
                with open(input_str, 'r') as file:
                    return file.read()
            else:
                raise Exception(f'File does not exist: {input_str}')
    
    async def setup_footer(self):
        """
        setup the footer
        """
        with ui.footer() as self.footer:
            ui.label(self.config.copy_right)
            ui.link("Powered by nicegui","https://nicegui.io/").style("color: #fff") 