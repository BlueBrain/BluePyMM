import contextlib
import os

@contextlib.contextmanager
def cd(dir):
    old_cwd = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(old_cwd)
