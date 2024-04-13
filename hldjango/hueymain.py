# see https://huey.readthedocs.io/en/latest/imports.html for evilness
from hueyconfig import huey
from lib.hl.hltasks import queueTaskBuildStoryPdf

# python modules
import sys
import os

# copied from huey_consumer.py
from huey.bin import huey_consumer


from lib.jr import jrfuncs

# when running tasks via huey we need to set this global
logdir = os.path.abspath(os.path.dirname(__file__))
logdir += "/jrlogs/huey"
print(logdir)
jrfuncs.setLogFileDir(logdir)


if __name__ == '__main__':
    print("Trying to start up huey consumer..")
    if sys.version_info >= (3, 8) and sys.platform == 'darwin':
        import multiprocessing
        try:
            multiprocessing.set_start_method('fork')
        except RuntimeError:
            pass
    huey_consumer.consumer_main()
