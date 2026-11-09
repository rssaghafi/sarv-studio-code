---
name: sarv-render
description: Sarv & Simurgh renderer: renders Remotion compositions (tests, animatics, films, Shorts) in the Cowork VM in resumable steps, applies the camera rules, checks output. Use for render, animatic, parallax, camera move, master.
---
# sarv-render v0.1 (Playbook rev 5: S6 step 4, S11)

Read first: Persian Stories/STUDIO.md (§2, §4, §5, §8). Also use the installed Remotion skills (best-practices, render, captions) for component code.
v0.1 scope: reliable rendering + the camera rules + current components. Master/animatic templates and the full camera kit arrive Oct 29 (v0.2).

## Contract
| | |
|---|---|
| Inputs (approved only) | Remotion project (Sarv Studio Code/bench now; Sarv Studio Code/remotion from Oct 29); episode props.json; approved frames, clips and audio |
| Must preserve | Shot order and durations from the alignment/shot list; approved frames and clips unaltered (no re-grading); line timing |
| May change | Camera moves within the rules below; transitions; title cards; particle passes |
| Done when | Output has the expected frame count, resolution and duration; loudness within ±1 LU of −16 LUFS (finished films); Claude's frame-sample check is clean |
| Escalate when | A shot needs a move the rules ban; a render fails twice at the same chunk; runtime differs from the locked animatic |

## Camera rules (all camera work happens here, never in the video model)
- One move per shot: push-in, pan, 2-layer parallax, or none. Ease in-out (sine). Gold-dust particles optional.
- Scale stays modest: ≤1.15 over a long hold, ≤1.10 over a 5-s shot. Parallax relative offset ≤14 px (larger offsets show the background ghost edge, Oct 17).
- Moves go on top of locked-camera Kling clips or stills. Full-bleed frame, no border overlay.
- Wing beats and head turns, when a beat needs them: cut-out animation from layered plates (e.g. feather-*-v2, flight-*-v2/v3), not a generated clip.
- 9:16 Shorts use separately outpainted frames, not a centre crop of the 16:9 hero.

## Render procedure (scripts/render.sh)
The VM cap is ~180 s per call and background jobs die, so every render is a job of short steps:
```
R="$HOME/mnt/Sarv Studio Code/scripts/render.sh"
bash "$R" setup                                   # once per session (~30 s): copies the project to ~/sarv-render, npm install
bash "$R" init  <job> <Composition> <public_dir> <dest.mp4> [props.json]
bash "$R" step  <job>                             # repeat until it prints VIDEO DONE (one call each)
bash "$R" finish <job>                            # audio pass, concat, mux, loudness report, copy to dest
bash "$R" clean <job>
```
- public_dir = the folder holding the media the composition loads (staticFile paths are relative to it).
- dest is never overwritten: use versioned names. Tests → 99_tests/<test>/; animatic → 08_review/animatic_v<n>.mp4; master → 09_deliver/master_v<n>.mp4; Shorts → 09_deliver/shorts/.
- Tuning knobs: CHUNK_FRAMES (default 300), STEP_BUDGET_S (default 110).
- Measured Oct 17 (60 s, 1080p, simple scene): init 19 s + 2 step calls (145 s) + finish 31 s ≈ 3.3 min, 1800/1800 frames, seams clean. A 12-min episode ≈ 40 min and ~20 step calls; tune chunk size and concurrency on Oct 29.

## After every render
1. Check frames, duration, resolution (ffprobe) and loudness (printed by finish).
2. Contact sheet with scripts/contact_sheet.py; Claude checks the samples for black frames, drift, missing layers.
3. Log render time in time-log.csv when it is part of an episode; Reza judges motion and style by watching.

## Components available now
- bench/src/Parallax.tsx: 2-layer parallax (background + BiRefNet cut-out) + gold-dust particles. Props {id, dir}; files <id>_bg.jpg, <id>_fg_s.png.
- bench/src/Root.tsx Scene: slow push-in + title card. Its gold double border belongs to the retired Safavid look; do not reuse it.

## Not in v0.1
Animatic/master templates, captions, Shorts compositions, FCPXML export (S11 step 5). Build from Oct 29 and from the EP1 record.
