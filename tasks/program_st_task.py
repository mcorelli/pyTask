"""
Program device ST with ST LINK/PROGRAMMER
"""

from os import path
from tasks.template_task import TaskBase
from tasks.utility import st_programmer

class ProgramSTDevice(TaskBase):
    """
    Task to program ST devices
    """
    def __init__(self, configpath:str):
        """ Constructor """
        fullfilename = path.join(configpath, __file__)
        super().__init__()
        __st_pgm = st_programmer.STProgrammerFactory.get_instance(fullfilename)

    def run(self):
        """ Run method """
        print('Ho ho ho')

if __name__ == '__main__':
    task = ProgramSTDevice(r'../config')
    task.run()
