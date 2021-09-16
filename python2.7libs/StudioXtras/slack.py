import hou
import json

from StudioXtras import utils
reload(utils)


def _processPost(cmd_output, cmd_err, helper):
    out_dict = json.loads(cmd_output)
    if "ok" in out_dict and not out_dict["ok"]:
        helper.error(out_dict["error"])


def _slackText(curl, api_key, channel, text, helper):
    command = "\"%s\" -F \"text=%s\" -F \"channel=%s\" -H \"Authorization:Bearer %s\" \"https://slack.com/api/chat.postMessage\"" % (
        curl, text, channel, api_key)
    (cmd_output, cmd_err) = utils.runCommand(command)
    _processPost(cmd_output, cmd_err, helper)


def _slackMedia(curl, api_key, channel, text, file, helper):
    command = "\"%s\" -F \"file=@%s\" -F \"initial_comment=%s\" -F \"channels=%s\" -H \"Authorization: Bearer %s\" \"https://slack.com/api/files.upload\"" % (
        curl, file, text, channel, api_key)
    (cmd_output, cmd_err) = utils.runCommand(command)
    _processPost(cmd_output, cmd_err, helper)


def run():
    utils.makeTimestampEnv()
    node = hou.pwd()  # hou.node("..")
    helper = utils.RopHelper(node.name())

    # Get node params
    api_key = helper.getParm(node, "api_token")
    channel = helper.getParm(node, "channel")
    message = helper.getParm(node, "message")
    send_media = helper.getParm(node, "attach_media")

    curl_executable = helper.executablePath("curl")

    if send_media:
        # Get the target ROP for source images
        op = helper.getTargetOutputNode(node)
        if op is None:
            return
        file = helper.getPictureParm(op).eval().replace(" ", "\\ ")
        _slackMedia(curl_executable, api_key, channel, message, file, helper)
    else:
        _slackText(curl_executable, api_key, channel, message, helper)
