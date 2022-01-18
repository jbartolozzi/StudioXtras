import hou
hou.setFrame(hou.playbar.frameRange()[0])


def callback(event_type):
    try:
        from StudioXtras import Utils
        from importlib import reload
        reload(Utils)
        if event_type == hou.hipFileEventType.BeforeSave:
            Utils.checkFilePaths()
    except Exception as e:
        print(str(e))


hou.hipFile.addEventCallback(callback)
