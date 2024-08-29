"""
Created on 2023-09-10

@author: wf
"""

# avoid ugly deprecation messages see
# https://stackoverflow.com/questions/879173/how-to-ignore-deprecation-warnings-in-python
# and
import shutup

shutup.please()
import sys
import traceback
import webbrowser
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime

from ngwidgets.webserver import WebserverConfig


class WebserverCmd(object):
    """
    Baseclass for command line handling of Webservers
    """

    def __init__(self, config: WebserverConfig, webserver_cls, debug: bool = False):
        """
        constructor
        """
        self.config = config
        self.version = config.version
        self.debug = debug
        self.webserver_cls = webserver_cls
        self.exit_code = 0

    def getArgParser(self, description: str = None, version_msg=None) -> ArgumentParser:
        """
        Setup command line argument parser

        Args:
            description(str): the description
            version_msg(str): the version message

        Returns:
            ArgumentParser: the argument parser
        """
        if description is None:
            description = self.version.description
        if version_msg is None:
            version_msg = self.program_version_message
        parser = ArgumentParser(
            description=description, formatter_class=RawDescriptionHelpFormatter
        )
        parser.add_argument(
            "-a",
            "--about",
            help="show about info [default: %(default)s]",
            action="store_true",
        )
        parser.add_argument(
            "--apache",
            help="create an apache configuration file for the given domain",
        )
        parser.add_argument(
            "-c",
            "--client",
            action="store_true",
            help="start client [default: %(default)s]",
        )
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            help="show debug info [default: %(default)s]",
        )
        parser.add_argument("--debugServer", help="remote debug Server")
        parser.add_argument(
            "--debugPort", type=int, help="remote debug Port", default=5678
        )
        parser.add_argument(
            "--debugRemotePath",
            help="remote debug Server path mapping - remotePath - path on debug server",
        )
        parser.add_argument(
            "--debugLocalPath",
            help="remote debug Server path mapping - localPath - path on machine where python runs",
        )

        parser.add_argument(
            "-l",
            "--local",
            action="store_true",
            help="run with local file system access [default: %(default)s]",
        )
        parser.add_argument("-i", "--input", help="input file")

        parser.add_argument(
            "-rol",
            "--render_on_load",
            action="store_true",
            help="render on load [default: %(default)s]",
        )

        parser.add_argument(
            "--host",
            default="localhost",
            help="the host to serve / listen from [default: %(default)s]",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=self.config.default_port,
            help="the port to serve from [default: %(default)s]",
        )
        parser.add_argument(
            "-s",
            "--serve",
            action="store_true",
            help="start webserver [default: %(default)s]",
        )
        parser.add_argument("-V", "--version", action="version", version=version_msg)
        return parser

    def handle_args(self) -> bool:
        handled = False
        if self.args.apache:
            print(self.to_apache_config(self.config, self.args.apache))
        if self.args.about:
            print(self.program_version_message)
            print(f"see {self.version.doc_url}")
            webbrowser.open(self.version.doc_url)
            handled = True
        if self.args.client:
            url = f"http://{self.args.host}:{self.args.port}"
            webbrowser.open(url)
            handled = True
        if self.args.serve:
            # instantiate the webserver
            ws = self.webserver_cls()
            ws.run(self.args)
            handled = True
        return handled

    def to_apache_config(self, config: WebserverConfig, domain: str) -> str:
        """
        Generate Apache configuration based on the given WebserverConfig.

        Args:
            config (WebserverConfig): The webserver configuration object.
            domain(str): the base domain to use
        Returns:
            str: The Apache configuration as a string.
        """
        iso_timestamp = datetime.now().isoformat()
        server_name = f"{config.short_name}.{domain}"
        admin_email = f"webmaster@{domain}"
        version_info = ""
        if config.version:
            version_info = f"""{config.version.name} Version {config.version.version} of {config.version.updated} ({config.version.description})"""

        header_comment = f"""# Apache Configuration for {server_name}
# {version_info}
# Generated by WebserverCmd at {iso_timestamp}
# http Port: {config.default_port}
# SSL Port: 443
# {config.copy_right}
# timeout: {config.timeout}
"""

        template = """<VirtualHost *:{port}>
    ServerName {server_name}
    ServerAdmin {admin_email}

    {ssl_config_part}
    ErrorLog ${{APACHE_LOG_DIR}}/{short_name}_error{log_suffix}.log
    CustomLog ${{APACHE_LOG_DIR}}/{short_name}{log_suffix}.log combined

    RewriteEngine On
    RewriteCond %{{HTTP:Upgrade}} =websocket [NC]
    RewriteRule /(.*) ws://localhost:{default_port}/$1 [P,L]
    RewriteCond %{{HTTP:Upgrade}} !=websocket [NC]
    RewriteRule /(.*) http://localhost:{default_port}/$1 [P,L]

    ProxyPassReverse / http://localhost:{default_port}/
</VirtualHost>
"""

        # For SSL Configuration
        ssl_config = template.format(
            port=443,
            server_name=server_name,
            admin_email=admin_email,
            short_name=config.short_name,
            log_suffix="_ssl",
            default_port=config.default_port,
            ssl_config_part="Include ssl.conf",
        )

        # For Non-SSL Configuration
        http_config = template.format(
            port=80,
            server_name=server_name,
            admin_email=admin_email,
            short_name=config.short_name,
            log_suffix="",
            default_port=config.default_port,
            ssl_config_part="",
        )

        apache_config = header_comment + ssl_config + http_config
        return apache_config

    def cmd_parse(self, argv: list = None):
        """
        parse the argument lists and prepare

        Args:
            argv(list): list of command line arguments

        """
        if argv is None:
            argv = sys.argv[1:]
        self.argv = argv
        self.program_name = self.version.name
        self.program_version = f"v{self.version.version}"
        self.program_build_date = str(self.version.date)
        self.program_version_message = (
            f"{self.program_name} ({self.program_version},{self.program_build_date})"
        )
        self.parser = self.getArgParser(
            description=self.version.description,
            version_msg=self.program_version_message,
        )
        self.args = self.parser.parse_args(argv)
        return self.args

    def cmd_main(self, argv: None) -> int:
        """
        main program as an instance

        Args:
            argv(list): list of command line arguments

        Returns:
            int: exit code - 0 of all went well 1 for keyboard interrupt and 2 for exceptions
        """
        try:
            self.cmd_parse(argv)
            if len(self.argv) < 1:
                self.parser.print_usage()
                sys.exit(1)
            self.handle_args()
        except KeyboardInterrupt:
            ### handle keyboard interrupt ###
            self.exit_code = 1
        except Exception as e:
            if self.debug:
                raise (e)
            indent = len(self.program_name) * " "
            sys.stderr.write(self.program_name + ": " + repr(e) + "\n")
            sys.stderr.write(indent + "  for help use --help")
            if self.args.debug:
                print(traceback.format_exc())
            self.exit_code = 2

        return self.exit_code
