import c4d
import os
import sys
import importlib
sys.path.append(os.path.dirname(__file__))
from lib import CheckPaths
from lib import Renderbot
from lib import CopyCrop


def loadBitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp

class CheckPathsCommand(c4d.plugins.CommandData):

    PLUGIN_ID = 123456999
    PLUGIN_NAME = "Check Paths"
    PLUGIN_INFO = 0
    PLUGIN_ICON = loadBitmap("checkpaths.tiff")
    PLUGIN_HELP = "Run StudioXtras Plugins"

    def Register(self):
        return c4d.plugins.RegisterCommandPlugin(
            self.PLUGIN_ID, self.PLUGIN_NAME, self.PLUGIN_INFO, self.PLUGIN_ICON, self.PLUGIN_HELP, self)

    def Execute(self, doc):
        importlib.reload(CheckPaths)
        CheckPaths.main(doc)
        return True

class RenderbotCommand(c4d.plugins.CommandData):

    PLUGIN_ID = 123456799
    PLUGIN_NAME = "Renderbot"
    PLUGIN_INFO = 0
    PLUGIN_ICON = loadBitmap("renderbot.tiff")
    PLUGIN_HELP = "Run StudioXtras Plugins"

    def Register(self):
        return c4d.plugins.RegisterCommandPlugin(
            self.PLUGIN_ID, self.PLUGIN_NAME, self.PLUGIN_INFO, self.PLUGIN_ICON, self.PLUGIN_HELP, self)

    def Execute(self, doc):
        importlib.reload(Renderbot)
        Renderbot.main(doc)
        return True

class CopyCropToArnoldCommand(c4d.plugins.CommandData):

    PLUGIN_ID = 1234512299
    PLUGIN_NAME = "Copy Crop to Arnold"
    PLUGIN_INFO = 0
    PLUGIN_ICON = loadBitmap("renderbot.tiff")
    PLUGIN_HELP = "Copy crop window from Arnold IPR to output."

    def Register(self):
        return c4d.plugins.RegisterCommandPlugin(
            self.PLUGIN_ID, self.PLUGIN_NAME, self.PLUGIN_INFO, self.PLUGIN_ICON, self.PLUGIN_HELP, self)

    def Execute(self, doc):
        importlib.reload(CopyCrop)
        CopyCrop.main(doc)
        return True


if __name__ == '__main__':
    CheckPathsCommand().Register()
    RenderbotCommand().Register()
    CopyCropToArnoldCommand().Register()