# /usr/bin/env python
import os
import sys
import subprocess
import glob
import yaml
from pprint import pprint

from fps import parse_fps
from index_xlsx import validate_xlsx, read_index_xlsx

# time format parser
#import re
#time_re = re.compile("([0-9]{1,2}):([0-9]{2})[.]([0-9]+)")
#time_re_short = re.compile("([0-9]{1,2})[.]([0-9]+)")


def format_time(ts):
    """Format input milliseconds (int) to "h:mm:ss.mss"
    """
    ss, ms = divmod(ts, 1000)
    mm, ss = divmod(ss, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d.%03d" % (hh, mm, ss, ms)


def ffmpeg_command_ts(inputfile, outputfile, ts0, ts1):
    bitrate = "48M"
    t_start = format_time(ts0)
    t_end = format_time(ts1)
    return [
        "ffmpeg", "-i", inputfile,
        "-ss", t_start,
        "-to", t_end,
        "-c:v", "mpeg4",
        "-b:v", bitrate,
        outputfile
    ]


#def ffmpeg_command_frames(inputfile, outputfile, start_frame, frames):
#    bitrate = "48M"
#    return [
#        "ffmpeg",
#        "-i", inputfile,
#        "-vf", "select='between(n\,%i\,%i)'" % (start_frame,
#                                                start_frame + frames),
#        "-c:v", "mpeg4",
#        "-b:v", bitrate,
#        outputfile
#    ]


def glob_index_files(basepath):
    paths = []
    for path in glob.glob(os.path.join(basepath, "**", "*_indices.xlsx")):
        print("Validating index file: %s" % path)
        if not validate_xlsx(path):
            print("Cannot open: %s" % path)
            continue
        paths.append(path)
    return paths


#def parse_time(time_str):
#    m = time_re_short.match(time_str)
#    if m:
#        [sec, ms] = m.groups()
#        mm = 0
#    else:
#        m = time_re.match(time_str)
#        if not m:
#            raise Exception("WARN: invalid time format: %s" % time_str)
#        [mm, sec, ms] = m.groups()
#    ts = 1000 * (60 * int(mm) + int(sec)) + int(ms)
#    return ts


#def listfile_parse_line(line):
#    """Parse Synclist (cvs).
#
#       Returns:
#    """
#    if len(line) < 6:
#        raise Exception("WARN: invalid number of row columns")
#
#    [athlete_id, throw_id, cam_id, video_file_name, sync_def, duration] = line
#    input_file = "%s%s_%s.MP4" % (athlete_id, throw_id, cam_id)
#    basename = os.path.basename(input_file).split(os.path.extsep)[0]
#    output_file = "%s-sync.MP4" % basename
#
#    if sync_def.isdigit():
#        sync_def = ("frame", int(sync_def))
#    else:
#        sync_def = ("ts", parse_time(sync_def))
#
#    if not duration.isdigit():
#        raise Exception("WARN: invalid duration format: %s" % duration)
#    dt = 1000 * int(duration)
#
#    return [input_file, output_file, sync_def, dt]


def read_conf(path="."):
    fn = os.path.join(path, "ffmpeg-sync.yml")
    with open(fn) as fd:
        if os.path.isfile(fn):
            return yaml.load(fd, Loader=yaml.Loader)


def input_boolean_prompt(prompt_str):
    while True:
        answer = input(prompt_str + " ").lower()
        if answer == 'y':
            return True
        elif answer in ['n', '']:
            return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("  Input directory (containing Synclist.csv) missing!")
        sys.exit(1)

    conf = read_conf()
    if conf:
        print("Using config:")
        pprint(conf)

    base_dir = sys.argv[1]
    index_file_paths = glob_index_files(base_dir)

    cmds = []

    for indexfile_path in index_file_paths:
        data, headers = read_index_xlsx(indexfile_path)
        pprint(data)
        for [trial_id, camera_id, frame] in data:
            path_parts = indexfile_path.split(os.path.sep)[:-1]
            subject_dir = path_parts[-1]
            base_dir = os.path.sep.join(path_parts)
            fn_template = "%s_%s_%s" % (subject_dir, trial_id, camera_id)
            input_path = os.path.join(base_dir, "%s.mp4" % (fn_template))
            output_path = os.path.join("output", "%s-sync.mp4" % (fn_template))
            if os.path.isfile(input_path):
                capture_fps = int(
                    conf["cameras"][camera_id]["fps"]) if conf else 240
                playback_fps = parse_fps(input_path)

                print("Procesing '%s' (capture_fps=%i, playback_fps=%.2f)" %
                      (input_path, capture_fps, playback_fps))
                ts = 1000 * frame / playback_fps
                tot_frames = (1000 * 2 * capture_fps) / playback_fps
                cmd = ffmpeg_command_ts(input_path,
                                        output_path,
                                        ts,
                                        ts + tot_frames)

                cmds.append(cmd)

    if len(cmds) == 0:
        sys.exit(0)

    print("Commands:")
    for cmd in cmds:
        print("  " + " ".join(cmd))
    print()

    if not input_boolean_prompt("Execute commands (y/N)?"):
        sys.exit(0)

    print("\nStart executing commands...\n")
    for cmd in cmds:
        print(" ".join(cmd))
        p = subprocess.run(cmd, shell=True)
        if p.returncode != 0:
            print("ERROR in ffmpeg processing")
