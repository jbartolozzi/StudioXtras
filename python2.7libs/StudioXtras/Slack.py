import hou
import json

from StudioXtras import Utils
reload(Utils)


def _processPost(cmd_output, cmd_err, helper):
    helper.debug("cmd_output: %s" % cmd_output)
    helper.debug("cmd_err: %s" % cmd_err)
    try:
        out_dict = json.loads(cmd_output)
    #     if "ok" in out_dict and not out_dict["ok"]:
    #         helper.error("Error running Slack API", details=out_dict["error"])
    # except:
    #     helper.error("Error running Slack API", details="%s\n%s" % (str(cmd_output), str(cmd_err)))
    except:
        pass

def _slackText(curl, api_key, channel, text, helper):
    command = "\"%s\" -F \"text=%s\" -F \"channel=%s\" -H \"Authorization:Bearer %s\" \"https://slack.com/api/chat.postMessage\"" % (
        curl, text, channel, api_key)
    helper.debug("command: %s" % command)
    (cmd_output, cmd_err) = Utils.runCommand(command)
    _processPost(cmd_output, cmd_err, helper)


def _slackMedia(curl, api_key, channel, text, file, helper):
    command = "\"%s\" -F \"file=@%s\" -F \"initial_comment=%s\" -F \"channels=%s\" -H \"Authorization: Bearer %s\" \"https://slack.com/api/files.upload\"" % (
        curl, file, text, channel, api_key)
    helper.debug("command: %s" % command)
    (cmd_output, cmd_err) = Utils.runCommand(command)
    _processPost(cmd_output, cmd_err, helper)


def run():
    Utils.makeTimestampEnv()
    node = hou.pwd()  # hou.node("..")
    helper = Utils.RopHelper(node.name(), debug=node.parm("debug").eval())

    # Get node params
    api_key = helper.getParm(node, "api_token")
    helper.debug("api_key: %s" % api_key)

    channel = helper.getParm(node, "channel")
    helper.debug("channel: %s" % channel)

    message = helper.getParm(node, "message")
    helper.debug("message: %s" % message)

    send_media = helper.getParm(node, "attach_media")
    helper.debug("send_media: %s" % send_media)

    curl_executable = helper.executablePath("curl", env="STUDIO_XTRAS_CURL")
    helper.debug("curl_executable: %s" % curl_executable)

    if send_media:
        # Get the target ROP for source images
        op = helper.getTargetOutputNode(node)
        if op is None:
            return
        file = helper.getPictureParm(op).eval().replace(" ", "\\ ")
        _slackMedia(curl_executable, api_key, channel, message, file, helper)
    else:
        _slackText(curl_executable, api_key, channel, message, helper)
