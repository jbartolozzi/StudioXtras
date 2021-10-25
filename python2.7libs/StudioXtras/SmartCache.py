import os
import shutil
import hou
from StudioXtras import Utils


def getLoad():
    node = hou.node("../")
    used, percent = Utils.getAppLoad()
    if "ui" not in dir(hou):
        return 0
    else:
        return 2 if (percent > node.parm("max_mem_percent").eval()) else 1


def deleteFileCache(node):
    string = hou.expandString(node.parm("file_cache_location").eval())
    directory = os.path.dirname(string)
    if os.path.exists(directory):
        try:
            shutil.rmtree(directory)
        except:
            print("Unable to delete %s" % directory)
