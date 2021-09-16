# StudioXtras

StudioXtras is a collection of tools I've built for Houdini over the past few years. They fill certain holes in the Houdini workflow and also serve as examples of how to built tools in Houdini.


# Installation

## Dependencies

The following dependencies are necessary for running all of the features of StudioXtras
[FFmpeg](https://www.ffmpeg.org/) [cURL](https://curl.se/download.html) [git](https://git-scm.com/download/win)

Several Tools are designed to work with Arnold and Deadline since that's what we've been using.

## Linux

Clone or download the repository. 
Install the python libraries to Houdini by doing the following

Then edit your `/home/${USER}/houdini18.5/houdini.env` file with the following

```
STUDIO_XTRAS="/directory/of/repository/StudioXtras/otls"
HOUDINI_OTLSCAN_PATH="${STUDIO_XTRAS};&"
```

## MacOS

Clone or download the repository. 
Install the python libraries to Houdini by doing the following

Then edit your `/Users/${USER}/Library/Preferences/houdini/18.5/houdini.env` file with the following

```
STUDIO_XTRAS="/directory/of/repository/StudioXtras/otls"
HOUDINI_OTLSCAN_PATH="${STUDIO_XTRAS};&"
```

## Windows
Clone or download the repository. 
Then edit your `C:\Users\username\Documents\houdini18.5\houdini.env` file with the following
```
STUDIO_XTRAS="/directory/of/repository/StudioXtras/otls"
HOUDINI_OTLSCAN_PATH="${STUDIO_XTRAS};&"
```
