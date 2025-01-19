#!/usr/bin/env python
"""
Created on 2025-01-18

@author: wf
"""
import re
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

def clean_smw_artifacts(input_str: str) -> str:
    """
    Remove SMW artifacts ([[SMW::on]] and [[SMW::off]]) from the input string.

    Args:
        input_str (str): Input string containing SMW artifacts.

    Returns:
        str: Cleaned string without SMW markers.
    """
    # Regex to match and remove SMW markers
    return re.sub(r"\[\[SMW::(on|off)\]\]", "", input_str)

@ui.page("/lines")
def lines_page(lines: str = None, auth_token: str = None, zoom: int = GPXViewer.default_zoom):
    """
    Endpoint to display routes based on 'lines' parameter.
    """
    global viewer
    if not viewer:
        ui.label("Error: Viewer not initialized")
        return

    if viewer.args.token and auth_token != viewer.args.token:
        ui.label("Error: Invalid authentication token")
        return

    if not lines:
        ui.label("Error: No 'lines' parameter provided")
        return

    # Clean the lines parameter to remove SMW artifacts
    cleaned_lines = clean_smw_artifacts(lines)

    # Delegate logic to GPXViewer
    try:
        viewer.parse_lines_and_show(cleaned_lines, zoom=zoom)
    except ValueError as e:
        ui.label(f"Error processing lines: {e}")

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
