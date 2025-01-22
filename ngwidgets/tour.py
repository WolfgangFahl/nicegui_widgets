"""
Created on 2025-01-19

@author: wf

Tour definition as Legs connecting Locs
Styling of Legs

"""

from dataclasses import field
from typing import Dict, Optional, Tuple

from ngwidgets.yamlable import lod_storable


@lod_storable
class Loc:
    """
    A location in a trip or tour
    """

    id: str
    coordinates: Tuple[float, float]  # latlon
    name: str
    loc_type: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None


@lod_storable
class Leg:
    """
    A segment of a trip between two locations
    """

    leg_type: str  # e.g., "bike", "train", "car"
    start: Loc
    end: Loc
    url: Optional[str] = None


@lod_storable
class Tour:
    """
    A sequence of legs connecting waypoints that form a complete journey
    """

    name: str
    legs: list[Leg] = field(default_factory=list)
    description: Optional[str] = None
    url: Optional[str] = None

    def dump(self, limit: int = 10, leg_styles: "LegStyles" = None):
        """
        Print a detailed dump of the tour for debugging

        Args:
           limit: Maximum number of legs to show
        """
        if leg_styles is None:
            leg_styles = LegStyles.default()
        print(f"Tour: {self.name}")
        for i, leg in enumerate(self.legs):
            if i >= limit:
                remaining = len(self.legs) - limit
                print(f"... {remaining} more legs")
                break
            leg_style = leg_styles.get_style(leg.leg_type)
            if leg_style:
                utf8_icon = leg_style.utf8_icon
            else:
                utf8_icon = "?"
            coord_start = (
                f"({leg.start.coordinates[0]:.5f}, {leg.start.coordinates[1]:.5f})"
            )
            coord_end = f"({leg.end.coordinates[0]:.5f}, {leg.end.coordinates[1]:.5f})"
            print(f" {utf8_icon} {coord_start} ➜ {coord_end}")


@lod_storable
class LegStyle:
    """
    Style configuration for a transport leg
    """

    leg_type: str  # e.g. "bike", "train", "car", "ferry", "bus", "plane"
    point_type: str
    color: str
    utf8_icon: str
    weight: int
    dashArray: Optional[str]
    opacity: float


@lod_storable
class LegStyles:
    """
    Collection of predefined styles for different leg types
    """

    styles: Dict[str, LegStyle] = field(default_factory=dict)

    def get_style(self, leg_type: str) -> LegStyle:
        """
        Get style for given leg type
        """
        leg_style = self.styles.get(leg_type)
        return leg_style

    @classmethod
    def default(cls) -> "LegStyles":
        """
        Get default leg styles
        """
        default_styles = {
            "bike": LegStyle(
                leg_type="bike",
                point_type="knooppunt",
                color="#FF0000",  # bike - red (avoid green due to map background)
                utf8_icon="🚲",
                weight=3,
                dashArray=None,
                opacity=1.0,
            ),
            "train": LegStyle(
                leg_type="train",
                point_type="train_station",
                color="#555555",  # train - dark gray (improves contrast over black)
                utf8_icon="🚂",
                weight=3,
                dashArray="10,10",
                opacity=1.0,
            ),
            "car": LegStyle(
                leg_type="car",
                point_type="parking",
                color="#404040",  # car - medium gray
                utf8_icon="🚗",
                weight=3,
                dashArray=None,
                opacity=1.0,
            ),
            "ferry": LegStyle(
                leg_type="ferry",
                point_type="ferry_terminal",
                color="#1E90FF",  # ferry - dodger blue for visibility
                utf8_icon="⛴️",
                weight=3,
                dashArray="15,10",
                opacity=0.8,
            ),
            "bus": LegStyle(
                leg_type="bus",
                point_type="bus_stop",
                color="#FF4500",  # bus - orange-red for distinctiveness
                utf8_icon="🚌",
                weight=3,
                dashArray=None,
                opacity=1.0,
            ),
            "plane": LegStyle(
                leg_type="plane",
                point_type="airport",
                color="#4B0082",  # plane - indigo for uniqueness
                utf8_icon="✈️",
                weight=3,
                dashArray="20,10,5,10",
                opacity=0.7,
            ),
        }
        return cls(styles=default_styles)
