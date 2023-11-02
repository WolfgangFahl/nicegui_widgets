"""
Created on 2023-10-3

@author: wf
"""
import datetime
from nicegui import ui
import asyncio
import sys

class ListOfDictsGrid:
    """
    ag grid based on list of dict
    
    see https://nicegui.io/documentation/ag_grid
    
    """

    def __init__(self,lod=None,key_col:str="#",columnDefs:list=None,options={},theme="ag-theme-material",classes="h-80",lenient:bool=False):
        """
        Constructor
        """
        self.lod=lod
        self.key_col=key_col
        self.lenient=lenient
        self.lod_index = {}
        self.ag_grid=ui.aggrid(options).classes(classes)
        self.ag_grid.theme=theme 
        self.setDefaultColDef()
        ui.button("resize",on_click=self.onSizeColumnsToFit)
        ui.button('Select all', on_click=lambda: self.ag_grid.call_api_method('selectAll'))
        if lod is not None:
            self.load_lod(lod, columnDefs)
     
        #self.onSizeColumnsToFit()
        #self.agGrid.html_columns = [0, 1, 2]
        #   self.agGrid.on('rowSelected', self.onRowSelected)
        #self.ag_grid.options["columnDefs"][0]["checkboxSelection"] = True

    def update_index(self,lenient:bool=False):
        """
        update the index based on the given key column
        """
        self.lod_index={}
        for row_index,row in enumerate(self.lod):
            if self.key_col in row:
                key_value=row[self.key_col]
                self.lod_index[key_value]=row
            else:
                msg=f"missing key column {self.key_col} in row {row_index}"
                if not lenient:
                    raise Exception(msg)
                else:
                    print(msg,file=sys.stderr)
                # missing key
                pass

    def get_row_for_key(self, key_value:str):
        row=self.lod_index.get(key_value,None)
        return row

    def update_row(self, key_value, row_key, value):
        """
        Update a row in the grid.
        """
        row=self.get_row_for_key(key_value)
        if row:
            row_data=self.get_row_data()
            for grid_row in row_data:
                if row[self.key_col] == grid_row[self.key_col]:
                    grid_row[row_key] = value
            
    def get_row_data(self):
        row_data=self.ag_grid.options["rowData"]
        return row_data
    
    async def onSizeColumnsToFit(self,_msg:dict):      
        await asyncio.sleep(0.2)
        if self.ag_grid:
            self.ag_grid.call_api_method("sizeColumnsToFit")
            self.ag_grid.update()
               
    def setDefaultColDef(self):
        """
        set the default column definitions
        """
        if not "defaultColDef" in self.ag_grid.options:
            self.ag_grid.options["defaultColDef"]={}
        defaultColDef=self.ag_grid.options["defaultColDef"]
        defaultColDef["resizable"]=True
        defaultColDef["sortable"]=True
        # https://www.ag-grid.com/javascript-data-grid/grid-size/
        defaultColDef["wrapText"]=True
        defaultColDef["autoHeight"]=True
        
    def load_lod(self,lod:list,columnDefs:list=None):
        """
        load the given list of dicts
        
        Args:
            lod(list): a list of dicts to be loaded into the grid
            columnDefs(list): a list of column definitions
        """
        if columnDefs is None:
            # assume lod
            columnDefs = []
            if len(lod)>0:
                header=lod[0]
                for key, value in header.items():
                    if isinstance(value, int) or isinstance(value, float):
                        col_filter = "agNumberColumnFilter"
                    elif isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                        col_filter = "agDateColumnFilter"
                    else:
                        col_filter = True  # Use default filter
                    columnDefs.append(dict({'field': key, "filter": col_filter}))
        self.ag_grid.options["columnDefs"]=columnDefs
        self.ag_grid.options["rowData"]=lod
        self.update_index(lenient=self.lenient)
        
    def update(self):
        if self.ag_grid:
            self.ag_grid.update()