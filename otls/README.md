# OTLS

Here are the docs for StudioXtras node operators

# ROPs

## FFmpeg

This ROP will take an input render ROP and automatically compile the output images into an mp4.
For most cases the advanced settings will not need to be used.
This ROP's primary purpose is to provide playable movie files, not final quality video.

FFmpeg must be installed and available in the PATH for this node to function correctly.
[FFmpeg](https://www.ffmpeg.org/)
[Installing FFmpeg on Windows](https://www.wikihow.com/Install-FFmpeg-on-Windows)
[Installing FFmpeg on MacOS using brew](http://jollejolles.com/install-ffmpeg-on-mac-os-x/)
[Installing FFmpeg on Linux](https://linuxize.com/post/how-to-install-ffmpeg-on-debian-9/)


## Slack

[cURL](https://curl.se/download.html)

Clone or download the repository. 
Install the python libraries to Houdini by doing the following

Then edit your `/home/${USER}/houdini18.5/houdini.env` file with the following

```
STUDIO_XTRAS="/directory/of/repository/StudioXtras/otls"
HOUDINI_OTLSCAN_PATH="${STUDIO_XTRAS};&"
```

## Renderbot

Clone or download the repository. 
Install the python libraries to Houdini by doing the following

Then edit your `/Users/${USER}/Library/Preferences/houdini/18.5/houdini.env` file with the following

```
STUDIO_XTRAS="/directory/of/repository/StudioXtras/otls"
HOUDINI_OTLSCAN_PATH="${STUDIO_XTRAS};&"
```