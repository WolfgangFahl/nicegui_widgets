'''
Created on 2023-09-13

@author: wf
'''
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from ngwidgets.version import Version

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
 
        
    
        