"""
Helper function to manage YAML and files
"""
import os
import sys
import yaml

def ext_chg(fullfilename: str, extension: str) -> str:
    """Change the file extension

    Args:
        fullfilename (str): filename to change extension
        extension (str): new extension

    Returns:
        str: filename with extension changed
    """
    newfilename = os.path.splitext(fullfilename)[0] + extension
    return newfilename


def load_yaml(fullfilename: str) -> dict:
    """Load a YAML file into a dictionary_

    Args:
        fullfilename (str): file to load

    Raises:
        FileNotFoundError: Raises if file not exists

    Returns:
        dict: Dictionary returned
    """
    if not os.path.isfile(fullfilename):
        raise FileNotFoundError
    with open(fullfilename, 'r', encoding='utf-8') as file:
        cnf = yaml.safe_load(file)
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
    backupfilename = ext_chg(fullfilename, '.bak')
    if os.path.isfile(fullfilename):
        if backup:
            if os.path.isfile(backupfilename):
                os.remove(backupfilename)
            os.rename(fullfilename, backupfilename)
    with open(fullfilename, 'w', encoding='utf-8') as file:
        yaml.dump(data, file)


def get_app_path(app: str) -> str:
    """Return execution path

    Returns:
        str: Execution path
    """
    application_path = ''
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif app:
        application_path = os.path.dirname(app)
    return application_path
