#!/usr/bin/env python
"""
Created on 2025-01-18

@author: wf
"""

from nicegui import ui
from ngwidgets.gpxviewer import GPXViewer

# Global viewer instance
viewer = None

def initialize_viewer():
    """
    Initialize the GPXViewer with parsed arguments.
    """
    global viewer
    parser = GPXViewer.get_parser()
    args = parser.parse_args()
    viewer = GPXViewer(args=args)

@ui.page("/")
def gpx(gpx: str = None, auth_token: str = None, zoom:int=GPXViewer.default_zoom):
    """
    GPX viewer page with optional gpx_url and auth_token.
    """
    global viewer
    if not viewer:
        ui.label("Error: Viewer not initialized")
        return

    if viewer.args.token and auth_token != viewer.args.token:
        ui.label("Error: Invalid authentication token")
        return

    gpx_to_use = gpx if gpx else viewer.args.gpx
    if gpx_to_use:
        viewer.load_gpx(gpx_to_use)
        viewer.show(zoom=zoom)
    else:
        ui.label("Please provide a GPX file via 'gpx' query parameter or the command line.")

def main():
    """
    Entry point for gpxviewer.
    """
    initialize_viewer()
    ui.run(port=viewer.args.port, title="GPX Viewer")

# Call main directly without a guard
main()
