""" Main file """

from importlib import import_module


def load_module(module_name: str, alias: str|None=None) -> None:
    """ Import an external module """
    if alias is not None:
        mod_ref = alias
    else:
        mod_ref = module_name
    globals()[mod_ref] = import_module(f'tasks.{module_name}')

if __name__ == "__main__":
    load_module('template_task')

    # base = template_task.TaskBase()
    # base.run()

    load_module('program_st_task', 'pgmst')

    # pylint: disable=undefined-variable
    prog = pgmst.ProgramSTDevice()                          # pyright: ignore[reportUndefinedVariable]
    prog.run()

    # from tasks import program_st_task
    # prog = program_st_task.ProgramSTDevice()
    # prog.run()
