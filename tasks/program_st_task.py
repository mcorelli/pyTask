"""
Program device ST with ST LINK/PROGRAMMER
"""

from os import path
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Callable
from tasks.template_task import TaskBase
from tasks.utility import st_programmer


class ProgramSTDevice(TaskBase):
    """
    Task to program ST devices
    """
    def __init__(self, configpath:str, args: dict, on_event: Callable[[Enum, str], None]|None=None):
        """ Constructor """
        fullfilename = path.join( path.abspath(configpath), Path(__file__).stem + '.yml')
        super().__init__(fullfilename, on_event)
        self.__st_pgm = st_programmer.STProgrammerFactory.get_instance(self._cnf['programmer'], on_event)
        if args['loader'] is not None:
            raise NotImplementedError
        if args['bootloader'] is not None:
            raise NotImplementedError
        self.__firmware = args['firmware']

    def _run(self) -> None:
        """ Run method """
        self.__st_pgm.program(self.__firmware)
        while self.__st_pgm.downloading:
            sleep(5)
            print('.', end='')

    def version(self) -> str:
        return "1.0.0"



def get_task(configpath:str, args: dict, callback: Callable[[Enum, str], None]|None=None) -> TaskBase:
    """
    Return the class name of the Task
    """
    return ProgramSTDevice(configpath, args, callback)
