import hou
import sys
import subprocess
from distutils.spawn import find_executable

class NodeHelper:
    def __init__(self, node_name):
        self.node_name = node_name

    def error(self, text):
        err_text = "ERROR! StudioXtras:%s:\n%s" % (self.node_name, str(text))
        sys.stderr.write(err_text + "\n")
        if "ui" in dir(hou):    
            raise hou.NodeError(err_text)

    def log(self, text):
        print("StudioXtras:%s: %s" % (self.node_name, text))

    def getParm(self, node, parm_name):
        try:
            return node.parm(parm_name).eval()
        except:
            self.error("Unable to get parm %s for node %s." % (parm_name, node.name()))
            return None

    def executablePath(self, executable_name):
        executable_path = find_executable(executable_name)
        if executable_path is None:
            self.error("%s is not installed. Please install %s and update your PATH environment variable." % (executable_name, executable_name)) 
        return executable_path

class RopHelper(NodeHelper):
    def getTargetOutputNode(self, node):
        ignore_dependancy = node.parm("ignore_dependancy")
        if len(node.inputs()) > 0 and \
                not (ignore_dependancy is not None \
                and not ignore_dependancy.isDisabled() \
                and ignore_dependancy.eval()):
            op = node.inputs()[0]
        else:
            op = hou.node(self.getParm(node, "output_driver"))

        # Check if op is a fetch, resolve the fetch path as new op
        if op is not None and op.type().name() == "fetch":
            op = hou.node(op.parm("source").eval())

        if op is None:
            self.error("Output ROP does not exist.")

        return op

    def getPictureParm(self, node):
        parm_names = ["ar_picture", "picture", "vm_picture", "ri_display_0", "copoutput", "HO_img_fileName"]
        for parm_name in parm_names:
            if node.parm(parm_name) is not None:
                return node.parm(parm_name)
        
        if picture_parm is None:
            self.error("Unable to find picture or vm_picture parm from render target.")
        return picture_parm

def runCommand(command, disable_env=False):
    if disable_env:
        process = subprocess.Popen(command, env={}, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    cmd_output, cmd_err = process.communicate()

    return (cmd_output, cmd_err)

def makeTimestampEnv():
    hou.putenv("TIMESTAMP", hou.expandString("$_HIP_SAVETIME").strip().replace(" ", "_").replace(":", "_"))