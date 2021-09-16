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
