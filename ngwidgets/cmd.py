'''
Created on 10.09.2023

@author: wf
'''
import sys
import traceback
import webbrowser
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

class WebserverCmd(object):
    '''
    Baseclass for command line handling of Webservers
    '''
    
    def __init__(self,version,webserver_cls,debug:bool=False):
        """
        constructor
        """
        self.version=version
        self.debug=debug
        self.webserver_cls=webserver_cls
        
    def getArgParser(self,description:str,version_msg)->ArgumentParser:
        """
        Setup command line argument parser
        
        Args:
            description(str): the description
            version_msg(str): the version message
            
        Returns:
            ArgumentParser: the argument parser
        """
        parser = ArgumentParser(description=description, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-a","--about",help="show about info [default: %(default)s]",action="store_true")
        parser.add_argument("-c","--client", action="store_true", help="start client [default: %(default)s]")
        parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="show debug info [default: %(default)s]")
        parser.add_argument("-l", "--local", dest="local", action="store_true", help="run with local file system access [default: %(default)s]")
        parser.add_argument("-i", "--input", help="input file")
        parser.add_argument("-rol","--render_on_load", action="store_true", help="render on load [default: %(default)s]")
    
        parser.add_argument("--host", default="localhost",
                                help="the host to serve / listen from [default: %(default)s]")
        parser.add_argument("--port",type=int,default=9859,help="the port to serve from [default: %(default)s]")
        parser.add_argument("-s","--serve", action="store_true", help="start webserver [default: %(default)s]")
        parser.add_argument("-V", "--version", action='version', version=version_msg)
        return parser

    def cmd_main(self,argv=None): 
        '''main program as an instance'''
    
        if argv is None:
            argv=sys.argv[1:]
            
        program_name = self.version.name
        program_version =f"v{self.version.version}" 
        program_build_date = str(self.version.date)
        program_version_message = f'{program_name} ({program_version},{program_build_date})'
    
        try:
            parser=self.getArgParser(description=self.version.license,version_msg=program_version_message)
            args = parser.parse_args(argv)
            if len(argv) < 1:
                parser.print_usage()
                sys.exit(1)
            if args.about:
                print(program_version_message)
                print(f"see {self.version.doc_url}")
                webbrowser.open(self.version.doc_url)
            if args.client:
                url=f"http://{args.host}:{args.port}"
                webbrowser.open(url)
            if args.serve:
                # instantiate the webserver
                ws=self.webserver_cls()
                ws.run(args)
            
        except KeyboardInterrupt:
            ### handle keyboard interrupt ###
            return 1
        except Exception as e:
            if self.debug:
                raise(e)
            indent = len(program_name) * " "
            sys.stderr.write(program_name + ": " + repr(e) + "\n")
            sys.stderr.write(indent + "  for help use --help")
            if args.debug:
                print(traceback.format_exc())
            return 2       