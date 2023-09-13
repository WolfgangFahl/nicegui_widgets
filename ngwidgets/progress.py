'''
Created on 2023-09-12

@author: wf
'''
from tqdm import tqdm
from nicegui import ui
from dataclasses import dataclass

@dataclass
class Progressbar():
    """
    generic progress bar 
    """
    total: int
    desc: str
    unit: str
  
class NiceguiProgressbar(Progressbar):
    """
    nicegui progess bar wrapper
    """

    def __init__(self,total,desc,unit):
        Progressbar.__init__(self,total,desc,unit)
        self.value=0
        self.progress = ui.linear_progress(value=0).props('instant-feedback')
        self.progress.visible = False
        
    def reset(self):
        self.progress.set_value(0)
        
    def set_description(self,desc:str):
        """
        set the description of the progress bar
        """
        self.progress.visible=True
        pass
        
    def update(self,step):
        """
        update the progress bar
        """
        self.value+=1
        self.progress.visible=True
        percent=self.value/self.total
        self.progress.value=percent  #round(percent*100)
        pass
    
class TqdmProgressbar(Progressbar):
    """
    tqdm progress bar wrapper
    """
    
    def __init__(self,total,desc,unit):
        """
        constructor
        """
        Progressbar.__init__(self,total,desc,unit)
        self.reset()
        
    def reset(self):
        self.progress=tqdm(total=self.total, desc=self.desc, unit=self.unit)
        
    def set_description(self,desc:str):
        self.progress.set_description(desc)
        
    def update(self,step):
        self.progress.update(step)
    