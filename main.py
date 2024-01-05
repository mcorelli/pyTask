""" Main file """
import logging
import logging.handlers
import os
from enum import Enum
from helper.files import load_yaml, save_yaml, get_app_path
from helper.load import load_task


def callback(status: Enum, msg: str):
    """ Call back funct """
    print(f'callback: status "{status}" message "{msg}"')


def cnf_default() -> dict:
    """ Create default configuration

    Returns:
        dict: default configuration
    """
    _cnf = {
        'log': {'filename': './log/pyTask.log', 'level': 'WARNING'}, 
    }
    return _cnf

def cnf_load(filename: str) -> dict:
    """Load configuration file

    Args:
        filename (str): fullfilename of config file

    Returns:
        dict: configuration loaded
    """
    try:
        _cnf = load_yaml(filename)
    except FileNotFoundError:
        _cnf = cnf_default()
        save_yaml(_cnf, filename)
    return _cnf


def log_init(log_cnf: dict) -> None:
    """Logger initializatiob

    Args:
        log_cnf (dict): Logger config
    """
    logging.basicConfig(
        format='%(asctime)s:%(levelname)-9s: %(message)s',
        handlers=[logging.handlers.TimedRotatingFileHandler(filename=log_cnf['filename'], when='W0', interval=4)],
        datefmt='%Y-%m-%d %H:%M:%S',
        level=log_cnf['level'])

if __name__ == "__main__":

    CNF_PATH = os.path.join(get_app_path(__file__), 'config')
    CNF_FILE = os.path.join(CNF_PATH, 'pytask.yml')
    SEQ_FILE = r'./sequences/test_seq_base.yml'

    cnf = cnf_load(CNF_FILE)
    log_init(cnf['log'])

    logging.info('Starting')

    if SEQ_FILE is not None:
        sequence = load_yaml(SEQ_FILE)
        logging.info('Loaded sequence: %s', sequence["Name"])
        logging.info('Description    : %s', sequence["Description"])
        for task in sequence['Tasks']:
            logging.info('Load: %s, module <%s>', task["task"], task["module"])

            tsk = load_task(task["module"], CNF_PATH, task["args"], callback)
            tsk.run()

        logging.info('Completed')
