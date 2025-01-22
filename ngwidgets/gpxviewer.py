"""
Created on 2025-01-17

@author: wf
"""

import argparse
import re
from typing import Optional

import gpxpy
import requests

from ngwidgets.leaflet_map import LeafletMap
from ngwidgets.tour import Leg, LegStyle, LegStyles, Loc, Tour


class GPXViewer:
    """
    display a given gpx file
    """

    samples = {
        "Mountain bike loop at Middlesex Fells reservation.": "https://www.topografix.com/fells_loop.gpx",
        "Via Verde de Arditurri": "https://www.bahntrassenradwege.de/images/Spanien/Baskenland/V-v-de-arditurri/Arditurri2.gpx",
        "Vía Verde del Fc Vasco Navarro": "https://ebike.bitplan.com/images/ebike/e/ec/VV-del-FC-Vasco-Navarro_fdmi1644.gpx",
    }
    default_center = [51.4934, 0.0098]  # greenwich
    default_zoom = 11

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
        parser.add_argument(
            "--zoom",
            type=int,
            default=GPXViewer.default_zoom,
            help="zoom level (default: 11)",
        )
        parser.add_argument(
            "--center",
            nargs=2,
            type=float,
            default=GPXViewer.default_center,
            help="center lat,lon - default: Greenwich",
        )
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
        self.tour = None
        self.leg_styles = LegStyles.default()
        self.set_center()
        if args:
            self.debug = args.debug
            self.token = args.token
            self.center = args.center
            self.zoom = args.zoom
            if self.args.gpx:
                self.load_gpx(self.args.gpx)
        else:
            self.zoom = GPXViewer.default_zoom
            self.center = GPXViewer.default_center

    def load_gpx(self, gpx_url: str):
        """
        load the given gpx file
        """
        response = requests.get(gpx_url)
        self.gpx = gpxpy.parse(response.text)
        self.get_points(self.gpx)
        return self.gpx

    def set_center(self):
        """
        Calculate and set the center and bounding box based on tour legs
        """

        if self.tour and self.tour.legs:
            points = []
            for leg in self.tour.legs:
                points.append(leg.start.coordinates)
                points.append(leg.end.coordinates)
            # Wrong order: lats, lons need to be extracted after zipping
            lats = [p[0] for p in points]
            lons = [p[1] for p in points]
            self.bounding_box = (min(lats), max(lats), min(lons), max(lons))
            self.center = ((min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2)
        else:
            self.center = self.default_center
            self.bounding_box = None
        return self.center

    def add_leg(
        self,
        start_point,
        end_point,
        leg_type: str,
        add_end_point: bool = False,
        url: Optional[str] = None,
    ):
        """
        Add a leg to the tour

        Args:
            start_point: GPX point for start of leg
            end_point: GPX point for end of leg
            leg_type: Type of leg (e.g., "bike", "train", "car")
            add_end_point: Whether to add the end point (True for last leg)
            url: Optional URL associated with the leg
        """
        if self.tour is None:
            self.tour = Tour(name="GPX Tour")

        # Create locations
        start_loc = Loc(
            id=str(len(self.tour.legs)),
            name=start_point.name if hasattr(start_point, "name") else None,
            coordinates=(start_point.latitude, start_point.longitude),
        )
        end_loc = Loc(
            id=str(len(self.tour.legs) + 1),
            name=end_point.name if hasattr(end_point, "name") else None,
            coordinates=(end_point.latitude, end_point.longitude),
        )

        # Create and add leg
        leg = Leg(leg_type=leg_type, start=start_loc, end=end_loc, url=url)
        self.tour.legs.append(leg)

    def get_points(self, gpx, way_points_fallback: bool = False):
        """
        Extract waypoints and legs from the GPX object and create a tour
        """
        self.tour = Tour(name="GPX Tour")

        # Process routes
        for route in gpx.routes:
            for i in range(len(route.points) - 1):
                url = route.link.href if route.link else None
                is_last = i == len(route.points) - 2
                self.add_leg(
                    route.points[i],
                    route.points[i + 1],
                    "bike",  # Default to bike for routes
                    add_end_point=is_last,
                    url=url,
                )

        # Process tracks
        for track in gpx.tracks:
            for segment in track.segments:
                for i in range(len(segment.points) - 1):
                    is_last = i == len(segment.points) - 2
                    self.add_leg(
                        segment.points[i],
                        segment.points[i + 1],
                        "bike",  # Default to bike for tracks
                        add_end_point=is_last,
                    )

        prev_loc = None
        # Handle waypoints if no legs were created and fallback is active
        if not self.tour.legs and gpx.waypoints and way_points_fallback:
            for i, waypoint in enumerate(gpx.waypoints):
                loc = Loc(
                    id=str(i),
                    name=waypoint.name,
                    coordinates=(waypoint.latitude, waypoint.longitude),
                    notes=waypoint.description,
                )
                if i > 0:
                    leg = Leg(
                        leg_type="bike",
                        start=prev_loc,
                        end=loc,
                        url=waypoint.link.href if waypoint.link else None,
                    )
                    self.tour.legs.append(leg)
                prev_loc = loc

    def parse_lines(self, lines: str):
        """
        Parse the 'lines' parameter into route segments.

        Args:
            lines (str): The input string containing routes in the format:
                "By bike: 51.243931° N, 6.520022° E, 51.269222° N, 6.625467° E:"

        Returns:
            Tour: Created tour from the parsed coordinates
        """
        coordinate_pattern = r"(\d+\.\d+)° ([NS]), (\d+\.\d+)° ([EW])"
        route_segments = lines.split(":")
        self.tour = Tour(name="Parsed Tour")

        for segment in route_segments:
            segment = segment.strip()

            # Extract leg type (e.g., "bike", "train")
            leg_type_match = re.match(r"By (\w+)→", segment)
            if leg_type_match:
                leg_type = leg_type_match.group(1).lower()
                pass
            else:
                leg_type = "bike"

            points = re.findall(coordinate_pattern, segment)
            if points:
                prev_loc = None
                for i, (lat, ns, lon, ew) in enumerate(points):
                    lat_val = float(lat) * (-1 if ns == "S" else 1)
                    lon_val = float(lon) * (-1 if ew == "W" else 1)

                    loc = Loc(
                        id=str(len(self.tour.legs) + i),
                        name=None,
                        coordinates=(lat_val, lon_val),
                    )

                    if prev_loc:
                        leg = Leg(leg_type=leg_type, start=prev_loc, end=loc)
                        self.tour.legs.append(leg)
                    prev_loc = loc

        if not self.tour.legs:
            raise ValueError("No valid routes found in the input lines.")

        return self.tour

    def parse_lines_and_show(self, lines: str, zoom: int = None):
        """
        Parse lines and display them on the map
        """
        self.parse_lines(lines)
        self.show(zoom=zoom)

    def show(self, zoom: int = None, center=None):
        """
        Show tour with styled paths
        """
        if zoom is None:
            zoom = self.zoom
        if center is None:
            center = self.set_center()

        self.map = LeafletMap(center=center, zoom=zoom)
        if self.tour:
            self.map.draw_tour(self.tour, self.leg_styles)
