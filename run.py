import importlib
import os

import static

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def import_files(path, extra_dir=''):
    ls = {entry.name: entry for entry in os.scandir(path + extra_dir)}
    for path_name in ls:
        child = ls[path_name]
        if child.is_dir():
            is_module = False
            for child_of_child in os.scandir(ROOT_DIR + '/' + child.name):
                if child_of_child.is_file():
                    if child_of_child.name == '__init__.py':
                        is_module = True
                        break
            if is_module:
                import_files(ROOT_DIR, extra_dir + '/' + child.name)
        elif child.is_file():
            if child.name.endswith('.py') and child.name != '__init__.py':
                import_path = child.name[:-3]
                if len(extra_dir) > 0:
                    import_path = extra_dir.replace('/', '.')[1:] + '.' + import_path
                if extra_dir == '' and import_path == 'run':
                    pass
                else:
                    importlib.import_module(import_path)


import_files(ROOT_DIR)
static.discord_bot.run()
