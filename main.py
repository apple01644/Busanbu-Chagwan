import importlib
import os

import static

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
for child in os.listdir(ROOT_DIR):
    if child.endswith('.py'):
        importlib.import_module(child[:-3])

static.discord_bot.run()
