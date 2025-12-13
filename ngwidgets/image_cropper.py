"""
Created on 2025-12-08

@author: wf
"""
import os

from PIL import Image
from nicegui import events, ui, background_tasks


class ImageCropper:
    """
    A NiceGUI-based interactive image cropper.
    Allows users to draw a box on an image to define crop coordinates.
    """

    def __init__(self,solution):
        self.solution=solution
        # Crop State
        self.crop_x: int = 0
        self.crop_y: int = 0
        self.crop_width: int = 0
        self.crop_height: int = 0

        # Dragging State for UI
        self.dragging: bool = False
        self.start_x: float = 0
        self.start_y: float = 0

        # References
        self.interactive_view: ui.interactive_image = None
        self.container = None
        # Injections needed by caller
        self.file_path: str = None  # Store the physical path
        # Debugging checkpoint
        pass

    def setup_ui(self, container, image_url: str):
        """
        Sets up the UI elements.

        Args:
            container: The parent container
            image_url: The URL for the browser to display
        """
        self.container = container

        # Coordinate display
        with ui.row().classes("items-center"):
            ui.label("Crop Area:")
            with ui.row():
                ui.number(label="X", value=0).bind_value(self, "crop_x").props("size=5 readonly")
                ui.number(label="Y", value=0).bind_value(self, "crop_y").props("size=5 readonly")
                ui.number(label="W", value=0).bind_value(self, "crop_width").props("size=5 readonly")
                ui.number(label="H", value=0).bind_value(self, "crop_height").props("size=5 readonly")

            # Reset button convenient to have nearby
            ui.button(icon="crop_free", on_click=self.reset_crop).props("flat round color=warning").tooltip("Reset Crop")
            # Crop button
            # Visibility is bound to crop_width. It appears only when width > 0.
            ui.button(icon="check", on_click=self.on_crop_click) \
                .props("flat round color=positive") \
                .tooltip("Apply Crop") \
                .bind_visibility_from(self, "crop_width", backward=lambda w: w > 0)

            # Rotation buttons
            ui.button(icon="rotate_left", on_click=lambda: self.on_rotate_click(left=True)) \
                .props("flat round color=primary") \
                .tooltip("Rotate Left 90°")
            ui.button(icon="rotate_right", on_click=lambda: self.on_rotate_click(left=False)) \
                .props("flat round color=primary") \
                .tooltip("Rotate Right 90°")


        # Interactive Image implementation
        self.interactive_view = ui.interactive_image(
            image_url,
            on_mouse=self.handle_mouse,
            events=["mousedown", "mousemove", "mouseup"],
            cross=True,
        ).classes("w-full")

    def set_source(self, source: str):
        """Updates the image source URL."""
        if self.interactive_view:
            self.interactive_view.set_source(source)

    def handle_mouse(self, e: events.MouseEventArguments):
        """
        Handles mouse events to draw a crop rectangle on the interactive image.
        """
        if e.type == "mousedown":
            self.dragging = True
            self.start_x = e.image_x
            self.start_y = e.image_y

        elif e.type == "mousemove":
            if self.dragging:
                self.update_crop_selection(e.image_x, e.image_y)

        elif e.type == "mouseup":
            self.dragging = False
            self.update_crop_selection(e.image_x, e.image_y)


    def update_crop_selection(self, current_x: float, current_y: float):
        """
        Calculates the rectangle coordinates based on start and current pointers,
        updates state variables, and draws the SVG overlay.
        """
        # Calculate top-left corner and dimensions
        x = min(self.start_x, current_x)
        y = min(self.start_y, current_y)
        w = abs(self.start_x - current_x)
        h = abs(self.start_y - current_y)

        # Update persistent crop variables (convert to int for PIL)
        self.crop_x = int(x)
        self.crop_y = int(y)
        self.crop_width = int(w)
        self.crop_height = int(h)

        # Update the visual SVG overlay
        self.interactive_view.content = (
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="none" stroke="red" stroke-width="2" />'
        )

    def reset_crop(self):
        """Resets crop variables and clears SVG overlay."""
        self.crop_x = 0
        self.crop_y = 0
        self.crop_width = 0
        self.crop_height = 0
        if self.interactive_view:
            self.interactive_view.content = ""

    def notify_problem(self,msg:str):
        with self.container:
            ui.notify(msg, type='warning')

    async def on_crop_click(self):
        """
        handle the click of the crop button
        """
        if self.file_path and os.path.isfile(self.file_path):
            background_tasks.create(self.apply_crop())
        else:
            self.notify_problem("No file path configured for cropping.")

    async def on_rotate_click(self, left: bool = True):
        """
        Handle the click of the rotate buttons.
        """
        if self.file_path and os.path.isfile(self.file_path):
            background_tasks.create(self.apply_rotation(left))
        else:
            self.notify_problem("No file path configured for rotation.")


    async def apply_crop(self):
        try:
            path=self.file_path
            x=self.crop_x
            y=self.crop_y
            w=self.crop_width
            h=self.crop_height

            if not os.path.exists(path):
                self.notify_problem(f"Image not found at {path}")
                return

            with Image.open(path) as img:
                # Ensure we are working with correct coordinates
                box = (x, y, x + w, y + h)
                cropped_img = img.crop(box)

                # Save back to specific path (overwrite)
                # We save specifically to maintain format
                cropped_img.save(path)
                msg=f"{path} cropped to {w}x{h}"
                with self.container:
                    ui.notify(msg)
                with self.interactive_view:
                    self.interactive_view.force_reload()
        except Exception as ex:
            self.solution.handle_exception(ex)

    async def apply_rotation(self, left: bool):
        """
        Rotates the image at self.file_path by 90 degrees and saves it.

        Args:
            left: If True, rotate 90 degrees Counter-Clockwise.
                  If False, rotate 90 degrees Clockwise.
        """
        try:
            path = self.file_path
            if not os.path.exists(path):
                self.notify_problem(f"Image not found at {path}")
                return
                        # Determine rotation angle constant
            # ROTATE_90 is Counter-Clockwise (Left)
            # ROTATE_270 is Counter-Clockwise 270 aka Clockwise 90 (Right)
            method = Image.Transpose.ROTATE_90 if left else Image.Transpose.ROTATE_270

            with Image.open(path) as img:
                rotated_img = img.transpose(method)
                rotated_img.save(path)

            direction = "left" if left else "right"
            msg = f"Rotated {direction} 90°"
            with self.container:
                ui.notify(msg)
                        # Reset crop markup as dimensions/orientation have changed
            self.reset_crop()

            # Force browser to reload the image
            with self.interactive_view:
                self.interactive_view.force_reload()
        except Exception as ex:
            self.solution.handle_exception(ex)


