'''
Created on 2023-09-12

@author: wf
'''
from tqdm import tqdm
from nicegui import ui

class NiceguiProgressbar():
    """
    nicegui progess bar wrapper
    """

    def __init__(self,total,desc,unit):
        self.total=total
        self.value=0
        self.desc=desc
        self.unit=unit
        self.progress = ui.linear_progress(value=0).props('instant-feedback')
        self.progress.visible = False
        
    def set_description(self,desc:str):
        self.progress.visible=True
        pass
        
    def update(self,step):
        self.value+=1
        self.progress.visible=True
        self.progress.value=self.value/self.total*100
        pass
    
class Progressbar():
    """
    tqdm progress bar wrapper
    """
    
    def __init__(self,total,desc,unit):
        """
        constructor
        """
        self.progress=tqdm(total=total, desc=desc, unit=unit)
        
    def set_description(self,desc:str):
        self.progress.set_description(desc)
        
    def update(self,step):
        self.progress.update(step)
    