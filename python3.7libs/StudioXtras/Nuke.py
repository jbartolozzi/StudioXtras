import hou
from StudioXtras import Utils
reload(Utils)


def run():
    Utils.makeTimestampEnv()
    node = hou.pwd()
    helper = Utils.RopHelper(node.name())
    op = helper.getTargetOutputNode(node)
    if op is None:
        return

    nuke_executable = helper.executablePath("nuke", env="STUDIO_XTRAS_NUKE")
    helper.debug("nuke_executable: %s" % nuke_executable)

    first_frame = int(helper.getParm(op, "f1"))
    last_frame = int(helper.getParm(op, "f2"))
    picture_parm = helper.getPictureParm(op)

    nuke_preset = node.parm("nuke_presets").eval()
    if nuke_preset == "tviscale":
        nuke_script = "tviscale.nk"
    elif nuke_preset == "denoise":
        nuke_script = "denoise.nk"
    else:
        nuke_script = node.parm("custom_nuke_script").eval()

    file_read_env = "STUDIO_XTRAS_NUKE_INPUT=%s" % picture_parm.rawValue()
    file_write_env = "STUDIO_XTRAS_NUKE_OUTPUT=%s" % node.parm("output_file").rawValue()

    command = "{file_read_env} {file_write_env} {nuke_executable} -F {first_frame}-{last_frame} -x {nuke_script}".format(
        **locals())

    print(command)
    # Utils.runCommand(command, background=True)
