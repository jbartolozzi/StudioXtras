import os
import shutil
import psutil
import hou


def _getMemLoad():
    app_mem = float(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
    total_mem = float(psutil.virtual_memory().total / 1024 ** 2)
    return app_mem, total_mem


def getLoad():
    node = hou.node("../")
    app_mem, total_mem = _getMemLoad()
    if "ui" not in dir(hou):
        return 0
    else:
        max_mem_usage = total_mem * float(node.parm("max_mem_percent").eval()) / 100.0
        if (app_mem > max_mem_usage):
            node.parm("cache_mode_label").set("Caching to Disk")
            return 2
        else:
            node.parm("cache_mode_label").set("Caching to RAM")
            return 1


def deleteFileCache(node):
    string = hou.expandString(node.parm("file_cache_location").eval())
    directory = os.path.dirname(string)
    if os.path.exists(directory):
        try:
            shutil.rmtree(directory)
        except:
            print("Unable to delete %s" % directory)
