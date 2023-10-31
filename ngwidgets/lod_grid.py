"""
Created on 2023-10-3

@author: wf
"""
import datetime
from nicegui import ui
import asyncio

class ListOfDictsGrid:
    """
    ag grid based on list of dict
    
    see https://nicegui.io/documentation/ag_grid
    
    """

    def __init__(self,lod=None,columnDefs:list=None,options={},theme="ag-theme-material",classes="h-80"):
        """
        Constructor
        """
        self.lod=lod
        self.ag_grid=ui.aggrid(options).classes(classes)
        self.ag_grid.theme=theme 
        self.setDefaultColDef()
        ui.button("resize",on_click=self.onSizeColumnsToFit)
        if lod is not None:
            self.load_lod(lod, columnDefs)
     
        #self.onSizeColumnsToFit()
        #self.agGrid.html_columns = [0, 1, 2]
        #   self.agGrid.on('rowSelected', self.onRowSelected)
        #self.ag_grid.options["columnDefs"][0]["checkboxSelection"] = True

   
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
        self.ag_grid.update()
