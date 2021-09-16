import hou
import datetime


def run():
    node = hou.pwd()
    if node.parm("use_hip_save").eval():
        hou.putenv(node.parm("var_name").eval(), hou.expandString(
            "$_HIP_SAVETIME").strip().replace(" ", "-"))
    else:
        hou.putenv(node.parm("var_name").eval(),
                   datetime.datetime.now().strftime(node.parm("formatting").eval()))

    print("Timsestamp set \"%s\" to " % node.parm(
        "var_name").eval() + hou.getenv(node.parm("var_name").eval()))
