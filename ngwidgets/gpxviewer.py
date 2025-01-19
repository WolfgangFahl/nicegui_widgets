"""
Created on 2025-01-17

@author: wf
"""

import argparse
import re
import gpxpy
import requests

from ngwidgets.leaflet_map import LeafletMap


class GPXViewer:
    """
    display a given gpx file
    """
    samples = {
        "Mountain bike loop at Middlesex Fells reservation.": "https://www.topografix.com/fells_loop.gpx",
        "Via Verde de Arditurri": "https://www.bahntrassenradwege.de/images/Spanien/Baskenland/V-v-de-arditurri/Arditurri2.gpx",
        "Vía Verde del Fc Vasco Navarro": "https://ebike.bitplan.com/images/ebike/e/ec/VV-del-FC-Vasco-Navarro_fdmi1644.gpx"
    }
    default_center=[51.4934, 0.0098] # greenwich
    default_zoom=11

    @classmethod
    def get_parser(cls):
        """
        Configure and return argument parser
        """
        parser = argparse.ArgumentParser(description="GPX File Viewer")
        parser.add_argument("--gpx", required=False, help="URL or path to GPX file")
        parser.add_argument(
            "--token", required=False, help="Authentication token for GPX access"
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8080,
            help="Port to run server on (default: 8080)",
        )
        parser.add_argument("--zoom", type=int, default=GPXViewer.default_zoom, help="zoom level (default: 11)")
        parser.add_argument("--center", nargs=2, type=float, default=GPXViewer.default_center, help="center lat,lon - default: Greenwich")

        parser.add_argument("--debug", action="store_true", help="Show debug output")
        return parser

    @classmethod
    def from_url(cls, gpx_url) -> "GPXViewer":
        viewer = cls()
        viewer.load_gpx(gpx_url)
        return viewer

    def __init__(self, args: argparse.Namespace = None):
        """
        constructor

        Args:
            args(argparse.Namespace): command line arguments
        """
        self.args = args
        self.points = []
        if args:
            self.debug = args.debug
            self.token = args.token
            self.center = args.center
            self.zoom = args.zoom
            if self.args.gpx:
                self.load_gpx(self.args.gpx)
        else:
            self.zoom=GPXViewer.default_zoom
            self.center=GPXViewer.default_center

    def load_gpx(self, gpx_url: str):
        """
        load the given gpx file
        """
        response = requests.get(gpx_url)
        self.gpx = gpxpy.parse(response.text)
        self.get_points(self.gpx)
        return self.gpx

    def get_points(self,gpx,way_points_fallback:bool=False):
        """
        get the points for the given gpx track
        """
        self.points = []
        # routes
        for route in gpx.routes:
            for point in route.points:
                self.points.append((point.latitude, point.longitude))
        # tracks
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self.points.append((point.latitude, point.longitude))
        # Handle waypoints if no points were found and fallback is active
        if not self.points and gpx.waypoints and way_points_fallback:
            for waypoint in gpx.waypoints:
                self.points.append((waypoint.latitude, waypoint.longitude))

                # create map centered on first point
        if self.points:
            lats, lons = zip(*self.points)
            self.bounding_box = (min(lats), max(lats), min(lons), max(lons))
            self.center = ((min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2)

    def parse_lines(self, lines: str):
        """
        Parse the 'lines' parameter into route segments.

        Args:
            lines (str): The input string containing routes in the format:
                "By bike: 51.243931° N, 6.520022° E, 51.269222° N, 6.625467° E:"

        Returns:
            list of list of tuples: Parsed routes as lists of (lat, lon) tuples.

        Raises:
            ValueError: If the input format is invalid.
        """
        # Match segments like "51.243931° N, 6.520022° E"
        coordinate_pattern = r"(\d+\.\d+)° ([NS]), (\d+\.\d+)° ([EW])"

        # Extract individual routes
        route_segments = lines.split(":")
        routes = []

        for segment in route_segments:
            points = re.findall(coordinate_pattern, segment)
            if points:
                route = [
                    (
                        float(lat) * (-1 if ns == "S" else 1),
                        float(lon) * (-1 if ew == "W" else 1)
                    )
                    for lat, ns, lon, ew in points
                ]
                routes.append(route)

        if not routes:
            raise ValueError("No valid routes found in the input lines.")

        return routes


    def parse_lines_and_show(self, lines: str, zoom: int = None):
        """
        Parse lines and display them on the map.
        """
        routes = self.parse_lines(lines)
        self.points = [point for route in routes for point in route]
        self.show(zoom=zoom)
    def show(self,zoom:int=None,center=None):
        """
        show my points
        """
        if zoom is None:
            zoom=self.zoom
        if center is None:
            center=self.center
        self.map = LeafletMap(center=center, zoom=zoom)
        self.map.draw_path(self.points)
