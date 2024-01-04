""" ST LINK/PRPOGRAMMER
"""

from ctypes import ArgumentError
from enum import Enum
import threading
import subprocess
import time
import os.path
from typing import Callable
from genericpath import isfile

########################################################################################################################

class STEvent(Enum):
    """ Event type for callback func
    """
    ERROR = 0

class STSetUp:
    """ Setup for ST Link
    """
    def __init__(self, addr: int, freq: int, protection: int):
        self.addr = addr
        self.freq = freq
        self.prot = protection


class STProgrammer:
    """
    Abstract Class
    """
    _fullfilename = None
    _serial = ''
    _on_event = None

    def __init__(self, fullfilename: str, on_event: Callable[[STEvent, str], None]|None=None):
        """
        Constructor

        Args:
            fullfilename (str): Full File Path name of programemr
            on_event (Callable[[STEvent, str], None]|None): Callbacke event
        
        Returns:
            STProgrammer
        """
        self._fullfilename = fullfilename
        self._on_event = on_event

    def auto_select_device(self) -> None:
        """
        Auto Select ST-LINK-Vx device
        
        Args:
            None

        Returns:
            None
        """
        devices = self.get_device_list()
        if len(devices) == 0:
            raise SystemError('ST-LINK-Vx not found!')
        if len(devices) > 1:
            raise SystemError('Too many ST-LINK-Vx found!')
        self._serial = devices[0]

    @classmethod
    def get_version(cls, fullfilename: str) -> None|str:
        """ Abstract method """
        raise NotImplementedError('This is an abstract method')

    def get_device_list(self) -> list[str]:
        """ Abstract method """
        raise NotImplementedError('This is an abstract method')

    def get_readout_protection_level(self) -> int:
        """ Abstract method """
        raise NotImplementedError('This is an abstract method')

    def set_readout_protection_level(self, level: int) -> bool:
        """ Abstract method """
        raise NotImplementedError('This is an abstract method')

    def program(self, firmware: str, st_opt: STSetUp, loader: str="") -> None:
        """ Programming device via Thread
        """
        threading.Thread(target=self.__run, args=(firmware, st_opt, loader)).start()

    @property
    def serial(self) -> str:
        """ Get serial"""
        return self._serial

    def _check_file(self, filename: str, exts: list[str]) -> bool:
        """ Check if file exists and the correct extension
        """
        if not os.path.isfile(filename):
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, f'Failed to find file "{filename}"!')
            return False
        if not filename[:-4] in exts:
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, f'Error to check extension "{exts}" in file "{filename}"!')
            return False
        return True

    def _erase_sector(self, freq: int, sect: int=1) -> bool:
        """ Abstract method """
        raise NotImplementedError('This is an abstract method')

    def _download_file(self, firmware: str, st_opt: STSetUp, loader: str) -> bool:
        """ Abstract method """
        raise NotImplementedError('This is an abstract method')

    def __run(self, firmware: str, st_opt: STSetUp, loader: str):
        """ Programming thread
        """

        if not self._check_file(firmware, ['.bin', '.hex']):
            return

        if self.set_readout_protection_level(0):
            return

        if firmware != loader:
            if not self._erase_sector(st_opt.freq, 1):
                return
            time.sleep(1)
        if not self._download_file(firmware, st_opt, loader):
            return
        if not self.set_readout_protection_level(st_opt.prot):
            return


########################################################################################################################

class STProgrammerFactory:
    """
    Factory class for ST Link & ST Programmer
    """
    def __init__(self):
        """
        Constructor method: DO NOT USE
        """
        raise NotImplementedError('Use "get_instance" class method!')

    @classmethod
    def get_instance(cls, fullfilename: str, on_event: Callable[[STEvent, str], None]|None=None) -> STProgrammer:
        """
        Factory get method

        Args:
            fullfilename (str): Full path name of ST LINK/PROGRAMMER

        Returns:
            STProgrammer: ST LINK/PROGRAMMER Class
        """

        if STLink.get_version(fullfilename) is not None:
            return STLink(fullfilename, on_event)

        if STM32Programmer.get_version(fullfilename) is not None:
            return STM32Programmer(fullfilename, on_event)

        raise NotImplementedError(f'Unable to find "{fullfilename}" !')

    @classmethod
    def version(cls) -> str:
        """ Return Version"""
        return 'version 1.0.0'

########################################################################################################################

class STLink(STProgrammer):
    """ ST Link programmer class
    """

    @classmethod
    def get_version(cls, fullfilename: str) -> None|str:
        """
        Get Version of ST Programmer CLI

        Args:
            fullfilename (str): Full path name of ST LINK/PROGRAMMER

        Returns:
            None: If fullfilename doesn't exist or is not a ST LINK
            str: Version string
        """
        if not isfile(fullfilename):
            return None
        try:
            return subprocess.check_output(f"{fullfilename } -v").decode('utf-8').splitlines()[0]
        except Exception:                                                       # pylint: disable=broad-exception-caught
            return None

    def get_device_list(self) -> list[str]:
        """ Get ST Link devices
        """
        devices = []
        if self._fullfilename is None:
            raise ArgumentError('Missing fullfilename')
        try:
            device_list = subprocess.check_output([self._fullfilename, '-List']).decode("utf-8").split()
            for i, e in enumerate(device_list):
                if e == 'SN:':
                    devices.append(device_list[i + 1])

        except Exception:                                                       # pylint: disable=broad-exception-caught
            pass
        return devices

    def get_readout_protection_level(self) -> int:
        """ Get Bit Fuse """

        if self._serial == "":
            comstr = f"{self._fullfilename} -c SWD Freq=4000 -rOB"
        else:
            comstr = f"{self._fullfilename} -c SWD Freq=4000 SN={self._serial} -rOB"

        try:
            res = subprocess.check_output(comstr)
        except Exception:                                                       # pylint: disable=broad-exception-caught
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, 'Failed find device!')
            return -1

        res = res.decode("utf-8", errors='ignore').split()
        if "RDP" not in res:
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, 'Failed to read protection level!')
            return -1
        return int(res[res.index("RDP")+3])

    def set_readout_protection_level(self, level: int) -> bool:
        """ Set Bit Fuse
        """
        if level not in [0, 1, 2]:
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, 'Protection level invalid!')
            return False

        if self._serial == "":
            comstr = f"{self._fullfilename} -c SWD Freq=4000 -OB RDP={level} -HardRst"
        else:
            comstr = f"{self._fullfilename} -c SWD Freq=4000 SN={self._serial} -OB RDP={level} -HardRst"

        try:
            subprocess.check_output(comstr)
        except Exception:                                                       # pylint: disable=broad-exception-caught
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, 'Failed to write protection level!')
            return False
        return True

    def _erase_sector(self, freq: int, sect: int=1) -> bool:
        """ Erase {sect} sector"""
        try:
            if self._serial != "":
                comstr = f"{self._fullfilename} -c SWD SN={self._serial} Freq={freq} -SE {sect}"
            else:
                comstr = f"{self._fullfilename} -c SWD Freq={freq} -SE {sect}"
            subprocess.check_output(comstr)
            return True
        except Exception:                                               # pylint: disable=broad-exception-caught
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, f'Error to Erase Sctor {sect}!')
            return False

    def _download_file(self, firmware: str, st_opt: STSetUp, loader: str) -> bool:
        """ Program device """
        if firmware == loader:
            comstr = f"{self._fullfilename} -c SWD SN={self._serial} Freq={st_opt.freq} -P {firmware} " \
                        f"{hex(st_opt.addr)} -V while_programming"
        else:
            comstr = f"{self._fullfilename} -c SWD SN={self._serial} Freq={st_opt.freq} -P {firmware} " \
                        f"{hex(st_opt.addr)} -EL {loader} -V while_programming -HardRst"
        try:
            res = subprocess.check_output(comstr)
            if 'Error occured during program operation!' in res.decode('utf-8'):
                if callable(self._on_event):
                    self._on_event(STEvent.ERROR, 'Error occured during program operation!')
                return False
            return True
        except Exception:                                                       # pylint: disable=broad-exception-caught
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, 'Error to ptogram device!')
            return False


class STM32Programmer(STProgrammer):
    """ STM32 Programmer programmer class
    """

    @classmethod
    def get_version(cls, fullfilename: str) -> None|str:
        """
        Get Version of ST Programmer CLI

        Args:
            fullfilename (str): Full path name of ST LINK/PROGRAMMER

        Returns:
            None: If fullfilename doesn't exist or is not a ST LINK
            str: Version string
        """
        if not isfile(fullfilename):
            return None
        try:
            return subprocess.check_output(f"{fullfilename } --version").decode('utf-8').splitlines()[4]
        except Exception:                                                       # pylint: disable=broad-exception-caught
            return None

    def get_device_list(self) -> list[str]:
        """ Get ST Link devices
        """
        devices = []
        if self._fullfilename is None:
            raise ArgumentError('Missing fullfilename')
        try:
            device_list = subprocess.check_output([self._fullfilename, '--List']).decode("utf-8").split()
            for i, e in enumerate(device_list):
                if e == 'SN':
                    devices.append(device_list[i + 2])

        except Exception:                                                       # pylint: disable=broad-exception-caught
            pass
        return devices

    def get_readout_protection_level(self) -> int:
        """ Get Bit Fuse """

        if self._serial == "":
            comstr = f"{self._fullfilename} -c port=SWD Freq=4000 -ob displ"
        else:
            comstr = f"{self._fullfilename} -c port=SWD Freq=4000 SN={self._serial} -ob displ"

        try:
            res = subprocess.check_output(comstr)
        except Exception:                                                       # pylint: disable=broad-exception-caught
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, 'Failed find device!')
            return -1

        res = res.decode("utf-8", errors='ignore').split()
        if "RDP" not in res:
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, 'Failed to read protection level!')
            return -1
        return int(res[res.index("RDP")+4][:-1])

    def set_readout_protection_level(self, level: int) -> bool:
        """ Set Bit Fuse
        """

        if self._serial == "":
            comstr = f"{self._fullfilename} -c port=SWD Freq=4000 -ob rdp={level}"
        else:
            comstr = f"{self._fullfilename} -c port=SWD Freq=4000 SN={self._serial} -ob rdp={level}"

        try:
            subprocess.check_output(comstr)
        except Exception:                                                       # pylint: disable=broad-exception-caught
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, 'Failed to write protection level!')
            return False
        return True

    def _erase_sector(self, freq: int, sect: int=1) -> bool:
        """ Erase {sect} sector"""
        try:
            if self._serial != "":
                comstr = f"{self._fullfilename} -c port=SWD SN={self._serial} Freq={freq} -E {sect}"
            else:
                comstr = f"{self._fullfilename} -c port=SWD Freq={freq} -E {sect}"
            subprocess.check_output(comstr)
            return True
        except Exception:                                               # pylint: disable=broad-exception-caught
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, f'Error to Erase Sctor {sect}!')
            return False

    def _download_file(self, firmware: str, st_opt: STSetUp, loader: str) -> bool:
        """ Program device """
        if firmware == loader:
            comstr = f"{self._fullfilename} -c port=SWD SN={self._serial} Freq={st_opt.freq} -w {firmware} " \
                        f"{hex(st_opt.addr)} -V -HardRst"
        else:
            comstr = f"{self._fullfilename} -c port=SWD SN={self._serial} Freq={st_opt.freq} -w {firmware} " \
                        f"{hex(st_opt.addr)} -EL {loader} -HardRst"
        try:
            res = subprocess.check_output(comstr)
            if 'Error occured during program operation!' in res.decode('utf-8'):
                if callable(self._on_event):
                    self._on_event(STEvent.ERROR, 'Error occured during program operation!')
                return False
            return True
        except Exception:                                                       # pylint: disable=broad-exception-caught
            if callable(self._on_event):
                self._on_event(STEvent.ERROR, 'Error to ptogram device!')
            return False

def test(fullfilename: str) -> None:
    """ Testing """
    stprog = STProgrammerFactory.get_instance(fullfilename)
    print(stprog.get_device_list())
    stprog.auto_select_device()
    print(f'serial is {stprog.serial}')
    print(f'RDP = {stprog.get_readout_protection_level()}')
    stprog.set_readout_protection_level(0)


if __name__ == '__main__':
    STLINK = r".\ST_Link_utility\ST-LINK_CLI.exe"
    print(STLink.get_version(STLINK))
    STM32PROG = r"C:/Program Files/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe"
    print(STM32Programmer.get_version(STM32PROG))

    test(STLINK)
    test(STM32PROG)
