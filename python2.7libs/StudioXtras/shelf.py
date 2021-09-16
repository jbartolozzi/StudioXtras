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
    json_file = hou.ui.selectFile(start_directory=hou.expandString("$HIP"),
                                  title="Export Selection to Python",
                                  collapse_sequences=False,
                                  file_type=hou.fileType.Any,
                                  pattern="*.py",
                                  default_value=None,
                                  multiple_select=False,
                                  image_chooser=None,
                                  chooser_mode=hou.fileChooserMode.Write,
                                  width=0, height=0)
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

    with open(hou.expandString(json_file), 'w') as outfile:
        for output in outputs:
            processed_lines = []
            lines = output.split("\n")
            for line in lines:
                if not line.startswith(" ") and \
                        not line.startswith("#") and \
                        line.strip() != "" and \
                        not line.startswith("if"):
                    processed_lines.append("try:")
                    processed_lines.append("    " + line.strip())
                    processed_lines.append("except Exception as e:")
                    processed_lines.append("    print(str(e))")
                else:
                    if line.startswith("hou"):
                        raise
                    processed_lines.append(line)

        outfile.write("\n".join(processed_lines))


def importFromPy():
    json_file = hou.ui.selectFile(start_directory=hou.expandString("$HIP"),
                                  title="Export Selection to JSON",
                                  collapse_sequences=False,
                                  file_type=hou.fileType.Any,
                                  pattern="*.py",
                                  default_value=None,
                                  multiple_select=False,
                                  image_chooser=None,
                                  chooser_mode=hou.fileChooserMode.Write,
                                  width=0, height=0)

    with open(hou.expandString(json_file)) as infile:
        exec(infile.read())
