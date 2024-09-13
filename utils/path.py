import os
from pathlib import Path

def get_project_root():
    """
    Find the root directory of the project.
    Assumes that the 'data' directory is directly under the project root.
    """
    current_path = Path.cwd()
    while current_path.name != 'root':
        if (current_path / 'data').exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError("Project root not found")

def resolve_data_path(filename):
    """
    Resolve the absolute path to a file in the data directory.
    
    :param filename: Name of the file in the data directory
    :return: Absolute path to the file
    """
    root_dir = get_project_root()
    return os.path.abspath(os.path.join(root_dir, 'data', filename))

def resolve_notebook_path(filename):
    """
    Resolve the absolute path to a notebook file in the notebooks directory.
    
    :param filename: Name of the notebook file in the notebooks directory
    :return: Absolute path to the notebook file
    """
    root_dir = get_project_root()
    return os.path.abspath(os.path.join(root_dir, 'notebooks', filename))


