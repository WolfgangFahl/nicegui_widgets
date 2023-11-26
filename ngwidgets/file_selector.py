'''
Created on 2023-07-24

@author: wf
'''
from typing import Callable, Dict, List, Optional, Union
from nicegui import ui
from nicegui.events import ValueChangeEventArguments
import inspect
import os

class FileSelector():
    """
    nicegui FileSelector
    """
    def __init__(self,path:str,extensions: dict=None,handler:Callable=None,filter_func: Callable[[str], bool] = None,create_ui:bool=True):
        """
        constructor
        
        Args:
            path (str): The path to the directory to start building the tree from.
            extensions(dict): the extensions to filter for as a dictionary with name as key and extension as value
            handler(Callable): handler function to call on selection
            filter_func(Callable): optional filter function
            create_ui(bool): if True create the self.tree ui.tree nicegui component - allows for testing the structure without ui by setting to False
        """   
        self.path=path
        if extensions is None:
            extensions = {"srt": ".SRT", "gpx": ".gpx"}
        self.extensions=extensions 
        self.handler=handler
        self.filter_func=filter_func
        # generate the tree structure
        self.tree_structure = self.get_dir_tree(self.path, self.extensions)

        if create_ui:
            # create the ui.tree object
            self.tree=ui.tree([self.tree_structure], label_key='label', on_select=self.select_file)       
    
    def get_path_items(self, path: str) -> List[str]:
        """
        Get sorted list of items in a specified directory path, filtering out non-relevant files like `._` files.
    
        Args:
            path (str): The directory path to list items from.
    
        Returns:
            List[str]: A sorted list of relevant items from the directory. 
                       Returns an empty list if an error occurs.
    
        """
        items = []
        
        try:
            all_items = os.listdir(path)
            
            for item in all_items:
                if not item.startswith('._'):
                    if not self.filter_func or self.filter_func(item):
                        items.append(item)
            
            items.sort()
        except BaseException:
            pass
    
        return items
        
    def get_dir_tree(self, path: str, extensions: dict, id_path: List[int] = [1]) -> Optional[Dict[str, Union[str, List[Dict]]]]:
        """
        Recursive function to construct a directory tree.
    
        Args:
            path (str): The path to the directory to start building the tree from.
            extensions(dict): the extensions to filter for as a dictionary with name as key and extension as value
            id_path (List[int]): List of integers representing the current path in the tree.
    
        Returns:
            dict: A dictionary representing the directory tree. For each directory or .scad file found,
            it will add a dictionary to the 'children' list of its parent directory's dictionary.
        """
        path = os.path.abspath(path)
        id_string = '.'.join(map(str, id_path))
        items=self.get_path_items(path)
        children = []
        item_counter = 1  # counter for generating child id
    
        # Iterating over directories first
        for name in items:
            item_path = os.path.join(path, name)
            child_id_path = id_path + [item_counter]
    
            if os.path.isdir(item_path):
                dir_tree = self.get_dir_tree(item_path, extensions, child_id_path)
                if dir_tree:
                    children.append(dir_tree)
                    item_counter += 1
    
        # Then iterating over files
        # Check if an empty string is an allowed extension
        allow_no_extension = "" in extensions.values()
        for name in items:
            item_path = os.path.join(path, name)
            child_id_path = id_path + [item_counter]
    
            # make sure the item is a file
            if not os.path.isdir(item_path):
  
                # Check if the item has an extension that matches the allowed extensions
                has_allowed_extension = any(name.endswith(ext) for ext in extensions.values() if ext)

                # Check if the item has no extension and no extension is allowed
                is_no_extension_allowed = allow_no_extension and '.' not in name

                # Proceed if the item either has an allowed extension or no extension is allowed
                if has_allowed_extension or is_no_extension_allowed:
                    children.append({
                        'id': '.'.join(map(str, child_id_path)),
                        'label': name,
                        'value': item_path,
                    })
                    item_counter += 1
    
        if children:
            return {
                'id': id_string,
                'label': os.path.basename(path),
                'value': path,
                'children': children,
            }

    def find_node_by_id(self, tree: Dict[str, Union[str, List[Dict]]], id_to_find: str) -> Optional[Dict[str, Union[str, List[Dict]]]]:
        """
        Recursive function to find a node (file or directory) by its ID in a directory tree.
    
        Args:
            tree (dict): A dictionary representing the directory tree. The tree is constructed with each node 
                containing 'id' (str) as a unique identifier, 'value' (str) as the path to the file or directory,
                and 'children' (list of dict) as a list of child nodes.
            id_to_find (str): The ID of the node to find in the directory tree.
    
        Returns:
            dict: The node associated with the found ID. Returns None if the ID is not found.
        """
        if tree['id'] == id_to_find:
            return tree
        
        for child in tree.get('children', []):
            found = self.find_node_by_id(child, id_to_find)
            if found:
                return found
                
        return None
    
    def expand(self,node_ids: List[str]) -> None:
        """
        expand the nodes with the given ids
        
        node_ids(list): the list of node ids to be expanded
        """
        self.tree._props['expanded'] = node_ids
        self.tree.update()
    
    async def select_file(self,vcea:ValueChangeEventArguments):
        """
        select the given file and call my handler on the file path of it
        
        Args:
            vcea(ValueChangeEventArguments): the tree selection event
        """
        id_to_find = vcea.value  # Assuming vcea.value contains the id
        if id_to_find is None:
            return 
        
        selected_node = self.find_node_by_id(self.tree_structure, id_to_find)
        if selected_node is None:
            raise ValueError(f"No item with id {id_to_find} found in the tree structure.")
        
        file_path = selected_node['value']
        
        # Only expand the node if it is a directory
        if os.path.isdir(file_path):
            # Access the children of the selected node and get their ids
            if 'children' in selected_node:
                child_ids = [child['id'] for child in selected_node['children']]
                self.expand(child_ids)
        else:
            if self.handler:
                if inspect.iscoroutinefunction(self.handler):
                    await self.handler(file_path)
                else:
                    self.handler(file_path) 
                # Close all nodes if it is a file
            self.expand([])