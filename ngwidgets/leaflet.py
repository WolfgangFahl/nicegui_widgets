'''
https://github.com/zauberzeug/nicegui/blob/main/examples/map/leaflet.py

@author: rodja

modified 2023-08-16 to handle set_zoom and draw_path
@author: wf
'''
from typing import Tuple,List

from nicegui import ui


class leaflet(ui.element, component='leaflet.js'):
    """
    nicegui Leaflet integration
    
    see https://leafletjs.com/
    """

    def __init__(self,version="1.7.1") -> None:
        super().__init__()
        ui.add_head_html(f'<link href="https://unpkg.com/leaflet@{version}/dist/leaflet.css" rel="stylesheet"/>')
        ui.add_head_html(f'<script src="https://unpkg.com/leaflet@{version}/dist/leaflet.js"></script>')

    def set_location(self, location: Tuple[float, float], zoom_level:int=9) -> None:
        lat,lon=location
        self.run_method('set_location',lat,lon,zoom_level)
        
    def set_zoom_level(self,zoom_level:int):
        self.run_method("set_zoom_level",zoom_level)
        
    def draw_path(self, path: List[Tuple[float, float]]) -> None:
        """Draw a path on the map based on list of lat-long tuples."""
        self.run_method('draw_path', path)