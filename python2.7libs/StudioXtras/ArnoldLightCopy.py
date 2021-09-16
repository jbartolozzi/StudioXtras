import hou

default_transform_mappings = {'P': 't', 'rot': 'r', 'scale': 's', 'pscale': 'scale'}


def _merge_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def loadMappings():
    hou.pwd().parm("attribute_map").set(
        {'exposure': 'ar_exposure', 'intensity': 'ar_intensity', 'Cd': 'ar_color'})


def _set_parm_from_attr(parm, attr, geometry_path, point_number, index):
    parm.setExpression("point(\"%s\",%s,\"%s\",%s)" % (geometry_path, point_number, attr, index))


def _set_light_params(attr_map, transform_node, light_node, point_number, geometry, geometry_path, point):
    missing_attrs = []
    missing_params = []

    # Go through the mapping
    for attr in attr_map:
        # Check if the geometry attribute exists
        found_attr = geometry.findPointAttrib(attr)
        if found_attr:
            # Check if its a transform mapping
            if attr in default_transform_mappings.keys():
                parm_tuple = transform_node.parmTuple(attr_map[attr])
            # Else its a light attrib mapping
            else:
                parm_tuple = light_node.parmTuple(attr_map[attr])
            if parm_tuple is not None:
                size = found_attr.size()
                values = point.attribValue(attr)
                # Handle the array type
                if isinstance(values, tuple):
                    for idx, value in enumerate(values):
                        _set_parm_from_attr(parm_tuple[idx], attr, geometry_path, point_number, idx)
                # Handle the singleton type
                else:
                    _set_parm_from_attr(parm_tuple[0], attr, geometry_path, point_number, 0)
            else:
                missing_params.append(attr_map[attr])
        else:
            missing_attrs.append(attr)


def run():
    node = hou.pwd()
    light = hou.node(node.parm("light").eval())
    template = hou.node(node.parm("template").eval())

    root = node.children()[0]

    if light is not None and template is not None:
        # Delete existing children
        with hou.InterruptableOperation("Deleting old rig."):
            for child in root.children():
                child.destroy()

        # Get the instance geometry
        if isinstance(template, hou.ObjNode):
            for child in template.children():
                if child.isRenderFlagSet():
                    vis_node = child
                    template.setDisplayFlag(0)
                    break
        else:
            vis_node = template
            template.parent().setDisplayFlag(0)

        geometry = hou.node(vis_node.parent().path() + "/Arnold_Light_Rig_Export")
        if geometry is None:
            geometry = vis_node.parent().createNode("null", "Arnold_Light_Rig_Export")
        geometry.setInput(0, vis_node)
        vis_node.parent().layoutChildren(items=(geometry,))
        geometry_path = geometry.path()
        geometry = geometry.geometry()

        interrupt = hou.InterruptableOperation(
            "", long_operation_name="Building Arnold light rig.", open_interrupt_dialog=(len(geometry.points()) > 25))
        total = float(len(geometry.points()))

        attr_map = hou.pwd().parm("attribute_map").eval()
        if node.parm("enable_transform_map").eval():
            attr_map = _merge_dicts(attr_map, default_transform_mappings)
        with interrupt:
            for idx, point in enumerate(geometry.points()):

                new_node = root.createNode("null", "point%s" % idx)
                new_node.setInput(0, hou.item(root.path() + "/1"))
                new_node.setDisplayFlag(False)

                copy_light = node.parent().copyItems(
                    (light,), channel_reference_originals=True, relative_references=False)[0]
                new_light = copy_light.copyTo(root)
                copy_light.destroy()
                new_light.setInput(0, new_node)
                new_light.setDisplayFlag(True)
                new_light.parm("light_enable").setExpression("ch(\"%s/enable\")" % node.path())
                interrupt.updateLongProgress(percentage=float(
                    idx) / total, long_op_status="Creating light %s." % idx)

                _set_light_params(attr_map, new_node, new_light, idx,
                                  geometry, geometry_path, point)

    root.layoutChildren()
