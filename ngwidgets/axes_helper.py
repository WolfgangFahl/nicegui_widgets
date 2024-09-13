from nicegui import ui


class AxesHelper:
    """
    A Python class for creating a 3D helper for visualizing the axes in a scene.
    This class is designed to be used with the `nicegui` library (https://pypi.org/project/nicegui/)
    for creating 3D scenes. It creates line objects for the x, y, and z axes,
    each with a distinct color, and provides methods for changing these colors and toggling their visibility.

    The original JavaScript code, which this Python code is based on, can be found at:
    https://raw.githubusercontent.com/mrdoob/three.js/master/src/helpers/AxesHelper.js
    The JavaScript code was refactored into this Python version by OpenAI's ChatGPT.

    For the refactoring, following prompts were given:
    1. Refactor a JavaScript class for handling ThreeJS scenes into a Python class using the `nicegui` library.
    2. The class should allow to hide/show axes.
    3. Usage of `nicegui` library's API for the colors.
    4. Include Google docstrings and type hints to the code.
    5. The scene should be a constructor parameter to be remembered.
    6. The Axes should be named x, y and z. The name attribute should be assigned after the line object creation.
    7. The `set_colors` method should be called in the constructor.
    8. Use `with self.scene as scene` when drawing the lines.
    9. The class should provide a method to toggle the visibility of axes.
    10. The default size of the axes to be drawn should be 10.0.
    11. Color information should be persisted when toggling the axes.
    12. Use a dictionary to store colors by axes names.

    According to nicegui's documentation (https://nicegui.io/documentation/scene), the 'scene.line()' function is used to
    create lines, here is an example:
        scene.line([-4, 0, 0], [-4, 2, 0]).material('#ff0000')

    Date: 2023-07-24
    @author: Refactored into Python by OpenAI's ChatGPT

    Attributes:
        size (float): The size of the axes to be drawn.
        scene (ui.scene): The scene where the axes will be drawn.

    Usage:
        scene = ui.scene().classes('w-full h-64')
        axes_helper = AxesHelper(scene, size=10.0)
        axes_helper.set_colors(x_axis_color='#FF0000', y_axis_color='#00FF00', z_axis_color='#0000FF')  # set colors for x, y, and z axes
        axes_helper.toggle_axes()  # toggle visibility of the axes
    """

    def __init__(self, scene: "ui.scene", size: float = 10.0):
        """
        The constructor for AxesHelper class.

        Args:
            scene (ui.scene): The scene where the axes will be drawn.
            size (float): The size of the axes to be drawn.
        """
        self.scene = scene
        self.size = size
        self.vertices = [
            (0, 0, 0),
            (size, 0, 0),
            (0, 0, 0),
            (0, size, 0),
            (0, 0, 0),
            (0, 0, size),
        ]

        self.axis_names = ["x", "y", "z"]
        self.lines = []
        self.axes_visible = False
        self.color_by_name = {"x": "#FF0000", "y": "#00FF00", "z": "#0000FF"}
        self.toggle_axes()

    def set_colors(
        self,
        x_axis_color: str = "#FF0000",
        y_axis_color: str = "#00FF00",
        z_axis_color: str = "#0000FF",
    ):
        """
        A method to set colors of the axes.

        Args:
            x_axis_color (str): Color of the x-axis.
            y_axis_color (str): Color of the y-axis.
            z_axis_color (str): Color of the z-axis.
        """
        self.color_by_name = {"x": x_axis_color, "y": y_axis_color, "z": z_axis_color}
        for idx, line in enumerate(self.lines):
            line.material(self.color_by_name[self.axis_names[idx]])

    def toggle_axes(self):
        """
        A method to toggle the visibility of the axes.
        """
        if self.axes_visible:
            # Axes are currently visible, so remove them
            for line in self.lines:
                try:
                    line.delete()
                except KeyError:
                    pass
            self.lines = []
            self.axes_visible = False
            self.scene.update()
        else:
            # Axes are currently not visible, so add them
            with self.scene:
                for i in range(3):
                    line = self.scene.line(
                        self.vertices[2 * i], self.vertices[2 * i + 1]
                    )
                    line.name = self.axis_names[i]
                    line.material(self.color_by_name[line.name])
                    self.lines.append(line)
            self.axes_visible = True
