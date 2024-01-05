"""
This is the template to must use in the PyTaskManage
"""

from abc import abstractmethod
from enum import Enum
from typing import Callable
import logging
from helper.files import load_yaml

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
            logging.info('Load cnf %s', fullfilename)
            self._cnf = load_yaml(fullfilename)
        self._on_event = on_event

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
