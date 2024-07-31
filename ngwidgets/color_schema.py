"""
Created on 2023-09-13

@author: wf
"""

from dataclasses import dataclass

from nicegui import ui


@dataclass
class ColorSchema:
    """
    a nicegui color schema
    """

    name: str = "default"
    primary: str = "#5898d4"
    secondary: str = "#26a69a"
    accent: str = "#9c27b0"
    dark: str = "#1d1d1d"
    positive: str = "#21ba45"
    negative: str = "#c10015"
    info: str = "#31ccec"
    warning: str = "#f2c037"

    def apply(self):
        """
        Apply this color schema to the current UI theme.
        """
        ui.colors(
            primary=self.primary,
            secondary=self.secondary,
            accent=self.accent,
            dark=self.dark,
            positive=self.positive,
            negative=self.negative,
            info=self.info,
            warning=self.warning,
        )

    @classmethod
    def get_schemas(cls):
        """
        Return a list of all available color schemas.
        """
        return [
            cls.default(),
            cls.indigo(),
            cls.red(),
            cls.pink_red(),
            cls.purple(),
            cls.deep_purple(),
            cls.blue(),
            cls.light_blue(),
            cls.cyan(),
            cls.teal(),
            cls.green(),
            cls.light_green(),
            cls.lime(),
            cls.yellow(),
            cls.amber(),
            cls.orange(),
            cls.deep_orange(),
            cls.brown(),
            cls.grey(),
            cls.blue_grey(),
        ]

    @classmethod
    def default(cls):
        """
        Return the default color schema.
        """
        return cls()

    def display(self):
        """
        Display all available color schemas visually in the UI.
        """
        for schema in ColorSchema.get_schemas():
            style = (
                "color: white;"
                "width: 75px; "
                "height: 50px; "
                "border: 1px solid #000; "
                "display: flex; "
                "justify-content: center; "
                "align-items: center; "
                "border-radius: 5px;"
            )
            with ui.row().style("margin-bottom: 10px;"):
                ui.label(schema.name).style(style + "background:grey;")
                schema._display_color("Primary", schema.primary, style)
                schema._display_color("Secondary", schema.secondary, style)
                schema._display_color("Accent", schema.accent, style)
                schema._display_color("Dark", schema.dark, style)
                schema._display_color("Positive", schema.positive, style)
                schema._display_color("Negative", schema.negative, style)
                schema._display_color("Info", schema.info, style)
                schema._display_color("Warning", schema.warning, style)

    def _display_color(self, name: str, color: str, style: str):
        with ui.column():
            ui.label(name).style(style + f"background: {color};")

    @classmethod
    def blue_grey(cls):
        """
        Return a color schema for the Blue Grey color palette from Material Palette.
        see https://www.materialpalette.com/grey/blue-grey
        """
        return cls(
            name="blue_grey",
            primary="#607D8B",  # Blue Grey
            secondary="#B0BEC5",  # Light Blue Grey
            accent="#37474F",  # Dark Blue Grey
            dark="#263238",  # Deepest Blue Grey
            positive="#4CAF50",  # Standard Positive Green
            negative="#D32F2F",  # Standard Negative Red
            info="#2196F3",  # Standard Info Blue
            warning="#FFC107",  # Standard Warning Amber
        )

    @classmethod
    def red(cls):
        """
        Return a color schema for the Red color palette from Material Palette.
        see https://www.materialpalette.com/red/red
        """
        return cls(
            name="red",
            primary="#F44336",
            secondary="#FFCDD2",
            accent="#D32F2F",
            dark="#B71C1C",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )

    @classmethod
    def purple(cls):
        """
        Return a color schema for the Purple color palette from Material Palette.
        see https://www.materialpalette.com/purple/purple
        """
        return cls(
            name="purple",
            primary="#9C27B0",  # Purple
            secondary="#CE93D8",  # Light Purple
            accent="#7B1FA2",  # Dark Purple
            dark="#4A148C",  # Deepest Purple
            positive="#4CAF50",  # Standard Positive Green
            negative="#D32F2F",  # Standard Negative Red
            info="#2196F3",  # Standard Info Blue
            warning="#FFC107",  # Standard Warning Amber
        )

    @classmethod
    def deep_purple(cls):
        """
        Return a color schema for the Deep Purple color palette from Material Palette.
        see https://www.materialpalette.com/purple/deep-purple
        """
        return cls(
            name="deep_purple",
            primary="#673AB7",  # Deep Purple
            secondary="#9575CD",  # Light Deep Purple
            accent="#512DA8",  # Dark Deep Purple
            dark="#311B92",  # Deepest Deep Purple
            positive="#4CAF50",  # Standard Positive Green
            negative="#D32F2F",  # Standard Negative Red
            info="#2196F3",  # Standard Info Blue
            warning="#FFC107",  # Standard Warning Amber
        )

    @classmethod
    def blue(cls):
        """
        Return a color schema for the Blue color palette from Material Palette.
        see https://www.materialpalette.com/blue/blue
        """
        return cls(
            name="blue",
            primary="#2196F3",  # Blue
            secondary="#90CAF9",  # Light Blue
            accent="#1976D2",  # Dark Blue
            dark="#0D47A1",  # Deepest Blue
            positive="#4CAF50",  # Standard Positive Green
            negative="#D32F2F",  # Standard Negative Red
            info="#2196F3",  # Standard Info Blue
            warning="#FFC107",  # Standard Warning Amber
        )

    @classmethod
    def light_blue(cls):
        """
        Return a color schema for the Light Blue color palette from Material Palette.
        see https://www.materialpalette.com/blue/light-blue
        """
        return cls(
            name="light_blue",
            primary="#03A9F4",  # Light Blue
            secondary="#81D4FA",  # Lightest Blue
            accent="#0288D1",  # Dark Light Blue
            dark="#01579B",  # Deepest Light Blue
            positive="#4CAF50",  # Standard Positive Green
            negative="#D32F2F",  # Standard Negative Red
            info="#2196F3",  # Standard Info Blue
            warning="#FFC107",  # Standard Warning Amber
        )

    @classmethod
    def cyan(cls):
        """
        Return a color schema for the Cyan color palette from Material Palette.
        see https://www.materialpalette.com/blue/cyan
        """
        return cls(
            name="cyan",
            primary="#00BCD4",  # Cyan
            secondary="#80DEEA",  # Light Cyan
            accent="#0097A7",  # Dark Cyan
            dark="#006064",  # Deepest Cyan
            positive="#4CAF50",  # Standard Positive Green
            negative="#D32F2F",  # Standard Negative Red
            info="#2196F3",  # Standard Info Blue
            warning="#FFC107",  # Standard Warning Amber
        )

    @classmethod
    def pink_red(cls):
        """
        Return a color schema for the Pink/Red color palette from Material Palette.
        see https://www.materialpalette.com/pink/red
        """
        return cls(
            name="pink_red",
            primary="#E91E63",  # Pink
            secondary="#F8BBD0",  # Light Pink
            accent="#C2185B",  # Dark Pink
            dark="#880E4F",  # Deepest Pink
            positive="#4CAF50",  # Standard Positive Green
            negative="#D32F2F",  # Standard Negative Red
            info="#2196F3",  # Standard Info Blue
            warning="#FFC107",  # Standard Warning Amber
        )

    @classmethod
    def teal(cls):
        """
        Return a color schema for the Teal color palette from Material Palette.
        see https://www.materialpalette.com/teal/teal
        """
        return cls(
            name="teal",
            primary="#009688",
            secondary="#80CBC4",
            accent="#00796B",
            dark="#004D40",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )

    @classmethod
    def lime(cls):
        """
        Return a color schema for the Lime color palette from Material Palette.
        see https://www.materialpalette.com/lime/lime
        """
        return cls(
            name="lime",
            primary="#CDDC39",
            secondary="#F0F4C3",
            accent="#AFB42B",
            dark="#827717",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )

    @classmethod
    def indigo(cls):
        """
        Return a color schema for the Indigo color palette from Material Palette.
        see https://www.materialpalette.com/indigo/indigo
        """
        color_schema = cls(
            name="indigo",
            primary="#3F51B5",
            secondary="#5C6BC0",
            accent="#8A72AC",
            dark="#1A237E",
            positive="#28A745",
            negative="#D32F2F",
            info="#536DFE",
            warning="#FFB74D",
        )
        return color_schema

    @classmethod
    def light_green(cls):
        """
        Return a color schema for the Light Green color palette from Material Palette.
        see https://www.materialpalette.com/green/light-green
        """
        return cls(
            name="light_green",
            primary="#8BC34A",  # Light Green
            secondary="#DCEDC8",  # Lightest Green
            accent="#689F38",  # Dark Light Green
            dark="#33691E",  # Deepest Light Green
            positive="#4CAF50",  # Standard Positive Green
            negative="#D32F2F",  # Standard Negative Red
            info="#2196F3",  # Standard Info Blue
            warning="#FFC107",  # Standard Warning Amber
        )

    @classmethod
    def green(cls):
        """
        Return a color schema for the Green color palette from Material Palette.
        see https://www.materialpalette.com/green/green
        """
        return cls(
            name="green",
            primary="#4CAF50",
            secondary="#C8E6C9",
            accent="#388E3C",
            dark="#1B5E20",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )

    @classmethod
    def yellow(cls):
        """
        Return a color schema for the Yellow color palette from Material Palette.
        see https://www.materialpalette.com/yellow/yellow
        """
        return cls(
            name="yellow",
            primary="#FFEB3B",
            secondary="#FFF9C4",
            accent="#FBC02D",
            dark="#F57F17",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )

    @classmethod
    def amber(cls):
        """
        Return a color schema for the Amber color palette from Material Palette.
        see https://www.materialpalette.com/amber/amber
        """
        return cls(
            name="amber",
            primary="#FFC107",
            secondary="#FFECB3",
            accent="#FFA000",
            dark="#FF8F00",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )

    @classmethod
    def orange(cls):
        """
        Return a color schema for the Orange color palette from Material Palette.
        see https://www.materialpalette.com/orange/orange
        """
        return cls(
            name="orange",
            primary="#FF9800",
            secondary="#FFE0B2",
            accent="#FF5722",
            dark="#E64A19",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )

    @classmethod
    def deep_orange(cls):
        """
        Return a color schema for the Deep Orange color palette from Material Palette.
        see https://www.materialpalette.com/orange/deep-orange
        """
        return cls(
            name="deep_orange",
            primary="#FF5722",
            secondary="#FFCCBC",
            accent="#E64A19",
            dark="#BF360C",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )

    @classmethod
    def brown(cls):
        """
        Return a color schema for the Brown color palette from Material Palette.
        see https://www.materialpalette.com/brown/brown
        """
        return cls(
            name="brown",
            primary="#795548",
            secondary="#D7CCC8",
            accent="#5D4037",
            dark="#3E2723",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )

    @classmethod
    def grey(cls):
        """
        Return a color schema for the Grey color palette from Material Palette.
        see https://www.materialpalette.com/grey/grey
        """
        return cls(
            name="grey",
            primary="#9E9E9E",
            secondary="#F5F5F5",
            accent="#616161",
            dark="#212121",
            positive="#4CAF50",
            negative="#D32F2F",
            info="#2196F3",
            warning="#FFC107",
        )
