"""
Helper function to manage module and task loading
"""
from importlib import import_module
from enum import Enum
from typing import Callable
from tasks.template_task import TaskBase


def load_module(module_name: str, alias: str|None=None) -> None:
    """Import an external module

    Args:
        module_name (str): module to be loaded
        alias (str | None, optional): Alias. Defaults to None.
    """
    if alias is not None:
        mod_ref = alias
    else:
        mod_ref = module_name
    globals()[mod_ref] = import_module(f'tasks.{module_name}')


def load_task(module_name: str, config_path: str, args: dict, event: Callable[[Enum, str], None]|None=None) -> TaskBase:
    """Return TaskBase from a task class

    Args:
        module_name (str): task module name
        config_path (str): path where config files are saved
        args (dict): task parmas
        event (Callable[[Enum, str], None] | None, optional): callback function. Defaults to None.

    Returns:
        TaskBase: _description_
    """
    module = import_module(f'tasks.{module_name}')
    factory = getattr(module, 'get_task')
    return factory(config_path, args, event)
