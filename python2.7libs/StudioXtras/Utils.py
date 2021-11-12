import hou
import os
import subprocess
from distutils.spawn import find_executable


class NodeHelper:
    def __init__(self, node_name, debug=False):
        self.node_name = node_name
        self.debug_mode = debug

    def error(self, text, details=""):
        err_text = "StudioXtras Error: %s\n    %s" % (self.node_name, str(text))
        print(err_text)
        if "ui" in dir(hou):
            hou.ui.displayMessage(text, title="StudioXtras Error",
                                  details=details, severity=hou.severityType.Error)
        else:
            raise hou.NodeError(text + " " + details)

    def warning(self, text, details=""):
        print("StudioXtras Warning: %s\n    %s" % (self.node_name, text))
        if "ui" in dir(hou):
            hou.ui.displayMessage(text, title="StudioXtras Warning",
                                  details=details, severity=hou.severityType.Warning)
        else:
            raise hou.NodeWarning(text + " " + details)

    def debug(self, text):
        if self.debug_mode:
            print("%s Debug: %s" % (self.node_name, text))

    def log(self, text):
        print("StudioXtras: %s\n    %s" % (self.node_name, text))

    def getParm(self, node, parm_name):
        try:
            return node.parm(parm_name).eval()
        except:
            self.error("Unable to get parm %s for node %s." % (parm_name, node.name()))
            return None

    def executablePath(self, executable_name, env=None):
        if env is not None and env in os.environ:
            executable_path = os.environ[env]
        else:
            executable_path = find_executable(executable_name)

        if not os.path.exists(executable_path):
            self.error("%s is not installed." % executable_name,
                       details="Please install %s and update your PATH environment variable. Refer to documentation for setting app specfic path variables." % executable_name)
        return executable_path


class RopHelper(NodeHelper):
    def getTargetOutputNode(self, node):
        ignore_dependancy = node.parm("ignore_dependancy")
        using_input_op = False
        output_driver_parm_text = self.getParm(node, "output_driver")
        if len(node.inputs()) > 0 and \
                not (ignore_dependancy is not None
                     and not ignore_dependancy.isDisabled()
                     and ignore_dependancy.eval()):
            op = node.inputs()[0]
            using_input_op = True
        else:
            op = hou.node(output_driver_parm_text)

        # Check if op is a fetch, resolve the fetch path as new op
        if op is not None and op.type().name() == "fetch":
            op = hou.node(op.parm("source").eval())

        if op is None and using_input_op:
            self.error("No output driver specified. Please connect input or select ROP from parameter.")
        elif op is None and not using_input_op:
            self.error(
                "Provided ROP path invalid or does not exist. Please set output driver or connect input.")

        return op

    def getPictureParm(self, node):
        parm_names = ["ar_picture",
                      "picture",
                      "vm_picture",
                      "ri_display_0",
                      "copoutput",
                      "HO_img_fileName",
                      "output"]
        for parm_name in parm_names:
            if node.parm(parm_name) is not None:
                return node.parm(parm_name)

        self.error("Unable to find picture or vm_picture parm from render target.")
        return None

    def getImageList(self, first_frame, last_frame, step, picture_parm, check_if_exists=False):
        output = list(picture_parm.evalAtFrame(frame)
                      for frame in range(int(first_frame), int(last_frame + 1), int(step)))
        if check_if_exists:
            return list(file for file in output if os.path.exists(file))
        else:
            return output


def runCommand(command, disable_env=False, background=False):
    if background:
        if disable_env:
            process = subprocess.Popen(command, env={}, shell=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        if disable_env:
            process = subprocess.Popen(command, env={}, shell=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        cmd_output, cmd_err = process.communicate()
        return (cmd_output, cmd_err)


def makeTimestampEnv():
    hou.putenv("TIMESTAMP", hou.expandString(
        "$_HIP_SAVETIME").strip().replace(" ", "_").replace(":", "_"))
