#!/usr/bin/env python3
"""Contact sheet per source frame: one row per clip, samples at 0%, 33%, 66%, 98% of duration. Usage: contact_sheet.py TESTDIR"""
import sys, subprocess, pathlib, json
T = pathlib.Path(sys.argv[1]); out = T/"review"/"sheets"; out.mkdir(parents=True, exist_ok=True)
tmp = pathlib.Path.home()/"work"/"cs"; tmp.mkdir(parents=True, exist_ok=True)
clips = sorted([*T.glob("kling/*.mp4"), *T.glob("runway/*.mp4"), *T.glob("parallax/*.mp4")])
fams = sorted({c.name.split("_")[0] for c in clips})
for fam in fams:
    rows = []
    for c in [c for c in clips if c.name.startswith(fam + "_")]:
        d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(c)]))
        tiles = []
        for k, p in enumerate([0.0, 0.33, 0.66, 0.98]):
            f = tmp/f"{c.stem}_{k}.jpg"
            subprocess.run(["ffmpeg","-loglevel","error","-y","-ss",f"{d*p:.2f}","-i",str(c),"-frames:v","1","-vf","scale=480:-2",str(f)], check=True)
            tiles.append(str(f))
        row = tmp/f"{c.stem}_row.jpg"
        label = c.stem.split("_",2)[-1]
        subprocess.run(["convert",*tiles,"+append","-gravity","NorthWest","-fill","yellow","-undercolor","#000a","-pointsize","22","-annotate","+6+4",label,str(row)], check=True)
        rows.append(str(row))
    subprocess.run(["convert",*rows,"-append","-quality","82",str(out/f"{fam}_sheet.jpg")], check=True)
    print(fam, len(rows))
