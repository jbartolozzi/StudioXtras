import hou
hou.setFrame(hou.playbar.frameRange()[0])


def hipCallback(event_type):
    try:
        from StudioXtras import Utils
        from importlib import reload
        reload(Utils)
        if event_type == hou.hipFileEventType.BeforeSave:
            Utils.checkFilePaths()
            Utils.checkOpenedHDAs()
        if event_type == hou.hipFileEventType.AfterLoad:
            Utils.runGooey()
    except Exception as e:
        print(str(e))


def hdaCallback(event_type, asset_definition, **kwargs):
    try:
        from StudioXtras import Utils
        from importlib import reload
        reload(Utils)
        if event_type == hou.hdaEventType.AssetSaved:
            Utils.checkOpenedHDAs(ignore_type=asset_definition.nodeType())
    except Exception as e:
        print(str(e))


hou.hipFile.addEventCallback(hipCallback)
hou.hda.addEventCallback((hou.hdaEventType.AssetSaved, ), hdaCallback)
