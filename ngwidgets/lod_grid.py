"""
Created on 2023-10-3

@author: wf
"""
import asyncio
import datetime
import sys
import traceback
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from nicegui import ui


@dataclass
class GridConfig:
    """
    Configuration for initializing a ListOfDictsGrid.
    """

    key_col: str = "#"
    column_defs: Optional[List[Dict]] = None
    options: Dict = field(default_factory=dict)
    # optics
    theme: str = "ag-theme-material"
    classes: str = "h-screen overflow-auto"
    all_cols_html: bool = True
    # behavior
    lenient: bool = False
    # default column defs
    autoHeight: bool = True
    sortable: bool = True
    resizable: bool = True
    editable: bool = False
    wrapText: bool = True
    # row options
    multiselect: bool = False
    auto_size_columns: bool = True
    # buttons
    with_buttons: bool = False
    prepend_new: bool = True
    html_columns: List[int] = field(default_factory=list)
    keygen_callback: Optional[Callable] = None
    exception_callback: Optional[Callable] = None
    debug: bool = False


class ListOfDictsGrid:
    """
    ag grid based on list of dict

    see https://nicegui.io/documentation/ag_grid
    see https://github.com/zauberzeug/nicegui/discussions/1833
    """

    def __init__(
        self, lod: Optional[List[Dict]] = None, config: GridConfig = None
    ) -> None:
        """
        Initialize the ListOfDictsGrid object.

        Args:
            lod (Optional[List[Dict]]): List of dictionaries to be displayed.
            config(GridConfig): configuration for the grid behavior
        """
        self.lod = lod
        self.config = config or GridConfig()
        self.lod_index = {}
        try:
            if self.config.with_buttons:
                self.setup_button_row()
            # Update options to include onGridReady event handling
            self.config.options[
                ":onGridReady"
            ] = "(params) => params.columnApi.autoSizeAllColumns()"

            self.ag_grid = ui.aggrid(
                options=self.config.options,
                html_columns=self.config.html_columns,
            ).classes(self.config.classes)
            self.ag_grid.theme = self.config.theme
            self.auto_size_columns = (self.config.auto_size_columns,)
            self.setDefaultColDef()
            if lod is not None:
                self.load_lod(lod, self.config.column_defs)
        except Exception as ex:
            self.handle_exception(ex)

    @property
    def options(self):
        return self.ag_grid._props.get("options", {})

    @options.setter
    def options(self, value):
        self.ag_grid._props["options"] = value

    @property
    def html_columns(self):
        return self.ag_grid._props.get("html_columns", [])

    @html_columns.setter
    def html_columns(self, value):
        self.ag_grid._props["html_columns"] = value

    @property
    def auto_size_columns(self):
        return self.ag_grid._props.get("auto_size_columns", True)

    @auto_size_columns.setter
    def auto_size_columns(self, value):
        self.ag_grid._props["auto_size_columns"] = value

    def handle_exception(self, ex: Exception) -> None:
        """
        Handles exceptions thrown during grid initialization or operation.

        In debug mode, this method prints the stack trace and re-raises the exception for further debugging. In non-debug mode, it notifies the user of a general error.

        Args:
            ex (Exception): The exception that was caught.

        Raises:
            Exception: Re-raises the exception in debug mode for further debugging.
        """
        if self.config.debug:
            # Print a stack trace to stderr
            print("Exception caught in ListOfDictsGrid:", file=sys.stderr)
            traceback.print_exc()
            # Optionally, re-raise the exception for further debugging.
            raise ex
        elif self.config.exception_callback:
            self.config.exception_callback(ex)
        else:
            # If not in debug mode, notify the user with a general error message.
            # Ensure that ui.notify or a similar method is available and properly configured.
            ui.notify("Unhandled exception occurred", type="error")

    def update_index(self, lenient: bool = False):
        """
        update the index based on the given key column
        """
        self.lod_index = {}
        if self.lod:
            for row_index, row in enumerate(self.lod):
                if self.config.key_col in row:
                    key_value = row[self.config.key_col]
                    self.lod_index[key_value] = row
                else:
                    msg = f"missing key column {self.config.key_col} in row {row_index}"
                    if not lenient:
                        raise Exception(msg)
                    else:
                        print(msg, file=sys.stderr)
                    # missing key
                    pass

    def get_row_for_key(self, key_value: str):
        """
        the the row for the given key_value

        Args:
            key_value: str
        """
        row = self.lod_index.get(key_value, None)
        return row

    def update_row(self, key_value, row_key, value):
        """
        Update a row in the grid.
        """
        row = self.get_row_for_key(key_value)
        if row:
            row_data = self.get_row_data()
            for grid_row in row_data:
                if row[self.config.key_col] == grid_row[self.config.key_col]:
                    grid_row[row_key] = value

    def get_row_data(self):
        """
        get the complete row data
        """
        row_data = self.ag_grid.options["rowData"]
        return row_data

    async def onSizeColumnsToFit(self, _msg: dict):
        """
        see https://www.reddit.com/r/nicegui/comments/17cg0o5/aggrid_autosize_columns_to_data_width/
        """
        # await asyncio.sleep(0.2)
        if self.ag_grid:
            self.ag_grid.call_column_api_method("autoSizeAllColumns")
            self.ag_grid.update()

    def setDefaultColDef(self):
        """
        set the default column definitions
        """
        if not "defaultColDef" in self.ag_grid.options:
            self.ag_grid.options["defaultColDef"] = {}
        if self.config.multiselect:
            # Apply settings for multiple row selection
            self.ag_grid.options["rowSelection"] = "multiple"
        defaultColDef = self.ag_grid.options["defaultColDef"]
        defaultColDef["resizable"] = self.config.resizable
        defaultColDef["sortable"] = self.config.sortable
        # https://www.ag-grid.com/javascript-data-grid/grid-size/
        defaultColDef["wrapText"] = self.config.wrapText
        defaultColDef["autoHeight"] = self.config.autoHeight
        defaultColDef["editable"] = self.config.editable

    def load_lod(self, lod: list, columnDefs: list = None):
        """
        load the given list of dicts

        Args:
            lod(list): a list of dicts to be loaded into the grid
            columnDefs(list): a list of column definitions
        """
        try:
            if columnDefs is None:
                # assume lod
                columnDefs = []
                if len(lod) > 0:
                    header = lod[0]
                    for key, value in header.items():
                        if isinstance(value, int) or isinstance(value, float):
                            col_filter = "agNumberColumnFilter"
                        elif isinstance(value, datetime.datetime) or isinstance(
                            value, datetime.date
                        ):
                            col_filter = "agDateColumnFilter"
                        else:
                            col_filter = True  # Use default filter
                        columnDefs.append(dict({"field": key, "filter": col_filter}))
            self.ag_grid.options["columnDefs"] = columnDefs
            self.ag_grid.options["rowData"] = lod
            self.update_index(lenient=self.config.lenient)
            if self.config.all_cols_html:
                # Set html_columns based on all_rows_html flag
                self.html_columns = list(range(len(columnDefs)))
        except Exception as ex:
            self.handle_exception(ex)

    def update(self):
        """
        update my aggrid
        """
        if self.ag_grid:
            self.ag_grid.update()

    async def get_selected_rows(self):
        """
        get the currently selected rows 
        """
        selected_rows = await self.ag_grid.get_selected_rows()
        return selected_rows

    async def delete_selected_rows(self, _args):
        """
        Delete the currently selected rows based on the key column.
        """
        # Await the asynchronous call to get selected rows
        selected_rows = await self.get_selected_rows()
        if len(selected_rows) == 0:
            ui.notify("no rows selected for delete", type="warning")
            return
        # Get the list of keys of selected rows
        selected_keys = [row[self.config.key_col] for row in selected_rows]
        # Notify the user about the operation
        ui.notify(f"deleting rows with keys {selected_keys}")
        # Update the data to exclude selected rows
        self.lod[:] = [
            row for row in self.lod if row[self.config.key_col] not in selected_keys
        ]
        # Update the grid to reflect changes
        self.update()

    async def new_row(self, _args):
        """
        add a new row
        """
        try:
            # Handle the key column
            if (
                self.config.key_col == "#"
            ):  # If the key column is '#' treating it as an integer index
                new_key = len(self.lod)
            elif (
                self.config.keygen_callback
            ):  # If a key generation callback is provided
                new_key = self.config.keygen_callback()
            else:  # If the key column isn't '#' and no keygen callback is provided
                msg = f"Missing keygen_callback to create new key for '{self.config.key_col}' column"
                ui.notify(msg, type="negative")
                return
            ui.notify(f"new row with {self.config.key_col}={new_key}")
            new_record = {f"{self.config.key_col}": new_key}
            if self.config.prepend_new:
                self.lod.insert(0, new_record)
            else:
                self.lod.append(new_record)
            self.update()
        except Exception as ex:
            self.handle_exception(ex)

    def setup_button_row(self):
        """
        set up a button row
        """
        with ui.row():
            # icons per https://fonts.google.com/icons
            if self.config.editable:
                ui.button(
                    "New", 
                    icon="add", 
                    on_click=self.new_row
                )
                ui.button(
                    "Delete", 
                    icon="delete", 
                    on_click=self.delete_selected_rows
                )
            #ui.button("Fit", icon="arrow_range", on_click=self.onSizeColumnsToFit)
            ui.button(
                "All",
                icon="select_all",
                on_click=lambda: self.ag_grid.call_api_method("selectAll"),
            )
