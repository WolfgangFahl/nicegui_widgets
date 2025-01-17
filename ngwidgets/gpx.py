#!/usr/bin/env python
"""
Created on 2025-01-17

@author: wf
"""
from nicegui import ui
from ngwidgets.leaflet_map import LeafletMap
import argparse
import gpxpy
import requests

class GPXViewer:
    """
    display a given gpx file
    """

    @classmethod
    def get_parser(cls):
        """
        Configure and return argument parser
        """
        parser = argparse.ArgumentParser(description='GPX File Viewer')
        parser.add_argument('--gpx', required=True,
            help='URL or path to GPX file')
        parser.add_argument('--debug', action='store_true',
            help='Show debug output')
        return parser

    @classmethod
    def from_url(cls,gpx_url)->"GPXViewer":
        viewer=cls()
        viewer.load_gpx(gpx_url)
        return viewer

    def __init__(self, args:argparse.Namespace=None):
        """
        constructor

        Args:
            args(argparse.Namespace): command line arguments
        """
        self.args = args
        if args:
            self.debug = args.debug
            self.load_gpx(self.args.gpx)

    def load_gpx(self,gpx_url:str):
        """
        load the given gpx file
        """
        response = requests.get(gpx_url)
        self.gpx = gpxpy.parse(response.text)
        return self.gpx

    def show(self):
        # get points from first track
        self.points = []
        for track in self.gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self.points.append((point.latitude, point.longitude))
        # create map centered on first point
        center = self.points[0] if self.points else (50.93, 6.95)
        self.map = LeafletMap(center=center, zoom=11)
        # draw the track
        self.map.draw_path(self.points)


@ui.page('/')
def home(gpx: str = None):
    """
    home page with optional gpx parameter
    """
    gpx_to_use = gpx if gpx else args.gpx if args else None
    if gpx_to_use:
        viewer = GPXViewer.from_url(gpx_to_use)
        viewer.show()
    else:
        ui.label('Please provide a gpx parameter via command line or gpx=param')


if __name__ in {"__main__", "__mp_main__"}:
    parser = GPXViewer.get_parser()
    args = parser.parse_args()
    viewer = GPXViewer(args=args)
    viewer.show()

ui.run(title='GPX Viewer')