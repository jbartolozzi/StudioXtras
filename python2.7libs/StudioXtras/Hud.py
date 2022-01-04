import hou
import json
import os


def _setup():
    node = hou.pwd()
    format_dict_file_path = hou.text.expandString("${STUDIO_XTRAS_HUDFORMAT}")
    if os.path.exists(format_dict_file_path):
        format_dict = json.loads(format_dict_file_path)
    else:
        format_dict = {}
    target = hou.node(node.parm("target").eval())
    return (node, target, format_dict)


def refreshString():
    def _defaultText(node, parmname, parmtype):
        if parmtype == 0:
            return "%s: `chs(\"%s/%s\")`\n" % \
                (node.parm(parmname).name().title(), node.path(), parmname)
        # elif parmtype == 1:
        #     return "%s: `chi(\"%s/%s\")`\n" % \
        #         (node.parm(parmname).name().title(), node.path(), parmname)
        else:
            return "%s: `ftrim(ch(\"%s/%s\"))`\n" % \
                (node.parm(parmname).name().title(), node.path(), parmname)

    node = hou.pwd()
    target = hou.node(node.parm("target").eval())
    multiparm = node.parm("multiparm")
    if not target:
        node.parm("hud_text").set("")
        return
    else:
        hud_text = target.name().title() + "\n"
        print(multiparm.multiParmInstancesCount())
        for i in range(multiparm.multiParmInstancesCount() / 2):
            parm_name = node.parm("parmname%s" % str(i + 1)).eval()
            parm_type = node.parm("parmtype%s" % str(i + 1)).eval()
            hud_text += _defaultText(target, parm_name, parm_type)

        node.parm("hud_text").set(hud_text)


def refresh():
    node = hou.pwd()
    target = hou.node(node.parm("target").eval())
    multiparm = node.parm("multiparm")
    for i in range(multiparm.multiParmInstancesCount() / 2):
        multiparm.removeMultiParmInstance(0)

    if not target:
        return

    else:
        parms = list(parm for parm in target.parms() if not parm.isHidden())
        parms.sort(key=lambda x: x.name())
        for parm in parms:
            multiparm.insertMultiParmInstance(0)
            node.parm("parmname1").set(parm.name())
            parm_temp_to_int = {hou.parmTemplateType.Float: 2,
                                hou.parmTemplateType.String: 0,
                                hou.parmTemplateType.Int: 1}
            parm_type = parm.parmTemplate().type()
            if parm_type in parm_temp_to_int:
                node.parm("parmtype1").set(parm_temp_to_int[parm_type])
            else:
                node.parm("parmtype1").set(2)
        refreshString()


def refreshVellum():
    def _defaultText(node, parmname, stringp=False):
        if stringp:
            return "%s: `chs(\"%s/%s\")`\n" % \
                (node.parm(parmname).name().title(), node.path(), parmname)
        else:
            return "%s: `ftrim(ch(\"%s/%s\"))`\n" % \
                (node.parm(parmname).name().title(), node.path(), parmname)

    def _expText(node, parmname, expparm):
        exp = "`ch(\"%s/%s\")`" % (node.path(), expparm)
        return "%s: `ftrim(ch(\"%s/%s\"))`E%s\n" % (node.parm(parmname).name().title(), node.path(), parmname, exp)

    def _switchText(node, switchparm, switchcompare, parma, parmb):
        switch_text = "`ifs(ch(\"%s/%s\")==%s,\"%s\",\"%s\")`" % \
            (node.path(), switchparm, switchcompare, parma.title(), parmb.title())
        eval_text = "`ifs(ch(\"%s/%s\")==%s,ftrim(ch(\"%s/%s\")), ftrim(ch(\"%s/%s\")))`" % \
            (node.path(), switchparm, switchcompare, node.path(), parma, node.path(), parmb)
        return "%s: %s\n" % (switch_text, eval_text)

    node, target, format_dict = _setup()
    if target is None or target.type().name() != "vellumconstraints":
        node.parm("hud_text").set("")
        return

    hud_text = target.name().title() + "\n"

    for parmname in ["constrainttype", "stretchtype", ]:
        hud_text += _defaultText(target, parmname, stringp=True)

    hud_text += _switchText(target, "domass", 1, "mass", "density")
    hud_text += _switchText(target, "dothickness", 1, "thickness", "thicknessscale")

    for parmname in ["dragnormal", "dragtangent"]:
        hud_text += _defaultText(target, parmname)

    hud_text += _expText(target, "stretchstiffness", "stretchstiffnessexp")
    for parmname in ["stretchdampingratio", "stretchrestscale"]:
        hud_text += _defaultText(target, parmname)

    hud_text += _expText(target, "bendstiffness", "bendstiffnessexp")
    for parmname in ["benddampingratio", "bendrestscale"]:
        hud_text += _defaultText(target, parmname)

    node.parm("hud_text").set(hud_text)
