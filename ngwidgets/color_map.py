"""
Created on 2024-07-17

@author: wf
"""
from colour import Color


class ColorMap:
    """
    A map of color ranges.

    Attributes:
        start_color (Color): The starting color of the range.
        end_color (Color): The ending color of the range.
        num_levels (int): The number of levels in the color range.
        lum_min (float): The minimum luminance for colors.
        lum_f (float): The factor to apply to the luminance based on the input factor.
        sat_f (float): The saturation factor for colors.
    """
    def __init__(self, 
        start_color: str="red", 
        end_color: str="green", 
        num_levels: int=5, 
        lum_min: float = 0.3, 
        lum_f: float = 0.7,
        sat_f: float = 1.0):
        self.start_color = Color(start_color)
        self.end_color = Color(end_color)
        self.num_levels = num_levels
        self.lum_min = lum_min
        self.lum_f = lum_f
        self.sat_f = sat_f
        self.main_colors = list(self.start_color.range_to(self.end_color, num_levels))
        self.color_matrix = self._create_color_matrix()

    def _map_to_color(self, main_color: Color, col_index: float) -> Color:
        """
        Maps a column index to a color shade based on the main color.
        """
        luminance = max(self.lum_min, main_color.luminance - self.lum_f * col_index)
        saturation = main_color.saturation * (1 - (1 - self.sat_f) * col_index)
        color= Color(hue=main_color.hue, saturation=saturation, luminance=luminance)
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

