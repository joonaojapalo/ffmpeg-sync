# `ffmpeg-sync` tool

Synchronize and trim bunch of consistently named videos.

## Usage

```sh
python ffmpeg-sync.py /path/to/video-directory
```

Tool reads `Synclist.csv`, finds corresponding files runs video processing commans using exsisting installation of **ffmpeg**.

Example directory contents of */path/to/video-directory*:
```
athlete1_trial1_cam1.mp4
athlete1_trial1_cam2.mp4
athlete1_trial2_cam1.mp4
athlete1_trial2_cam2.mp4
Synclist.csv
```


## `Synclist.csv`

Trim and sync definitions are defined in a file called `Synclist.csv` and it must be located in */video-directory*.

File fromat is

```csv
part1,part2,part3,video_name,sync_time,duration
```

If `video_name` is not given it's constructed as `{part1}_{part2}_{part3}.mp4`.

Example file:

```csv
athlete1,trial1,cam1,,9.620,7
athlete1,trial1,cam2,,9.620,7
athlete1,trial2,cam1,,9.620,7
athlete1,trial2,cam2,,9.620,7
```
