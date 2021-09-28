import hou
import os
import threading
import time

from StudioXtras import Utils
reload(Utils)


def _createImageList(first_frame, last_frame, step, picture_parm, enable_denoise_postfix, denoise_postfix):
    def getExt(input):
        return "." + input.split(".")[-1]
    output = []
    threads = []
    files_to_delete = []
    for frame in range(int(first_frame), int(last_frame + 1), int(step)):
        frame_file = picture_parm.evalAtFrame(frame)

        if (enable_denoise_postfix):
            ext = getExt(frame_file)
            frame_file = frame_file.replace(ext, denoise_postfix + ext)

        if not frame_file.endswith(".jpg"):
            # Create a thread to run iconvert
            jpg_frame_file = frame_file.replace(getExt(frame_file), ".jpg")

            command = "iconvert -g auto %s %s" % (frame_file, jpg_frame_file)
            t = threading.Thread(target=Utils.runCommand, args=(command,))
            threads.append(t)
            time.sleep(0.1)  # to avoid clogging resource error
            t.start()

            files_to_delete.append(jpg_frame_file)
            frame_file = jpg_frame_file

        frame_file = os.path.basename(frame_file)
        output.append("file \'%s\'" % frame_file)
    for thread in threads:
        thread.join()
    return (output, files_to_delete)


def _writeFfmpegList(output_file, output_list):
    with open(output_file, 'w') as f:
        for item in output_list:
            f.write("%s\n" % item)


def run():
    # Boiler plate setup
    Utils.makeTimestampEnv()
    node = hou.pwd()  # hou.node("..")
    helper = Utils.RopHelper(node.name())
    # Find ffmpeg executable
    ffmpeg_executable = helper.executablePath("ffmpeg")
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

    picture_parm = helper.getPictureParm(op)
    dirname = os.path.dirname(picture_parm.eval())
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Create image list
    list_file = os.path.join(os.path.dirname(picture_parm.eval()), "ffmpeg_list.txt")

    # Write image list to render directory
    enable_denoise_postfix = helper.getParm(node, "enable_denoise_postfix")
    denoise_postfix = helper.getParm(node, "denoise_postfix")

    image_list, files_to_delete = _createImageList(
        f1, f2, f3, picture_parm, enable_denoise_postfix, denoise_postfix)

    _writeFfmpegList(list_file, image_list)

    # Prepare directory for output file
    output_file = node.parm("vm_picture").eval()
    output_directory = os.path.dirname(output_file)

    output_file = output_file.replace(" ", "\\ ")

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    command = "\"%s\" -y -r %s -f concat -i \"%s\" -r %s %s \"%s\"" % (ffmpeg_executable, fps,
                                                                       list_file, fps, node.parm("advanced_parameters").evalAsString(), output_file)

    cmd_output, cmd_err = Utils.runCommand(command)

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
