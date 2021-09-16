# StudioXtras

StudioXtras is a collection of tools I've built for Houdini over the past few years. They fill certain holes in the Houdini workflow and also serve as examples of how to built tools in Houdini.

[Docs for Node Operators](https://github.com/jbartolozzi/StudioXtras/tree/main/otls)\
[Docs for Shelf Tools](https://github.com/jbartolozzi/StudioXtras/tree/main/toolbar)


# Installation

The following dependencies are necessary for running all of the features of StudioXtras
[FFmpeg](https://www.ffmpeg.org/) [cURL](https://curl.se/download.html) [git](https://git-scm.com/download/win)

Several Tools are designed to work with Arnold and Deadline since that's what we've been using.

Add the following lines to your houdini.env file. 
```
STUDIO_XTRAS="/path/to/StudioXtras/"
HOUDINI_PATH="${STUDIO_XTRAS};${ARNOLD};${DEADLINE};${OCTANE};${REDSHIFT};&"
```
The other plugins are just examples of how you can load multiple in one line call.\
**Note** You can set `HOUDINI_PATH` this way even if you dont set the other variables. 
You can always easily load/unload plugins by commenting out the `PLUGIN_NAME="/path/to/plugin/dir` 
variable rather than trying to manage a long `HOUDINI_PATH` line.

[See Houdini documentation on environment variables](https://www.sidefx.com/docs/houdini/basics/config_env.html)
1. Linux   `/home/${USER}/houdini18.5/houdini.env`
2. MacOS   `/Users/${USER}/Library/Preferences/houdini/18.5/houdini.env`
3. Windows `C:\Users\username\Documents\houdini18.5\houdini.env`

