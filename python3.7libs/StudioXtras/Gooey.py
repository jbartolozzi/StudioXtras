import hou
import json
from importlib import reload
from StudioXtras import Utils
reload(Utils)


def run():
    node = hou.pwd()
    helper = Utils.RopHelper(node.name(), debug=node.parm("debug").eval())
    hou.hipFile.save(file_name=None, save_to_recent_files=True)
    if len(node.inputs()):
        target = node.inputs()[0]
    else:
        target = hou.node(node.parm("target").eval())
    if not target:
        helper.error("Invalid target ROP specified")
        return

    gooey_file = Utils.getGooeyFileName()
    out_dict = {"rop": target.path(), "hip": hou.hipFile.path()}
    with open(gooey_file, 'w') as outfile:
        json.dump(out_dict, outfile)

    houdinifx = helper.executablePath("houdinifx")
    command = f"{houdinifx} {hou.hipFile.path()}"
    cmd_output, cmd_err = Utils.runCommand(command)
    print(cmd_output.decode("utf-8"))
    print(cmd_err.decode("utf-8"))
