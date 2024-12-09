"""
Created on 2024-12-07

@author: wf
"""
import logging
from nicegui import events, ui
from typing import Any, List, Tuple, Dict

class LeafletMap(ui.leaflet):
    """Enhanced Leaflet map with additional functionality"""

    def __init__(self,
        center: Tuple[float, float]=(51.505, -0.09),
        zoom: int=9,
        with_draw_control: bool=True,
        classes: str="w-full h-96",
        debug:bool=False):
        """Initialize enhanced map

        Args:
            center: Initial center coordinates as (lat,lon) tuple
            zoom: Initial zoom level
            with_draw_control: Whether to add the draw control
            classes: CSS classes to apply (default: h-96)
        """
        draw_control = {
            'draw': {
                'polygon': True,
                'marker': True,
                'circle': True,
                'rectangle': True,
                'polyline': True,
                'circlemarker': True,
            },
            'edit': {
                'edit': True,
                'remove': True,
            },
        } if with_draw_control else None

        super().__init__(center=center, zoom=zoom, draw_control=draw_control)
        self.debug=debug
        self.classes(classes)
        self.on('map-click', self._handle_click)
        self.on('draw:created', self._handle_draw)

    def _handle_click(self, e: events.GenericEventArguments):
        """Default click handler that adds a marker"""
        lat = e.args['latlng']['lat']
        lng = e.args['latlng']['lng']
        _marker = self.marker(latlng=(lat, lng))


    def _handle_draw(self, e: events.GenericEventArguments):
        """Default draw handler"""
        layer_type = e.args['layerType']
        coords = e.args['layer'].get('_latlng') or e.args['layer'].get('_latlngs')
        layer_id = e.args['layer'].get('_leaflet_id')
        msg=f'Drawn a {layer_type} with id {layer_id} at {coords}'
        if self.debug:
            logging.warn(msg)
        ui.notify(msg)

    def draw_path(self, path: List[Tuple[float, float]], options: Dict = None) -> Any:
        """Draw a polyline path on the map
        Args:
            path: List of (lat,lon) coordinate tuples
            options: Optional styling options for the polyline
        Returns:
            The created layer object
        """
        if options is None:
            options = {'color': 'red', 'weight': 3, 'opacity': 0.7}

        layer = self.generic_layer(name='polyline', args=[path, options])
        return layer