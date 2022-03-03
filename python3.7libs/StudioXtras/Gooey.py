import hou
import json
import os
import platform
import signal
from importlib import reload
from StudioXtras import Utils
import subprocess
reload(Utils)


def getActiveDisplays():
    if platform.system() == "Linux":
        command = "ps e | grep -Po \" DISPLAY=[\\.0-9A-Za-z:]* \" | sort -u"
        output, error = Utils.runCommand(command)
        displays = list(line.strip() for line in output.decode(
            "utf-8").split("\n") if "display" in line.lower())
        if len(displays):
            return list(display.split("=")[1] for display in displays)

    return []


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

    env = os.environ.copy()
    displays = getActiveDisplays()
    if len(displays):
        env["DISPLAY"] = displays[0]

    houdinifx = helper.executablePath("houdinifx")
    command = f"{houdinifx} -foreground {hou.hipFile.path()}"

    helper.log(f"Running command {command}")

    with subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, bufsize=1, env=env, universal_newlines=True) as p:
        pid = p.pid
        helper.log(f"Starting process with pid: {pid}")
        for line in p.stdout:
            print(line, end='')
            if "error" in line.lower():
                print(f"Found error in Gooey job.")
                os.kill(p.pid, signal.SIGTERM)
            if "Gooey Complete" in line:
                os.kill(p.pid, signal.SIGTERM)
