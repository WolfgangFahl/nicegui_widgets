import platform
from pathlib import Path
from typing import List, Optional

from nicegui import events, ui


class LocalFilePicker(ui.dialog):
    """
    see
    https://raw.githubusercontent.com/zauberzeug/nicegui/main/examples/local_file_picker/local_file_picker.py

    Comments improved by Claude AI

    A simple file picker that allows selection of files from the local filesystem where NiceGUI is running.

    Attributes:
        path (Path): The current directory path.
        upper_limit (Optional[Path]): The upper limit directory.
        show_hidden_files (bool): Whether to show hidden files.
        grid (ui.aggrid): The AgGrid component for displaying files.
        drives_toggle (Optional[ui.toggle]): Toggle for selecting drives on Windows.

    Args:
        directory (str): The directory to start in.
        upper_limit (Optional[str]): The directory to stop at. Defaults to the starting directory.
        multiple (bool): Whether to allow multiple file selection. Defaults to False.
        show_hidden_files (bool): Whether to show hidden files. Defaults to False.
    """

    def __init__(
        self,
        directory: str,
        *,
        upper_limit: Optional[str] = ...,
        multiple: bool = False,
        show_hidden_files: bool = False,
    ) -> None:
        super().__init__()

        self.path: Path = Path(directory).expanduser()
        self.upper_limit: Optional[Path] = (
            None
            if upper_limit is None
            else Path(directory if upper_limit == ... else upper_limit).expanduser()
        )
        self.show_hidden_files: bool = show_hidden_files
        self.grid: ui.aggrid
        self.drives_toggle: Optional[ui.toggle] = None

        with self, ui.card():
            self.add_drives_toggle()
            self.grid = (
                ui.aggrid(
                    {
                        "columnDefs": [{"field": "name", "headerName": "File"}],
                        "rowSelection": "multiple" if multiple else "single",
                    },
                    html_columns=[0],
                )
                .classes("w-96")
                .on("cellDoubleClicked", self.handle_double_click)
            )
            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=self.close).props("outline")
                ui.button("Ok", on_click=self._handle_ok)
        self.update_grid()

    def add_drives_toggle(self) -> None:
        """
        Adds a toggle for selecting drives on Windows platforms.
        """
        if platform.system() == "Windows":
            import win32api

            drives: List[str] = win32api.GetLogicalDriveStrings().split("\000")[:-1]
            self.drives_toggle = ui.toggle(
                drives, value=drives[0], on_change=self.update_drive
            )

    def update_drive(self) -> None:
        """
        Updates the current path when a new drive is selected.
        """
        if self.drives_toggle:
            self.path = Path(self.drives_toggle.value).expanduser()
            self.update_grid()

    def update_grid(self) -> None:
        """
        Updates the grid with the current directory contents.
        """
        paths: List[Path] = list(self.path.glob("*"))
        if not self.show_hidden_files:
            paths = [p for p in paths if not p.name.startswith(".")]
        paths.sort(key=lambda p: p.name.lower())
        paths.sort(key=lambda p: not p.is_dir())

        self.grid.options["rowData"] = [
            {
                "name": f"📁 <strong>{p.name}</strong>" if p.is_dir() else p.name,
                "path": str(p),
            }
            for p in paths
        ]
        if (self.upper_limit is None and self.path != self.path.parent) or (
            self.upper_limit is not None and self.path != self.upper_limit
        ):
            self.grid.options["rowData"].insert(
                0,
                {
                    "name": "📁 <strong>..</strong>",
                    "path": str(self.path.parent),
                },
            )
        self.grid.update()

    def handle_double_click(self, e: events.GenericEventArguments) -> None:
        """
        Handles double-click events on grid items.

        Args:
            e (events.GenericEventArguments): The event arguments.
        """
        self.path = Path(e.args["data"]["path"])
        if self.path.is_dir():
            self.update_grid()
        else:
            self.submit([str(self.path)])

    async def _handle_ok(self) -> None:
        """
        Handles the 'Ok' button click event.
        """
        rows: List[dict] = await self.grid.get_selected_rows()
        self.submit([r["path"] for r in rows])
