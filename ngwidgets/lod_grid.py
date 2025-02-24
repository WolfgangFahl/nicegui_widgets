"""
Created on 2023-10-3

@author: wf
"""

import datetime
import sys
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

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
    button_names: List[str] = field(default_factory=lambda: ["new", "delete", "all", "fit"])
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
        self.all_selected = False  # track selection state
        try:
            if self.config.with_buttons:
                self.setup_button_row(self.config.button_names)
            # Update options to include onGridReady event handling
            self.config.options[":onGridReady"] = (
                "(params) => params.columnApi.autoSizeAllColumns()"
            )

            self.ag_grid = ui.aggrid(
                options=self.config.options,
                html_columns=self.config.html_columns,
            ).classes(self.config.classes)
            self.ag_grid.theme = self.config.theme
            self.auto_size_columns = self.config.auto_size_columns
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

    def get_column_def(self, col: str) -> Dict:
        """
        get the column definition for the given column

        Args:
            col (str): The field name of the column where checkboxes should be enabled.

        Returns:
            Dict: the column definition
        """
        if not self.ag_grid.options.get("columnDefs"):
            raise Exception(
                "Column definitions are not set. Load the data first using load_lod."
            )
        # Go through each column definition
        for col_def in self.ag_grid.options["columnDefs"]:
            if col_def["field"] == col:
                return col_def
        return None

    def set_column_def(self, col: str, key: str, value: Any) -> Dict:
        """
        Set a value in a column definition dictionary for a specified column.

        This method updates the column definition dictionary for a given column by
        setting a specific key to a provided value. If the column definition exists,
        the key-value pair is updated; if not, no changes are made.

        Parameters:
            col (str): The name of the column to update.
            key (str): The key in the column definition dictionary to set.
            value (Any): The value to assign to the key in the dictionary.

        Returns:
            Dict: The updated column definition dictionary, or None if the column does not exist.
        """
        col_def = self.get_column_def(
            col
        )  # Assuming get_column_def is defined elsewhere.
        if col_def:
            col_def[key] = value
        return col_def

    def set_checkbox_renderer(self, checkbox_col: str):
        """
        set cellRenderer to checkBoxRenderer for the given column

        Args:
            checkbox_col (str): The field name of the column where
            rendering as checkboxes should be enabled.

        """
        col_def = self.get_column_def(checkbox_col)
        col_def["cellRenderer"] = "checkboxRenderer"

    def set_checkbox_selection(self, checkbox_col: str):
        """
        Set the checkbox selection for a specified column.

        Args:
            checkbox_col (str): The field name of the column where checkboxes should be enabled.
        """
        col_def = self.get_column_def(checkbox_col)
        if col_def:
            col_def["checkboxSelection"] = True

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
            ui.notify(
                f"Unhandled exception {str(ex)} occurred in ListOfDictsGrid",
                type="error",
            )

    def get_index(self, lenient: bool = False,lod=None,key_col:str=None):
        """
        get and index (dict of dicts) of the given list of
        dicts based on the given key column - if no key_col is given
        index by row number starting from 1
        """
        lod_index = {}
        if lod is None:
            lod=self.lod
        if lod:
            for row_index, row in enumerate(lod):
                if key_col is None:
                    lod_index[row_index+1] = row
                else:
                    if self.config.key_col in row:
                        key_value = row[key_col]
                        lod_index[key_value] = row
                    else:
                        msg = f"missing key column {self.config.key_col} in row {row_index}"
                        if not lenient:
                            raise Exception(msg)
                        else:
                            print(msg, file=sys.stderr)
                        # missing key
                        pass
        return lod_index

    def update_index(self, lenient: bool = False):
        """
        update my index (with view records)
        """
        self.lod_index=self.get_index(lenient=lenient,lod=self.lod,key_col=self.config.key_col)

    def get_row_for_key(self, key_value: str):
        """
        the the row for the given key_value

        Args:
            key_value: str
        """
        row = self.lod_index.get(key_value, None)
        return row

    def get_cell_value(self, key_value: Any, col_key: str) -> Any:
        """
        get the value for the given cell

        Args:
            key_value (Any): The value of the key column for the row to update.
            row_key (str): The column key of the cell to update.

        Returns:
            Any: the value of the cell or None if the row doesn't exist
        """
        rows_by_key = self.get_rows_by_key()
        row = rows_by_key.get(key_value, None)
        value = None
        if row:
            value = row.get(col_key, None)
        return value

    def update_cell(self, key_value: Any, col_key: str, value: Any) -> None:
        """
        Update a cell in the grid.

        Args:
            key_value (Any): The value of the key column for the row to update.
            row_key (str): The column key of the cell to update.
            value (Any): The new value for the specified cell.

        """
        rows_by_key = self.get_rows_by_key()
        row = rows_by_key.get(key_value, None)
        if row:
            row[col_key] = value

    def get_row_data(self):
        """
        get the complete row data
        """
        row_data = self.ag_grid.options["rowData"]
        return row_data

    def get_rows_by_key(self) -> Dict[Any, Dict[str, Any]]:
        """
        Organize rows in a dictionary of dictionaries, indexed by the key column value specified in GridConfig.

        Returns:
            Dict[Any, Dict[str, Any]]: A dictionary of dictionaries, with each sub-dictionary representing a row,
                                       indexed by the key column values.
        """
        data_by_key = {}
        key_col = (
            self.config.key_col
        )  # Retrieve key column name from the GridConfig instance
        for row in self.get_row_data():
            key_value = row.get(key_col, None)
            if key_value is not None:
                data_by_key[key_value] = row
        return data_by_key

    async def onSizeColumnsToFit(self, _msg: dict):
        """
        see https://www.reddit.com/r/nicegui/comments/17cg0o5/aggrid_autosize_columns_to_data_width/
        """
        # await asyncio.sleep(0.2)
        self.sizeColumnsToFit()

    def sizeColumnsToFit(self):
        if self.ag_grid:
            self.ag_grid.run_grid_method("autoSizeAllColumns")
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
                html_columns = list(range(len(columnDefs)))
                self.html_columns = html_columns
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

    async def get_selected_lod(self,lod_index=None):
        """
        selected rows are in view (e.g. potentially  html) format
        get back the original list of dict rows
        """
        selected_lod = []
        selected_rows = await self.get_selected_rows()
        if lod_index is None:
            lod_index=self.get_index(lenient=self.config.lenient,lod=self.lod)
        for row in selected_rows:
            key_value = row[self.config.key_col]
            record = lod_index[key_value]
            selected_lod.append(record)
        return selected_lod

    def select_all_rows(self):
        """
        select all my ag_grid rows
        """
        self.ag_grid.run_grid_method("selectAll")

    def deselect_all_rows(self):
        """
        deselect all my ag_grid rows
        see https://stackoverflow.com/a/52199985/1497139
        """
        self.ag_grid.run_grid_method("deselectAll")

    def toggle_select_all_rows(self):
        """
        Toggle between selecting all rows and deselecting all rows.
        """
        if self.all_selected:
            self.deselect_all_rows()
        else:
            self.select_all_rows()
        self.all_selected = not self.all_selected
        self.update_select_all_toggle_button()

    def update_select_all_toggle_button(self):
        """
        Update the toggle button's label and icon based on selection state.
        see https://github.com/zauberzeug/nicegui/discussions/3596
        """
        stb = self.select_toggle_button
        if self.all_selected:
            stb.text = "None"
            stb.props("icon=check_box_outline_blank")
        else:
            stb.text = "All"
            stb.props("icon=select_all")
        stb.update()

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

    def setup_button_row(self, button_names: list):
        """
        set up a button row

        Args:
            button_names (list): the list of buttons to be setup
        """
        with ui.row() as self.button_row:
            # icons per https://fonts.google.com/icons
            if self.config.editable:
                if "new" in button_names:
                    self.new_button = ui.button(
                        "New", icon="add", on_click=self.new_row
                    )
                if "delete" in button_names:
                    self.delete_button = ui.button(
                        "Delete", icon="delete", on_click=self.delete_selected_rows
                    )
            if "fit" in button_names:
                self.fit_button = ui.button(
                    "Fit", icon="fit_screen", on_click=self.onSizeColumnsToFit
                )
            if "all" in button_names:
                self.select_toggle_button = ui.button(
                    "All",
                    icon="select_all",
                    on_click=self.toggle_select_all_rows,
                )
