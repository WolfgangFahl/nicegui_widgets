'''
Created on 2023-09-10

@author: wf
'''
import sys
from ngwidgets.cmd import WebserverCmd
from ngwidgets.widgets_demo import NiceGuiWidgetsDemoWebserver

class NiceguiWidgetsCmd(WebserverCmd):
    """
    command line handling for ngwidgets
    """
    
def main(argv:list=None):
    """
    main call
    """
    cmd=NiceguiWidgetsCmd(config=NiceGuiWidgetsDemoWebserver.get_config(),webserver_cls=NiceGuiWidgetsDemoWebserver)
    exit_code=cmd.cmd_main(argv)
    return exit_code
        
DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())