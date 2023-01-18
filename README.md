# `ffmpeg-sync` tool

Synchronize and trim bunch of consistently named videos.

## Usage

```sh
python .\ffmpeg-sync.py ..\preprocess\Subjects\S1\
```

Example directory contents of */path/to/video-directory*:
```
athlete1_trial1_cam1.mp4
athlete1_trial1_cam2.mp4
athlete1_trial2_cam1.mp4
athlete1_trial2_cam2.mp4
athlete1_indicex.xlsx
```


## *_indices.xlsx

Trim and sync definitions are defined in a file called Excel file (.xlsx) and it must be located in */video-directory*.

File fromat is

```csv
part1,part2,part3,video_name,sync_time,duration
```

Video name is constructed as `{part1}_{part2}_{part3}.mp4`.
