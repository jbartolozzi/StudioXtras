import hou
import os
import json
import time

from StudioXtras import Utils
reload(Utils)


def generateOutputPictureHscript():
    '''
    This helper function prints out a recrusive ifs
    hscript to automatically set the output file path parm without
    having to use python. This way the hda can be locked inside of Renderbot
    '''
    def _compareRecurse(parm_array):
        if len(parm_array):
            parm_name = parm_array.pop()
            return "ifs(strcmp(chs(chs(\"output_driver\")+\"/%s\"),\"\"), chs(chs(\"output_driver\")+\"/%s\"), %s)" % (parm_name, parm_name, _compareRecurse(parm_array))
        else:
            return "\"\""
    compare_string = _compareRecurse(Utils.ROP_OUTPUT_FILE_PARMS)
    return("`%s`" % compare_string)


def _createImageList(first_frame, last_frame, step, picture_parm):
    def getExt(input):
        return "." + input.split(".")[-1]
    output = []
    files_to_delete = []
    for frame in range(int(first_frame), int(last_frame + 1), int(step)):
        frame_file = picture_parm.evalAtFrame(frame)
        frame_file = os.path.basename(frame_file)
        output.append("file \'%s\'" % frame_file)
    return (output, files_to_delete)


def _writeFfmpegList(output_file, output_list):
    with open(output_file, 'w') as f:
        for item in output_list:
            f.write("%s\n" % item)


def _CreateFFmpegCommand(ffmpeg_executable, configfile, codec, fps, list_file, output_file):
    """
    Adapted from https://github.com/jedypod/generate-dailies/blob/master/dailies-config.yaml
    """

    config = configfile
    globals_config = config.get("globals")
    codec_config = config["output_codecs"][codec]

    # ffmpeg-10bit No longer necessary in ffmpeg > 4.1
    ffmpeg_command = ffmpeg_executable

    # if codec_config['bitdepth'] >= 10:
    #     pixel_format = "rgb48le"
    # else:
    #     pixel_format = "rgb24"

    if codec_config['name'] == 'mjpeg':
        # Set up input arguments for frame input through pipe:
        args = "{0} -y -r {1} -f concat -i {2}".format(
            ffmpeg_command, fps, list_file)
    else:
        # Set up input arguments for raw video and pipe:
        args = "{0} -hide_banner -loglevel info -y -f concat -r {1} -i {2}".format(
            ffmpeg_command, fps, list_file)

    # Add timecode so that start frame will display correctly in RV etc
    # args += " -timecode {0}".format(start_tc)

    if codec_config['codec']:
        args += " -c:v {0}".format(codec_config['codec'])

    if codec_config['profile']:
        args += " -profile:v {0}".format(codec_config['profile'])

    if codec_config['qscale']:
        args += " -qscale:v {0}".format(codec_config['qscale'])

    if codec_config['preset']:
        args += " -preset {0}".format(codec_config['preset'])

    if codec_config['keyint']:
        args += " -g {0}".format(codec_config['keyint'])

    if codec_config['bframes']:
        args += " -bf {0}".format(codec_config['bframes'])

    if codec_config['tune']:
        args += " -tune {0}".format(codec_config['tune'])

    if codec_config['crf']:
        args += " -crf {0}".format(codec_config['crf'])

    if codec_config['pix_fmt']:
        args += " -pix_fmt {0}".format(codec_config['pix_fmt'])

    if codec_config['vf']:
        args += " -vf {0}".format(codec_config['vf'])

    if codec_config['vendor']:
        args += " -vendor {0}".format(codec_config['vendor'])

    if codec_config['metadata_s']:
        args += " -metadata:s {0}".format(codec_config['metadata_s'])

    if codec_config['bitrate']:
        args += " -b:v {0}".format(codec_config['bitrate'])

    if codec_config['movie_ext']:
        output_file = os.path.splitext(output_file)[0] + "." + codec_config['movie_ext']

    # Finally add the output movie file path
    args += " -r {0} {1}".format(fps, output_file)
    return args


def getConfigList(configjson):
    codecs = ["custom"]
    codecs.extend(sorted(configjson["output_codecs"].keys()))
    output = []
    for codec in codecs:
        output.append(codec)
        output.append(codec.title())
    return output


def run():
    # Boiler plate setup
    Utils.makeTimestampEnv()
    node = hou.pwd()  # hou.node("..")

    helper = Utils.RopHelper(node.name(), debug=node.parm("debug").eval())
    helper.debug("Running in debug mode.")

    ffmpeg_executable = helper.executablePath("ffmpeg", env="STUDIO_XTRAS_FFMPEG")
    helper.debug("ffmpeg_executable: %s" % ffmpeg_executable)

    # Get the target ROP for source images
    op = helper.getTargetOutputNode(node)
    if op is None:
        return

    # Create the list of images to pass to FFMPEG
    f1 = helper.getParm(op, "f1")
    f2 = helper.getParm(op, "f2")
    f3 = helper.getParm(op, "f3")
    fps = helper.getParm(node, "fps")
    fps = max(fps / f3, 1)

    gamma = node.parm("gamma").eval()

    helper.debug("f1: %s" % f1)
    helper.debug("f2: %s" % f2)
    helper.debug("f3: %s" % f3)
    helper.debug("fps: %s" % fps)
    helper.debug("gamma: %s" % gamma)

    picture_parm = helper.getPictureParm(op)
    dirname = os.path.dirname(picture_parm.eval())
    if not os.path.exists(dirname):
        helper.log("Making directory %s." % dirname)
        os.makedirs(dirname)

    # Create image list
    list_file = os.path.join(os.path.dirname(picture_parm.eval()), "ffmpeg_list.txt")
    helper.debug("list_file: %s" % list_file)

    if node.parm("ocio_convert").eval():
        # The COP output is the converted JPG we use for the video
        cop_output = hou.node("./convert/output")
        output_image_parm = cop_output.parm("copoutput")

        # Create the ffmpeg imagelist, and list of temp files to delete
        image_list, files_to_delete = _createImageList(
            f1, f2, f3, output_image_parm)

        # Render out the temp converted images
        cop_output.render()

    else:
        image_list, files_to_delete = _createImageList(
            f1, f2, f3, picture_parm)

    # Write the ffmpeg imagelist
    _writeFfmpegList(list_file, image_list)

    print("ALF_PROGRESS 75.0%")
    # Prepare directory for output file
    output_file = node.parm("vm_picture").eval()
    output_directory = os.path.dirname(output_file)

    output_file = output_file.replace(" ", "\\ ")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    configjson = json.loads(hou.pwd().type().definition().sections()
                            ['dailies-config.json'].contents())
    config_list = getConfigList(configjson)
    preset = config_list[hou.pwd().parm("ffmpeg_preset").eval() * 2]

    if preset != "custom":
        ffmpeg_command = _CreateFFmpegCommand(
            ffmpeg_executable,
            configjson,
            preset,
            fps,
            list_file,
            output_file)

    else:
        # Run ffmpeg
        ffmpeg_command = "\"%s\" -hide_banner -y -r %s -gamma %s -f concat -i \"%s\" -r %s %s \"%s\"" % \
            (ffmpeg_executable,
                fps,
                gamma,
                list_file,
                fps,
                node.parm("advanced_parameters").evalAsString(),
                output_file)

    cmd_output, cmd_err = Utils.runCommand(ffmpeg_command)
    helper.debug(ffmpeg_command)
    helper.debug("%s\n%s" % (cmd_output, cmd_err))

    files_to_delete.append(list_file)
    for del_file in files_to_delete:
        if os.path.exists(del_file):
            try:
                os.remove(del_file)
                time.sleep(0.1)  # to avoid clogging resource error
            except Exception as e:
                helper.warning("Unable to delete auto converted file.", details=str(e))

    to_check = ['error', 'unable']
    if cmd_err != "" and any(list((match in cmd_err.lower() for match in to_check))):
        helper.error("Unable to run FFmpeg", details=cmd_err)
