"""
Created on 28.08.2024

@author: wf
"""

from nicegui import ui
from nicegui.events import ColorPickEventArguments

from ngwidgets.axes_helper import AxesHelper


class SceneFrame:
    """
    a frame for a scene with a potentially to be colors stl object
    """

    def __init__(self, solution, stl_color: str = "#57B6A9"):
        """
        constructor
        """
        self.solution = solution
        self.stl_color = stl_color
        self.scene = None
        self.stl_objects = {}
        self.axes_view = None

    def setup_button_row(self):
        """
        setup my button row
        """
        with ui.row() as self.button_row:
            self.grid_button = self.solution.tool_button(
                "toggle grid",
                handler=self.toggle_grid,
                icon="grid_off",
                toggle_icon="grid_on",
            )
            self.axes_button = self.solution.tool_button(
                "toggle axes",
                icon="polyline",
                toggle_icon="square",
                handler=self.toggle_axes,
            )
            self.color_picker_button = ui.button(icon="colorize", color=self.stl_color)
            with self.color_picker_button:
                self.color_picker = ui.color_picker(on_pick=self.pick_color)
            self.color_picker_button.disable()

    async def pick_color(self, e: ColorPickEventArguments):
        """
        Asynchronously picks a color based on provided event arguments.

        This function changes the color of the 'color_picker_button' and the 'stl_object'
        according to the color specified in the event arguments.

        Args:
            e (ColorPickEventArguments): An object containing event-specific arguments.
                The 'color' attribute of this object specifies the color to be applied.

        Note:
            If 'stl_object' is None, the function will only change the color of 'color_picker_button'.
            Otherwise, it changes the color of both 'color_picker_button' and 'stl_object'.
        """
        self.color_picker_button.style(f"background-color:{e.color}!important")
        self.stl_color = e.color
        for stl_object in self.stl_objects.values():
            stl_object.material(f"{e.color}")
        pass

    async def toggle_axes(self):
        """
        toggle the axes of my scene
        """
        try:
            self.solution.toggle_icon(self.axes_button)
            new_state = not self.axes_view or not self.axes_view.axes_visible
            new_msg = "on" if new_state else "off"
            ui.notify(f"toggling axes {new_msg}")
            if self.axes_view is None:
                self.axes_view = AxesHelper(self.scene)
            else:
                self.axes_view.toggle_axes()
        except Exception as ex:
            self.solution.handle_exception(ex)

    async def toggle_grid(self, _ea):
        """
        toogle the grid of my scene
        """
        try:
            grid = self.scene._props["grid"]
            grid_str = "off" if grid else "on"
            grid_js = "false" if grid else "true"
            # try toggling grid
            ui.notify(f"setting grid to {grid_str}")
            grid = not grid
            # workaround according to https://github.com/zauberzeug/nicegui/discussions/1246
            js_cmd = f'scene_c{self.scene.id}.children.find(c => c.type === "GridHelper").visible = {grid_js}'
            await ui.run_javascript(js_cmd)
            self.scene._props["grid"] = grid
            self.scene.update()
            # try toggling icon
            self.solution.toggle_icon(self.grid_button)
        except Exception as ex:
            self.solution.handle_exception(ex)
        pass

    def load_stl(
        self, stl_name: str, url: str, scale: float = 1.0, stl_color: str = "#57B6A9"
    ) -> object:
        """
        Loads an STL object into the scene, applies transformations, and sets its material.

        This method enables the color picker button, loads an STL file from the specified URL,
        applies a translation and scaling transformation, sets the object's name and material,
        and then returns the STL object.

        Args:
            stl_name (str): The name to assign to the STL object within the scene.
            url (str): The URL or path from which to load the STL file.
            scale (float, optional): The scale factor to apply to the STL object. Defaults to 1.0.
            stl_color (str, optional): the initial color to use for the stl object
        Returns:
            object: The loaded and transformed STL object within the scene.

        Raises:
            ValueError: If the STL file cannot be loaded from the specified URL.
        """
        self.color_picker_button.enable()
        with self.scene:
            stl_object = self.scene.stl(url).move(x=0.0).scale(scale)
            stl_object.name = stl_name
            if stl_color is None:
                stl_color = self.stl_color
            stl_object.material(stl_color)
            self.stl_objects[stl_name] = stl_object
            return stl_object
