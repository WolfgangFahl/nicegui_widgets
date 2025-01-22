"""
Created on 2025-01-22

@author: wf
"""
import sys
from argparse import ArgumentParser
from ngwidgets.cmd import WebserverCmd
from ngwidgets.mbus_viewer_server import NiceMBusWebserver
from ngwidgets.mbus_viewer import MBusExamples

class NiceMBusCmd(WebserverCmd):
    """
    command line handling for ngwidgets
    """
    def getArgParser(self, description: str, version_msg) -> ArgumentParser:
            """
            override the default argparser call
            """
            parser = super().getArgParser(description, version_msg)
            parser.add_argument(
                "-rp",
                "--root_path",
                default=MBusExamples.examples_path(),
                help="path to mbux hex files [default: %(default)s]",
            )
            return parser


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