import hou


def copyRenderRegionToArnold():
    desktop = hou.ui.curDesktop()
    ipr = desktop.paneTabOfType(hou.paneTabType.IPRViewer)

    rop = ipr.ropNode()

    if rop is not None and rop.type().name() == "arnold":
        xmin, xmax, ymin, ymax = ipr.cropRegion()
        camera = hou.node(rop.parm("camera").eval())
        if camera is not None:
            xres = camera.parm("resx").eval()
            yres = camera.parm("resy").eval()

            xmin = int(xmin * xres)
            xmax = int(xmax * xres)
            ymin = int(ymin * yres)
            ymax = int(ymax * yres)

            if (xmin == 0 and xmax == xres and ymin == 0 and ymax == yres):
                # Clear out the crop window
                rop.parm("ar_user_options_enable").set(False)
                rop.parm("ar_user_options").set("")
            else:
                # Set the crop window area on the Arnold ROP
                rop.parm("ar_user_options_enable").set(True)
                # Swap the ymax/ymin because the IPR viewer space is flipped
                rop.parm("ar_user_options").set(
                    "region_min_x %s region_min_y %s region_max_x %s region_max_y %s" %
                    (xmin, yres - ymax - 1, xmax, yres - ymin - 1))
        else:
            hou.ui.displayMessage("ROP has no selected camera. Required to determine resolution.")

    else:
        hou.ui.displayMessage("Select an Arnold ROP in the IPR Viewer")


def exportToPy():
    python_file = hou.ui.selectFile(start_directory=hou.expandString("$HIP"),
                                    title="Export Selection to Python",
                                    collapse_sequences=False,
                                    file_type=hou.fileType.Any,
                                    pattern="*.py",
                                    default_value=None,
                                    multiple_select=False,
                                    image_chooser=None,
                                    chooser_mode=hou.fileChooserMode.Write,
                                    width=0, height=0)
    if python_file is None:
        return
    if not python_file.endswith(".py"):
        python_file = python_file + ".py"

    outputs = []
    for node in hou.selectedNodes():
        outputs.append(node.asCode(brief=False,
                                   recurse=True,
                                   save_channels_only=False,
                                   save_creation_commands=True,
                                   save_keys_in_frames=True,
                                   save_outgoing_wires=True,
                                   save_parm_values_only=False,
                                   save_spare_parms=True,
                                   function_name=None))

    with open(hou.expandString(python_file), 'w') as outfile:
        processed_lines = []
        for output in outputs:
            lines = iter(output.split("\n"))
            line = next(lines, None)
            while line is not None:
                if line.startswith("if"):
                    block = []
                    block.append(line)
                    line = next(lines, None)
                    while line.startswith(" "):
                        block.append(line)
                        line = next(lines, None)

                    processed_lines.append("try:")
                    for block_line in block:
                        processed_lines.append("    " + block_line)
                    processed_lines.append("except Exception as e:")
                    processed_lines.append("    print(str(e))")

                elif not line.startswith(" ") and \
                        not line.startswith("#") and \
                        line.strip() != "" and \
                        not line.startswith("if"):
                    processed_lines.append("try:")
                    processed_lines.append("    " + line.strip())
                    processed_lines.append("except Exception as e:")
                    processed_lines.append("    print(str(e))")
                    line = next(lines, None)
                else:
                    if line.startswith("hou"):
                        raise
                    processed_lines.append(line)
                    line = next(lines, None)

        outfile.write("\n".join(processed_lines))


def importFromPy():
    import os
    python_file = hou.ui.selectFile(start_directory=hou.expandString("$HIP"),
                                    title="Export Selection to JSON",
                                    collapse_sequences=False,
                                    file_type=hou.fileType.Any,
                                    pattern="*.py",
                                    default_value=None,
                                    multiple_select=False,
                                    image_chooser=None,
                                    chooser_mode=hou.fileChooserMode.Write,
                                    width=0, height=0)

    if python_file is not None and os.path.exists(python_file):
        with open(hou.expandString(python_file)) as infile:
            exec(infile.read())


def checkFilePaths():
    import json
    import os
    pathmap_file_path = hou.text.expandString("${PATH_MAP_DICT}")
    if not os.path.exists(pathmap_file_path):
        hou.ui.displayMessage("Pathmap file not found.",
                              title="StudioXtras Error",
                              details="In your houdini.env file specify PATH_MAP_DICT to point to a json file.",
                              severity=hou.severityType.Error)

        return

    correction_dict = {}
    with open(pathmap_file_path, 'r') as infile:
        correction_dict = json.load(infile)

    root_node = hou.node("/")
    failed = []
    for parm in root_node.allParms():
        parm_template = parm.parmTemplate()
        if parm_template.type() == hou.parmTemplateType.String and \
                parm_template.stringType() == hou.stringParmType.FileReference:

            try:
                unexpanded = parm.unexpandedString()
                for correction in correction_dict.keys():
                    if correction in unexpanded:
                        parm.set(unexpanded.replace(correction, correction_dict[correction]))
            except:
                failed.append("%s : %s" % (parm.node().path(), parm.name()))

    # if "ui" in dir(hou):
    #     hou.ui.displayMessage("Following parameters could not be processed",
    #                           title="StudioXtras Error",
    #                           details="\n".join(failed),
    #                           severity=hou.severityType.Warning)
