""" Main file """

from importlib import import_module
from yaml import safe_load
from tasks.template_task import TaskBase


def load_module(module_name: str, alias: str|None=None) -> None:
    """ Import an external module """
    if alias is not None:
        mod_ref = alias
    else:
        mod_ref = module_name
    globals()[mod_ref] = import_module(f'tasks.{module_name}')


def get_task(module_name: str, config_path: str) -> TaskBase:
    """ Return TaskBase from a task class """
    module = import_module(f'tasks.{module_name}')
    factory = getattr(module, 'get_task')
    return factory(config_path)


if __name__ == "__main__":

    print('\nStarting.\n')
    CNFG_PATH = r'./config'
    SEQUENCE = r'./sequences/test_sequence.yml'

    if SEQUENCE is not None:
        with open(SEQUENCE, 'r', encoding='utf-8') as file:
            sequence = safe_load(file)
        print(f'Loaded sequence: {sequence["Name"]}')
        print(f'Description    : {sequence["Description"]}\n')
        for task in sequence['Tasks']:
            print(f'Load: {task["task"]}, module <{task["module"]}>')

            tsk = get_task(task["module"], CNFG_PATH, task["args"])
            tsk.run()

        print('\nCompleted.\n')
