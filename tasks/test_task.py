"""
A simple test task
"""

from os import path
from pathlib import Path
from typing import Callable
from tasks.template_task import BaseStatus, TaskBase


class Test(TaskBase):
    """
    Simple Task
    """
    def __init__(self, configpath:str, on_event: Callable[[BaseStatus, str], None]|None=None):
        """ Constructor """
        fullfilename = path.join( path.abspath(configpath), Path(__file__).stem + '.yml')
        super().__init__(fullfilename, on_event)
        self.__say__ = self._cnf['say_ho_ho']

    def _init(self) -> None:
        """ Init """
        print('\tMhhh')
        if callable(self._on_event):
            self._on_event(BaseStatus.OK, 'Init')

    def _run(self):
        """ Run method """
        print(self.__say__)

    def _final(self) -> None:
        """ Finalization after Run"""
        print('\tOOOhhh')
        if callable(self._on_event):
            self._on_event(BaseStatus.OK, 'Init')


def get_task(configpath:str, args: dict, callback: Callable[[BaseStatus, str], None]|None=None) -> TaskBase:
    """
    Return the class name of the Task
    """
    _ = args
    return Test(configpath, callback)
