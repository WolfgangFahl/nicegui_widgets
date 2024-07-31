"""
Created on 2024-07-17

@author: wf
"""

from colour import Color


class ColorMap:
    """
    A map of color ranges.

    the first column of each row has the color range from start_color to end_color
    the other columns are interpolated using the lum_min, lum_max and sat_f parameters

    Attributes:
        start_color (Color): The starting color of the range.
        end_color (Color): The ending color of the range.
        num_levels (int): The number of levels in the color range.
        lum_min (float): The minimum luminance
        lum_max (float): The maximum luminance
        sat_f (float): The saturation factor
    """

    def __init__(
        self,
        start_color: str = "#ff002b",
        end_color: str = "#110080",
        num_levels: int = 5,
        lum_min: float = 0.5,
        lum_max: float = 0.86,
        sat_f: float = 0.35,
    ):
        self.start_color = Color(start_color)
        self.end_color = Color(end_color)
        self.num_levels = num_levels
        self.lum_min = lum_min
        self.lum_max = lum_max
        self.sat_f = sat_f
        self.main_colors = list(self.start_color.range_to(self.end_color, num_levels))
        self.color_matrix = self._create_color_matrix()

    def _map_to_color(self, main_color: Color, col_index: float) -> Color:
        """
        Maps a column index to a color shade based on the main color.
        """
        luminance = (self.lum_max - self.lum_min) * col_index + self.lum_min
        saturation = main_color.saturation * (1 - (1 - self.sat_f) * col_index)
        color = Color(hue=main_color.hue, saturation=saturation, luminance=luminance)
        return color

    def _create_color_matrix(self):
        matrix = []
        for main_color in self.main_colors:
            shade_row = []
            for col in range(self.num_levels):
                col_index = col / (self.num_levels - 1)
                shade = self._map_to_color(main_color, col_index)
                shade_row.append(shade)
            matrix.append(shade_row)
        return matrix

    def get_color(self, row: int, col: int) -> Color:
        """
        Retrieves the color hex code at the specified row and column indices.
        """
        return self.color_matrix[row][col]
