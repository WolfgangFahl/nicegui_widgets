'''
Created on 2023-09-13

@author: wf
'''
from nicegui import ui
from dataclasses import dataclass

@dataclass
class ColorSchema:
    """
    a nicegui color schema
    """
    primary:str='#5898d4',
    secondary:str='#26a69a',
    accent:str='#9c27b0',
    dark:str='#1d1d1d',
    positive:str='#21ba45',
    negative:str='#c10015',
    info:str='#31ccec',
    warning:str='#f2c037'
    
    def apply(self):
        """
         Apply this color schema to the current UI theme.
        """
        ui.colors(
            primary=self.primary,
            secondary=self.secondary,
            accent=self.accent,
            dark=self.dark,
            positive=self.positive,
            negative=self.negative,
            info=self.info,
            warning=self.warning
        )
            
    @classmethod
    def indigo(cls):
        """
        Return a color schema for the Indigo color palette from Material Palette.
        see https://www.materialpalette.com/indigo/indigo
        """
        color_schema=cls(
            primary='#3F51B5',
            secondary='#5C6BC0',
            accent='#8A72AC',
            dark='#1A237E',
            positive='#28A745',
            negative='#D32F2F',
            info='#536DFE',
            warning='#FFB74D'
        )
        return color_schema