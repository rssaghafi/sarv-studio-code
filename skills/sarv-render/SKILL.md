---
name: "sarv-render"
description: "Render Sarv & Simurgh films, animatics and Shorts with the pinned Remotion kit in short resumable steps."
---

# sarv-render v0.4 (STUDIO.md v2.2; recipes also in 03_templates/agents/editor-renderer.md)

Read first: Persian Stories/STUDIO.md (current version; it wins) and 03_templates/agents/editor-renderer.md and the film's `Films/EPxx_<slug>/film.yaml` (pinned engine/kit version). Also use the installed Remotion skills (best-practices, render, captions) for component code. Paths below are relative to the film folder `Films/EPxx_<slug>/` unless they start with a root folder name. EP1 lives in Films/EP01_zal-and-the-simurgh (migrated Nov 9; old folder numbering kept, see its README.md).

## Contract
| | |
|---|---|
| Inputs (approved only) | Remotion project (Sarv Studio Code/remotion, kit pinned in film.yaml); 08_edit/props.json; 04_storyboard/shots.csv (the single source of truth for pictures, tiers, moves, cues); approved frames in 06_picture/approved/; clips in 07_motion/; audio in 05_sound/ |
| Must preserve | Shot order and durations from the shot list; approved frames and clips unaltered (no re-grading); line timing |
| May change | Camera moves within the rules below; transitions; title cards; particle passes |
| Done when | Output has the expected frame count, resolution and duration; loudness within ±1 LU of −16 LUFS (finished films); Claude's frame-sample check is clean; every picture rendered is the picture in shots.csv |
| Escalate when | A shot needs a move the rules ban; a render fails twice at the same chunk; runtime differs from the locked animatic |

## Camera rules (all camera work happens here, never in the video model)
- One move per shot, from the shot list: push-in, pan, 2-layer parallax, `speaker`, or `drift`. Ease in-out (sine). Gold-dust particles optional. Every shot moves; neighbouring shots use different moves; silence beats get `drift` (1.02→1.05, ≤±5 px) + gold dust, never a held image or frozen last frame.
- `speaker`: push toward the speaking character at a focus point, cap 1.25 on 2K frames; key lines cut to a real close-up frame instead of pushing further.
- Scale stays modest: ≤1.15 over a long hold, ≤1.10 over a 5-s shot (speaker cap above). Parallax relative offset ≤14 px (larger shows the background ghost edge).
- Moves go on top of locked-camera Kling clips or stills. Full-bleed frame, no border overlay.
- Wing beats and head turns, when a beat needs them: cut-out animation from layered plates, not a generated clip.
- Shorts and chapter cuts (ED-05): full-screen 9:16 only, 1080x1920, cropped from the 1920x1080 film with a per-shot crop plan Reza has approved; each cut 3:00 or under; pans are timed to the narration; title and text cards are scaled to fit on a lapis ground, never cropped. Built with ffmpeg (no paid calls). No lapis letterbox and no plain 16:9 cuts unless Reza asks. No outpainted frames.

## Render procedure (scripts/render_v03.sh; it stops if the sound step fails, ALLOW_SILENT=1 only for a deliberately silent render)
Start with the health check (free disk on the work volume, engine version, balance). The VM cap is ~180 s per call and background jobs die, so every render is a job of short steps:
```
R="$(ls -d "${SARV_CODE:-/nonexistent}" "$HOME/Code/Sarv Studio Code" "$HOME"/mnt/*"Sarv Studio Code" 2>/dev/null | head -1)/scripts/render_v03.sh"   # code folder: SARV_CODE, else ~/Code, else any mounted folder ending in Sarv Studio Code
bash "$R" setup                                   # once per session (~30 s): copies the project to ~/sarv-render, npm install
bash "$R" init  <job> <Composition> <public_dir> <dest.mp4> [props.json]
bash "$R" step  <job>                             # repeat until it prints VIDEO DONE (one call each)
bash "$R" finish <job>                            # audio pass, concat, mux, loudness report, copy to dest
bash "$R" clean <job>
```
- public_dir = the folder holding the media the composition loads (staticFile paths are relative to it).
- dest is never overwritten: use versioned names. Tests → 99_tests/<test>/; animatic → Films/EPxx/08_edit/animatic_v<n>.mp4 (review copy shown in Output/G4_storyboard/); review copies go in Output/<gate>/; approved files are moved (not copied) into 10_publish: film → Full Movie/, Short → Shorts/Highlights/, chapters → Shorts/Chapters/ (FI-11; 09_deliver is retired).
- Tuning knobs: CHUNK_FRAMES (default 300), STEP_BUDGET_S (default 110).
- Measured Oct 17 (60 s, 1080p, simple scene): init 19 s + 2 step calls (145 s) + finish 31 s ≈ 3.3 min. A 12-min episode ≈ 40 min and ~20 step calls.

## After every render
1. Check frames, duration, resolution (ffprobe) and loudness (printed by finish).
2. Contact sheet with scripts/contact_sheet.py; Claude checks the samples for black frames, drift, missing layers, and that pictures match shots.csv.
3. Log render time in time-log.csv (Claude session minutes); Reza judges motion and style by watching and his minutes go in the attention column.

## Components available now
- Sarv Studio Code/remotion (kit v0.7): see its README for Parallax, speaker, drift, particles and the title options veilIn, veilOut, textIn, textOut, dust. The old bench Scene's gold double border belongs to the retired Safavid look; do not reuse it.