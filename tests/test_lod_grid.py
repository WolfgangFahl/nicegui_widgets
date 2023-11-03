'''
Created on 2023-11-02

@author: wf
'''
from ngwidgets.basetest import Basetest
from ngwidgets.lod_grid import ListOfDictsGrid

class TestLodGrid(Basetest):
    '''
    test ListOfDictsGrid
    '''
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.lod=[
            {'name': 'Alice', 'age': 18, 'parent': 'David'},
            {'name': 'Bob', 'age': 21, 'parent': 'Eve'},
            {'name': 'Carol', 'age': 42, 'parent': 'Frank'},
        ]
        self.lod_grid=ListOfDictsGrid(self.lod,key_col="name")

    def test_lod_index(self):
        """
        test the list of dics indexing
        """
        debug=self.debug
        #debug=True
        if debug:
            print(self.lod_grid.lod_index)
        self.assertTrue("Alice" in self.lod_grid.lod_index)
            

    def test_update_row(self):
        new_age=19
        self.lod_grid.update_row("Alice","age",new_age)
        alice_row=self.lod_grid.lod_index["Alice"]
        self.assertEqual(new_age,alice_row["age"])
    
        