"""
Helper function to manage YAML and files
"""
from os import remove, rename
from os.path import isfile, splitext
from yaml import dump, safe_load


def load_yaml(fullfilename: str) -> dict:
    """Load a YAML file into a dictionary_

    Args:
        fullfilename (str): file to load

    Raises:
        FileNotFoundError: Raises if file not exists

    Returns:
        dict: Dictionary returned
    """
    if not isfile(fullfilename):
        raise FileNotFoundError
    with open(fullfilename, 'r', encoding='utf-8') as file:
        cnf = safe_load(file)
        return cnf
    return {}


def save_yaml(data: dict, fullfilename: str, backup: bool=True) -> None:
    """Save a dictionary as YAML file

    Args:
        data (dict): yaml data
        fullfilename (str): yaml file
        backup (bool, optional): if True create a backup file. Defaults to True.
    """
    # Backup old yaml file
    backupfilename = splitext(fullfilename)[0] + '.bak'
    if isfile(fullfilename):
        if backup:
            if isfile(backupfilename):
                remove(backupfilename)
            rename(fullfilename, backupfilename)
    with open(fullfilename, 'w', encoding='utf-8') as file:
        dump(data, file)
