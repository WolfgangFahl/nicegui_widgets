"""
Created on 2023-11-02
Updated on 2026-10-09 - live test environment, nicegui 3 row data semantics

@author: wf
"""

from typing import Dict, List

from nicegui import Client, ui
from starlette.responses import JSONResponse

from ngwidgets.lod_grid import GridConfig, ListOfDictsGrid
from ngwidgets.test_live import LiveCmd, LiveWebserver, LiveWebTest


class LodGridWebserver(LiveWebserver):
    """
    Webserver with pages that exercise a ListOfDictsGrid

    the grid needs a page context - a grid created outside a page
    has no client once the server runs
    """

    @staticmethod
    def get_lod() -> List[Dict]:
        """
        the list of dicts of the pages

        Returns:
            List[Dict]: three persons
        """
        lod = [
            {"name": "Alice", "age": 18, "parent": "David"},
            {"name": "Bob", "age": 21, "parent": "Eve"},
            {"name": "Carol", "age": 42, "parent": "Frank"},
        ]
        return lod

    @staticmethod
    def get_grid(lod: List[Dict]) -> ListOfDictsGrid:
        """
        create a grid keyed by name for the given lod

        Args:
            lod: the list of dicts to load

        Returns:
            ListOfDictsGrid: the grid
        """
        grid_config = GridConfig(key_col="name", debug=True)
        lod_grid = ListOfDictsGrid(lod, config=grid_config)
        return lod_grid

    def __init__(self):
        super().__init__()

        @ui.page("/lod_grid/index")
        async def lod_grid_index(client: Client):
            lod = self.get_lod()
            lod_grid = self.get_grid(lod)
            result = {
                "keys": list(lod_grid.lod_index.keys()),
                "row_count": len(lod_grid.ag_grid.options["rowData"]),
                "column_count": len(lod_grid.ag_grid.options["columnDefs"]),
                "html_columns": lod_grid.html_columns,
                "cell_renderer": ":cellRenderer"
                in lod_grid.ag_grid.options["columnDefs"][0],
            }
            return JSONResponse(content=result)

        @ui.page("/lod_grid/update_cell")
        async def lod_grid_update_cell(client: Client):
            lod = self.get_lod()
            lod_grid = self.get_grid(lod)
            lod_grid.update_cell("Alice", "age", 19)
            result = {
                "index_age": lod_grid.lod_index["Alice"]["age"],
                "lod_age": lod[0]["age"],
                "grid_age": lod_grid.ag_grid.options["rowData"][0]["age"],
                "cell_value": lod_grid.get_cell_value("Alice", "age"),
            }
            return JSONResponse(content=result)

        @ui.page("/lod_grid/new_row")
        async def lod_grid_new_row(client: Client):
            lod = self.get_lod()
            lod_grid = self.get_grid(lod)
            lod_grid.config.keygen_callback = lambda: "Dan"
            await lod_grid.new_row(None)
            result = {
                "keys": list(lod_grid.lod_index.keys()),
                "grid_keys": [
                    row["name"] for row in lod_grid.ag_grid.options["rowData"]
                ],
            }
            return JSONResponse(content=result)


class LodGridCmd(LiveCmd):
    """
    Cmd class for the LodGridWebserver
    """

    def __init__(self, config, server_class):
        super().__init__(config=config, webserver_cls=server_class)


class TestLodGrid(LiveWebTest):
    """
    test ListOfDictsGrid in the live test environment
    """

    @classmethod
    def setUpClass(cls):
        cls.ws = LodGridWebserver()
        cls.cmd = LodGridCmd(cls.ws.config, LodGridWebserver)
        cls.start_runner()

    def setUp(self, debug=False, profile=True):
        super().setUp(debug=debug, profile=profile)

    def test_lod_index(self):
        """
        test the list of dicts indexing and the loaded grid
        """
        result = self.get_json("/lod_grid/index")
        if self.debug:
            print(result)
        self.assertEqual(["Alice", "Bob", "Carol"], result["keys"])
        self.assertEqual(3, result["row_count"])
        self.assertEqual(3, result["column_count"])
        self.assertEqual([0, 1, 2], result["html_columns"])
        self.assertTrue(result["cell_renderer"])

    def test_update_cell(self):
        """
        test the update_cell API function - the change reaches
        the index, the lod and the grid
        """
        result = self.get_json("/lod_grid/update_cell")
        if self.debug:
            print(result)
        for key in ["index_age", "lod_age", "grid_age", "cell_value"]:
            self.assertEqual(19, result[key], key)

    def test_new_row(self):
        """
        test that a new row reaches the index and the grid
        """
        result = self.get_json("/lod_grid/new_row")
        if self.debug:
            print(result)
        self.assertEqual(["Dan", "Alice", "Bob", "Carol"], result["keys"])
        self.assertEqual(result["keys"], result["grid_keys"])
