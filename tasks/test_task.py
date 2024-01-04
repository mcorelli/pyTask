"""
A simple test task
"""

from os import path
from pathlib import Path
from tasks.template_task import TaskBase


class Test(TaskBase):
    """
    Simple Task
    """
    def __init__(self, configpath:str):
        """ Constructor """
        fullfilename = path.join( path.abspath(configpath), Path(__file__).stem + '.yml')
        super().__init__(fullfilename)
        self.__say__ = self._cnf['say_ho_ho']

    def _init(self) -> None:
        """ Init """
        print('\tMhhh')

    def _run(self):
        """ Run method """
        print(self.__say__)

    def _final(self) -> None:
        """ Finalization after Run"""
        print('\tOOOhhh')


def get_task(configpath:str, args: dict) -> TaskBase:
    """
    Return the class name of the Task
    """
    _ = args
    return Test(configpath)
