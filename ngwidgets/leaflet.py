"""
(Re) Created on 2024-12-03

compatibility layer

@author: wf
"""
from typing import List, Tuple
from nicegui import ui

class leaflet(ui.leaflet):
    """Leaflet map wrapper for backwards compatibility with older nicegui versions"""

    def __init__(self, version: str = "1.7.1") -> None:
        """Initialize map with default center and zoom
        Args:
            version: Kept for backwards compatibility, not used"""
        super().__init__(center=(0.0, 0.0), zoom=9)
        self._path_layer = None

    def set_location(self, location: Tuple[float, float], zoom_level: int = 9) -> None:
        """Set map center and zoom
        Args:
            location: (latitude, longitude) tuple
            zoom_level: Zoom level 1-18"""
        self.center = location
        self.zoom = zoom_level

    def set_zoom_level(self, zoom_level: int) -> None:
        """Set map zoom level
        Args:
            zoom_level: Zoom level 1-18"""
        self.zoom = zoom_level

    def draw_path(self, path: List[Tuple[float, float]]) -> None:
        """Draw path on map
        Args:
            path: List of (lat, lon) points"""
        if self._path_layer:
            self.remove_layer(self._path_layer)
        self._path_layer = self.generic_layer({
            'type': 'polyline',
            'latLngs': path,
            'options': {'color': 'red', 'weight': 3, 'opacity': 0.7}
        })