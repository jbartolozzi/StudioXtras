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

ISPYTHONTHREE = str(sys.version).startswith("3")
USER = getpass.getuser()
APIKEY = os.getenv("SLACK_API_KEY")
CURL = find_executable("curl")
CHANNEL = os.getenv("SLACK_RENDER_CHANNEL")


def runCommand(command):
    if ISPYTHONTHREE:
        process = subprocess.Popen(command,
                                   text=True,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(command,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

    cmd_output, error = process.communicate()
    try:
        result_data = json.loads(cmd_output)
        if not result_data['ok']:
            c4d.gui.MessageDialog(
                "Slack posting failed with the following error:\n%s." % result_data)
    except:
        pass


def slackTextMessage(curl, api_key, channel, text):
    command = "%s -F \"text=%s\" -F channel=%s -H \"Authorization: Bearer %s\" https://slack.com/api/chat.postMessage" % (
        curl, text, channel, api_key)
    runCommand(command)


def slackMediaMessage(curl, api_key, channel, text, file):
    command = "%s -F \"file=@%s\" -F \"initial_comment=%s\" -F \"channels=%s\" -H \"Authorization: Bearer %s\" \"https://slack.com/api/files.upload\"" % (
        curl, file, text, channel, api_key)
    runCommand(command)


def isRendering(file_path):
    while c4d.CheckIsRunning(c4d.CHECKISRUNNING_EXTERNALRENDERING):
        pass
    if not os.path.exists(file_path):
        c4d.gui.MessageDialog("Output image %s not found." % file_path)
    else:
        slackMediaMessage(CURL, APIKEY, CHANNEL, "Renderbot image from %s" % USER, file_path)


def main(doc):

    # Check for required global variables
    if APIKEY == "" or APIKEY is None:
        c4d.gui.MessageDialog(
            "Slack API key not set. Make sure to set environment variable \"SLACK_API_KEY\".")
        return

    if CURL is None:
        c4d.gui.MessageDialog("Unable to find cURL executable, make sure cURL is installed.")
        return

    backup = {}
    rdata = doc.GetActiveRenderData()

    backup[c4d.RDATA_MULTIPASS_ENABLE] = rdata[c4d.RDATA_MULTIPASS_ENABLE]
    rdata[c4d.RDATA_MULTIPASS_ENABLE] = 0

    backup[c4d.RDATA_GLOBALSAVE] = rdata[c4d.RDATA_GLOBALSAVE]
    rdata[c4d.RDATA_GLOBALSAVE] = 1

    backup[c4d.RDATA_SAVEIMAGE] = rdata[c4d.RDATA_SAVEIMAGE]
    rdata[c4d.RDATA_SAVEIMAGE] = 1

    # Create a temp file name for the image to write to
    temp_file = "".join(random.choice(string.ascii_uppercase + string.digits)
                        for _ in range(24)) + ".jpg"

    backup[c4d.RDATA_PATH] = rdata[c4d.RDATA_PATH]
    rdata[c4d.RDATA_PATH] = os.path.join(tempfile.gettempdir(), temp_file)

    backup[c4d.RDATA_FORMAT] = rdata[c4d.RDATA_FORMAT]
    rdata[c4d.RDATA_FORMAT] = 1104

    backup[c4d.RDATA_FRAMESEQUENCE] = rdata[c4d.RDATA_FRAMESEQUENCE]
    rdata[c4d.RDATA_FRAMESEQUENCE] = c4d.RDATA_FRAMESEQUENCE_CURRENTFRAME
    file_path = rdata[c4d.RDATA_PATH]

    # Render image and open listener thread.
    c4d.CallCommand(12099)
    if c4d.CheckIsRunning(c4d.CHECKISRUNNING_EXTERNALRENDERING):

        if not ISPYTHONTHREE:
            import thread
            thread.start_new(isRendering, (file_path,))
        else:
            import threading
            threading.Thread(target=isRendering,
                             args=(file_path,),
                             ).start()

    # Reset all settings
    for key in backup:
        rdata[key] = backup[key]


if __name__ == '__main__':
    main(doc)
