import hou
import json
import os
import signal
from importlib import reload
from StudioXtras import Utils
import subprocess
reload(Utils)


def run():
    node = hou.pwd()
    helper = Utils.RopHelper(node.name(), debug=node.parm("debug").eval())
    if node.parm("save_on_exec").eval():
        helper.log(f"Saving {hou.hipFile.path()}")

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
    command = f"{houdinifx} -foreground {hou.hipFile.path()}"

    helper.log(f"Running command {command}")

    with subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        pid = p.pid
        helper.log(f"Starting process with pid: {pid}")
        for line in p.stdout:
            print(line, end='')
            if "error" in line.lower():
                print(f"Found error in Gooey job.")
                p.kill()
            if "ALF_PROGRESS 100%" in line:
                p.kill()
