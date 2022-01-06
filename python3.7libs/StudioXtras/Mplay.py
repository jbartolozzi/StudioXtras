import hou
from importlib import reload
from StudioXtras import Utils
reload(Utils)


def run():
    Utils.makeTimestampEnv()
    node = hou.pwd()  # hou.node("..")
    helper = Utils.RopHelper(node.name())
    op = helper.getTargetOutputNode(node)
    if op is None:
        return
    first_frame = helper.getParm(op, "f1")
    last_frame = helper.getParm(op, "f2")
    step = helper.getParm(op, "f3")
    picture_parm = helper.getPictureParm(op)

    images = helper.getImageList(first_frame, last_frame, step, picture_parm, check_if_exists=True)
    mplay_executable = helper.executablePath("mplay")

    command = "%s %s" % (mplay_executable, " ".join(images))
    Utils.runCommand(command, background=True)
