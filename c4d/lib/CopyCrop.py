import c4d
import getpass
import json
import os
import random
import string
import subprocess
import sys
import tempfile
from distutils.spawn import find_executable

import c4d, os, sys

C4D_RENDERER = 110304
ARNOLD_RENDERER = 1029988
ARNOLD_RENDERER_COMMAND = 1039333
C4DAIP_OPTIONS_OPERATOR = 931647947
IRR_COMMAND = 430000021
ARNOLD_DRIVER = 1030141
ARNOLD_RENDER_OVERRIDES = 1038579

driver = c4d.BaseObject(ARNOLD_DRIVER)

  
def GetActiveOperatorNetwork(renderSettings):
    if renderSettings is None:
        return None
     
    return renderSettings[C4DAIP_OPTIONS_OPERATOR]
def SetActiveOperatorNetwork(renderSettings, opnetwork):
    if renderSettings is None:
        return None
     
    renderSettings[C4DAIP_OPTIONS_OPERATOR] = opnetwork
def CreateArnoldRenderSettings():
    c4d.CallCommand(ARNOLD_RENDERER_COMMAND)
 
def GetArnoldRenderSettings(rdata):
  
    # find the active Arnold render settings
    videopost = rdata.GetFirstVideoPost()
    while videopost:
        if videopost.GetType() == ARNOLD_RENDERER:
            return videopost;
        videopost = videopost.GetNext()
      
    # create a new one when does not exist
    if videopost is None:
        CreateArnoldRenderSettings()
         
        videopost = rdata.GetFirstVideoPost()
        while videopost:
            if videopost.GetType() == ARNOLD_RENDERER:
                return videopost;
            videopost = videopost.GetNext()
                      
    return None

def GetC4dSettings(doc):
    rdata = doc.GetActiveRenderData()
    # find the active Arnold render settings
    videopost = rdata.GetFirstVideoPost()
    while videopost:
        if videopost.GetType() == c4d.RDATA_RENDERENGINE_STANDARD:
            return videopost;
        videopost = videopost.GetNext()

def main(doc):
    print("[Studio Xtras] Copy Arnold Crop")
    # c4d.CallCommand(ARNOLD_RENDERER_COMMAND)
    # c4dRenderSettings = GetC4dSettings(doc)
    # if c4dRenderSettings is None:
    #     raise BaseException("Failed to find c4dRenderSettings render settings")

    # find the Arnold video post data    
    rdata = doc.GetActiveRenderData()
    arnoldRenderSettings = GetArnoldRenderSettings(rdata)
    if arnoldRenderSettings is None:
        raise BaseException("Failed to find Arnold render settings")
    
    # rdata[c4d.RDATA_RENDERREGION] = 1
    # c4d.CallButton(rdata, c4d.RDATA_FROMIRR)
    # c4d.EventAdd()
    yres = rdata[c4d.RDATA_YRES_VIRTUAL]
    xres = rdata[c4d.RDATA_XRES_VIRTUAL]

    xmin = rdata[c4d.RDATA_RENDERREGION_LEFT]
    ymin = rdata[c4d.RDATA_RENDERREGION_TOP]
    xmax = xres - rdata[c4d.RDATA_RENDERREGION_RIGHT] - 1
    ymax = yres - rdata[c4d.RDATA_RENDERREGION_BOTTOM] - 1
    # rdata[c4d.RDATA_RENDERREGION] = 0

    # if c4d.IsCommandChecked(IRR_COMMAND) :
    #     c4d.CallCommand(IRR_COMMAND)

    # C4DTOA_RENDEROVERRIDE_REGION_X1

    # C4DTOA_RENDEROVERRIDE_XRES                   = 1004, // [Int32] Resolution width.
    # C4DTOA_RENDEROVERRIDE_YRES                   = 1005, // [Int32] Resolution height.
    # C4DTOA_RENDEROVERRIDE_USE_REGION             = 1006, // [Bool] If true then a region is rendered.
    # C4DTOA_RENDEROVERRIDE_REGION_X1              = 1007, // [Int32] Left border of the render region.
    # C4DTOA_RENDEROVERRIDE_REGION_X2              = 1008, // [Int32] Right border of the render region.
    # C4DTOA_RENDEROVERRIDE_REGION_Y1              = 1009, // [Int32] Top border of the render region.
    # C4DTOA_RENDEROVERRIDE_REGION_Y2              = 1010, // [Int32] Bottom border of the render region.

    # doc.GetSettingsInstance(c4d.DOCUMENTSETTINGS_DOCUMENT).GetContainer(ARNOLD_RENDER_OVERRIDES)
    
    # rdata[c4d.RDATA_RENDERENGINE] = ARNOLD_RENDERER
    user_options = "region_min_x %s region_min_y %s region_max_x %s region_max_y %s" % (xmin, ymin, xmax, ymax)
    arnoldRenderSettings[c4d.C4DAI_OPTIONS_USER_OPTIONS] = user_options
    c4d.EventAdd()


if __name__ == '__main__':
    main(doc)
