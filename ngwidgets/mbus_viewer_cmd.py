"""
Created on 2025-01-22

@author: wf
"""

import sys

from ngwidgets.cmd import WebserverCmd
from ngwidgets.mbus_viewer_server import NiceMBusWebserver


class NiceMBusCmd(WebserverCmd):
    """
    command line handling for ngwidgets
    """


def main(argv: list = None):
    """
    main call
    """
    cmd = NiceMBusCmd(
        config=NiceMBusWebserver.get_config(),
        webserver_cls=NiceMBusWebserver,
    )
    exit_code = cmd.cmd_main(argv)
    return exit_code


DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())