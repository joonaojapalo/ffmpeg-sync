import csv
import os
import sys
import re
import subprocess

# time format parser
time_re = re.compile("([0-9]{1,2}):([0-9]{2})[.]([0-9]+)")
time_re_short = re.compile("([0-9]{1,2})[.]([0-9]+)")


def format_time(ts):
    """Format input milliseconds (int) to "h:mm:ss.mss"
    """
    ss, ms = divmod(ts, 1000)
    mm, ss = divmod(ss, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d.%03d" % (hh, mm, ss, ms)


def ffmpeg_command(inputfile, outputfile, ts0, ts1):
    bitrate = "48M"
    t_start = format_time(ts0)
    t_end = format_time(ts1)
    return [
        "ffmpeg", "-i",
        inputfile, "-ss", t_start, "-to", t_end, "-c:v", "mpeg4", "-b:v",
        bitrate, outputfile
    ]


def parse_time(time_str):
    m = time_re_short.match(time_str)
    if m:
        [sec, ms] = m.groups()
        mm = 0
    else:
        m = time_re.match(time_str)
        if not m:
            raise Exception("WARN: invalid time format: %s" % time_str)
        [mm, sec, ms] = m.groups()
    ts = 1000 * (60 * int(mm) + int(sec)) + int(ms)
    return ts


def listfile_parse_line(line):
    """Parse Synclist (cvs).

       Returns:
    """
    if len(line) < 6:
        raise Exception("WARN: invalid number of row columns")

    [athlete_id, throw_id, cam_id, video_file_name, sync_ts, duration] = line
    input_file = "%s%s_%s.MP4" % (athlete_id, throw_id, cam_id)
    basename = os.path.basename(input_file).split(os.path.extsep)[0]
    output_file = "%s-sync.MP4" % basename

    sync_ts = parse_time(sync_ts)

    if not duration.isdigit():
        raise Exception("WARN: invalid duration format: %s" % duration)
    dt = 1000 * int(duration)

    return [input_file, output_file, sync_ts, dt]


def parse_synclist(base_dir):
    ffmpef_cmds = [] 
    for line_num, line in enumerate(f):
        if line[0].startswith("#"):
            continue
        try:
            [input_file, output_file, ts, dt] = listfile_parse_line(line)
        except Exception as e:
            raise Exception("Error on line %d -- %s" % (line_num, e))

        cmd = ffmpeg_command(os.path.join(base_dir, input_file),
                            os.path.join(base_dir, output_file),
                            ts,
                            ts + dt)
        ffmpef_cmds.append(cmd)
    return ffmpef_cmds


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("  Input directory (containing Synclist.csv) missing!")
        sys.exit(1)

    base_dir = sys.argv[1]
    listfile_path = os.path.join(base_dir, "Synclist.csv")

    if not os.path.isfile(listfile_path):
        print("  Synclist.csv not found: %s" % (listfile_path))
        sys.exit(1)
    
    f = csv.reader(open(listfile_path, "r"))

    try:
        cmds = parse_synclist(base_dir)
    except Exception as e:
        print(e)
        sys.exit(1)

    print("Commands:")
    for cmd in cmds:
        print("  " + " ".join(cmd))
    print()

    while True:
        answer = input("Execute commands (y/N)? ").lower()
        if answer == 'y':
            break
        elif answer in ['n', '']:
            sys.exit(0)

    print("\nStart executing commands...\n")
    for cmd in cmds:
        print(" ".join(cmd))
        p = subprocess.run(cmd, shell=True)
        if p.returncode != 0:
            print("ERROR in ffmpeg processing")

