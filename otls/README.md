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

This ROP will send a message when run. It can upload images and videos from a target ROP as well.
We primarily use it alongside FFmpeg to review animations on Slack.
Contant your sys admin to set up a Slack application with the following permissions
```
channels:join     Join public channels in a workspace
chat:write        Send messages as @renderbot
files:write       Upload, edit, and delete files as Render Bot
incoming-webhook  Post messages to specific channels in Slack
```
In your `houdini.env` file you'll need to add your Slack API token which should look something like this
```
SLACK_API_TOKEN="xoxb-1234567890123-1234567890123-A12345678901234567890123"
```

The Slack ROP relies on [cURL](https://curl.se/download.html)
[How to install cURL on Mac/Windows/Linux](https://help.ubidots.com/en/articles/2165289-learn-how-to-install-run-curl-on-windows-macosx-linux)

## Renderbot

Renderbot is a compiled render preset tool we use across different types of files.
The main functions are submitting the following jobs via Deadline
1. Run a sim job from a selected ROP
2. Run an OpenGL playblast, compile it with FFmpeg, and send it to Slack
3. Run an Arnold job, compile it with FFmpeg, and send it to Slack

# Crowds

## Crowds LOD Character

## Crowds LOD Prop

## Crowds Layer Offset