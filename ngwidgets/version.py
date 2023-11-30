'''
Created on 2023-09-12

@author: wf
'''
import ngwidgets
from dataclasses import dataclass

@dataclass
class Version:
    """
    Version handling for nicegui widgets
    """
    name = "ngwidgets"
    version = ngwidgets.__version__
    date = '2023-09-10'
    updated = '2023-11-30'
    description = 'NiceGUI widgets'
    
    authors = 'Wolfgang Fahl'
    
    doc_url="https://wiki.bitplan.com/index.php/Nicegui_widgets"
    chat_url="https://github.com/WolfgangFahl/nicegui_widgets/discussions"
    cm_url="https://github.com/WolfgangFahl/nicegui_widgets"

    license = f'''Copyright 2023 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.'''
    
    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""
