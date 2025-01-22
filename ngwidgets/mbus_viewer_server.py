"""
Created on 22.01.2025

@author: wf
"""

import os

from nicegui import Client

import ngwidgets
from ngwidgets.input_webserver import InputWebserver, InputWebSolution, WebserverConfig
from ngwidgets.mbus_viewer import MBusExamples, MBusViewer
from ngwidgets.yamlable import lod_storable


@lod_storable
class Version:
    """
    Version handling for nicegui widgets
    """

    name = "mbus-viewer"
    version = ngwidgets.__version__
    date = "2025-01-22"
    updated = "2025-01-22"
    description = "MBus message parser and JSON result viewer"

    authors = "Wolfgang Fahl"

    doc_url = "https://wiki.bitplan.com/index.php/MBus_Viewer"
    chat_url = "https://github.com/WolfgangFahl/nicegui_widgets/discussions"
    cm_url = "https://github.com/WolfgangFahl/nicegui_widgets"

    license = f"""Copyright 2025 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""

    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""


class NiceMBusWebserver(InputWebserver):
    """
    webserver to demonstrate ngwidgets capabilities
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        copy_right = "(c)2025 Wolfgang Fahl"
        config = WebserverConfig(
            short_name="mbus_viewer",
            timeout=6.0,
            copy_right=copy_right,
            version=Version(),
            default_port=9853,
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = NiceMBus
        return server_config

    def __init__(self):
        """
        Constructor
        """
        InputWebserver.__init__(self, config=NiceMBusWebserver.get_config())
        pass

    def configure_run(self):
        root_path = (
            self.args.root_path if self.args.root_path else MBusExamples.examples_path()
        )
        self.root_path = os.path.abspath(root_path)
        self.allowed_urls = [
            "https://raw.githubusercontent.com/WolfgangFahl/nicescad/main/examples/",
            "https://raw.githubusercontent.com/openscad/openscad/master/examples/",
            self.root_path,
        ]


class NiceMBus(InputWebSolution):
    """ """

    def __init__(self, webserver: "NiceMBusWebserver", client: Client):
        super().__init__(webserver, client)

    async def home(self):
        """
        provide the main content page
        """

        def setup_home():
            viewer = MBusViewer(solution=self)
            viewer.setup_ui()

        await self.setup_content_div(setup_home)
