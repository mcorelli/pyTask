"""
This is the template to must use in the PyTaskManage
"""

from abc import abstractmethod
from enum import Enum
from typing import Callable
from genericpath import isfile
from yaml import safe_load


class BaseStatus(Enum):
    """ Event type for callback func
    """
    OK = 0
    ERROR = -1

class TaskBase:
    """
    Task base abstract class
    """
    _cnf = {}

    def __init__(self, fullfilename: str|None=None, on_event: Callable[[BaseStatus, str], None]|None=None):
        """
        Constructor
        """
        if fullfilename is not None:
            self.load_cnf(fullfilename)
        self._on_event = on_event

    def load_cnf(self, fullfilename: str) -> None:
        """ Load file conf into cnf dict """
        if not isfile(fullfilename):
            raise FileNotFoundError
        with open(fullfilename, 'r', encoding='utf-8') as file:
            self._cnf = safe_load(file)

    def run(self) -> None:
        """ Run """
        self._init()
        self._run()
        self._final()

    def _init(self) -> None:
        """ Initialization before Run"""
        return

    def _final(self) -> None:
        """ Finalization after Run"""
        return

    @abstractmethod
    def _run(self) -> None:
        """ Abstract method """
        raise NotImplementedError('This is an abstract method')

if __name__ == "__main__":
    base = TaskBase()
    base.run()
