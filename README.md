# StudioXtras

StudioXtras is a collection of tools I've built for Houdini over the past few years. They fill certain holes in the Houdini workflow and also serve as examples of how to built tools in Houdini.

[Docs for node operators](https://github.com/jbartolozzi/StudioXtras/tree/main/otls)
[Docs for shelf tools](https://github.com/jbartolozzi/StudioXtras/tree/main/toolbar)


# Installation

The following dependencies are necessary for running all of the features of StudioXtras
[FFmpeg](https://www.ffmpeg.org/) [cURL](https://curl.se/download.html) [git](https://git-scm.com/download/win)

Several Tools are designed to work with Arnold and Deadline since that's what we've been using.

Add the following lines to your houdini.env file.
```
STUDIO_XTRAS="/directory/of/repository/StudioXtras/"
HOUDINI_PATH="${STUDIO_XTRAS};${ARNOLD};${DEADLINE};${OCTANE};${REDSHIFT};&"
```
[See Houdini documentation on environment variables](https://www.sidefx.com/docs/houdini/basics/config_env.html)
1. Linux   `/home/${USER}/houdini18.5/houdini.env`
2. MacOS   `/Users/${USER}/Library/Preferences/houdini/18.5/houdini.env`
3. Windows `C:\Users\username\Documents\houdini18.5\houdini.env`

