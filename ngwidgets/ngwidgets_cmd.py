'''
Created on 2023-09-10

@author: wf
'''
import sys
from ngwidgets.cmd import WebserverCmd
from ngwidgets.widgets_demo import Webserver

class NiceguiWidgetsCmd(WebserverCmd):
    """
    command line handling for ngwidgets
    """
    
def main(argv:list=None):
    """
    main call
    """
    cmd=NiceguiWidgetsCmd(config=Webserver.get_config(),webserver_cls=Webserver)
    exit_code=cmd.cmd_main(argv)
    return exit_code
        
DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())