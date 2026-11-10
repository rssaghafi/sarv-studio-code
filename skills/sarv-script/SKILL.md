---
name: "sarv-script"
description: "Sarv & Simurgh screenwriter: source dossier, two-column script, line-by-line review, table read, cue map and source card from an approved G1 story. Use for research EPxx, write/revise the script, table read, Gate 1/2 prep."
---

# sarv-script v0.7 (S1 research, S3 script and table read; STUDIO.md v2.2)

Read first: Persian Stories/STUDIO.md (v2.2; section numbers changed in v2.0, find a rule by its ID in 03_templates/agents/rule-register.csv) and the film's `Films/EPxx_<slug>/film.yaml` (status, gate state, budget). Every path below is relative to the film folder `Films/EPxx_<slug>/` unless it starts with a root folder name (01_bible, 02_library, 03_templates, 05_ops). EP1 now lives in Films/EP01_zal-and-the-simurgh (migrated Nov 9; old folder numbering kept, see its README.md) and is read-only reference.
v0.7 scope: research mode, write mode (with the trim rule and the line-by-line fields), Stage 2 audit, table read, cue map. The G1 story session (S2) is still done by hand in chat until sarv-story exists. The Image Brief runs in parallel with G2 and is not part of this skill.

## Model rule (the Money, time and models section of STUDIO.md is the authority; read it, this is the summary)
Opus 5.5: research mode and the G1 story, the FIRST script draft (G2 Stage 1), the Stage 2 audit (in a FRESH chat, so it does not grade its own drafting), the closing segment and companion-video claims. Sonnet 5.5: everything else (revision rounds, cue map, table read, packet, records). If Sonnet fails the same item twice, that item goes to Opus. If a revision round changes words, the changed lines get a Stage 2 audit. Fable and Haiku are not used for script work. Claude cannot switch its own model: Reza switches it in the Claude app, and each switch is a Reza task in the film's plan.json. In your first message of a stage, name the model you are running on; if it is not the one the plan task calls for, say so and do not start the stage without Reza's word. Claude (not ChatGPT) writes the line-by-line review. At the end of every task, say whether Reza should start a new chat, give a ready-to-paste handoff prompt and the model to select. In EP3 round 1, count the lines Reza changes and record it in decisions.md (EP2 baseline: 65 of 67 spoken lines, 11 meaning shifts).

## Contract
| | |
|---|---|
| Inputs (approved only) | 01_story/brief.md; story.md (the approved G1 story: kept sections, must-haves, labels) + the working narration file it names (EP2: cinematic_narration_v3.md); the pronunciation list collected at G1 (02_cast/pronunciation.csv, 01_bible/voice/pronunciation.pls); character names; accepted masters in 02_cast / 03_world for picture notes; voice cards after G3 |
| Must preserve | Approved G1 story beats and scene order; character motivations; every [SOURCE]/[SCHOLAR]/[INTERP]/[INVENTED] label; line IDs once issued; what the poem says |
| May change | Wording, line order inside a scene, what is said vs. shown, who speaks a quoted line |
| Done when | Table read within ±10% of target runtime; every line labelled; every Persian name in glossary.md and the pronunciation list; cue map drafted; G2 approved |
| Escalate to Reza when | 2 revision rounds used; the source is ambiguous or sensitive; runtime off by >15% (give options, do not cut a kept beat on your own); a fix would change a G1-approved beat |

## Research mode (S1, Opus 5.5) → 01_story/research/
1. Pull the Persian passage from Ganjoor (ganjoor.net). Record each section and verse range URL in sources.csv: `id,type,title,url,verses,used_for,label`.
2. Summarize the plot beat by beat in English, translated from the Persian. Never work from, quote or paraphrase a modern copyrighted English translation.
3. Context (author, date, manuscript tradition, scholarly readings, later legends). Label each item: text / documented history / legend / interpretation, with a source.
4. Flag sensitivities and adaptation questions for the G1 story.
5. Write dossier.md. Auto-check: every claim has a sources.csv id.
6. G1 deliverable also lists EVERY proper name with a proposed respelling, so Reza records the ones the machine fails (02_cast/pronunciation.csv).

## Write mode (S3, Stage 1, Opus 5.5) → 01_story/
`script.md` is always the current script. Before replacing it, move the old one to `_history/script_v<n>_<YYYYMMDD>.md` (never overwrite or delete). Keep the script as DATA in the film's `tools/` (for example g2_script_data_v<n>.py plus a build script that writes script.md and the metrics), so every revision is a rebuild, not a retype. Structure: cold open hook (≤30 s) → 3–6 chapters → climax → "What the text says / what we changed" (2–3 min, separate from the story runtime) → pointer to the next story.
Each line is one block. Two columns = AUDIO and SCREEN:
```
### L014 · CH2 · [SOURCE: Ganjoor <section>, v.112–114]
AUDIO  SIMURGH (low, warm): "…"
SCREEN Medium, locked. The Simurgh lowers her head to the nest; Zal reaches up. Camera: slow push-in. Music: Simurgh motif, soft.
G1 id: S05-3 · TRIM: <what was dropped or changed, if anything>
```
- Line IDs are stable: never renumber. Inserts become L014a; cuts stay listed as `L015 CUT`. Every line carries its G1 passage id (`G1 id:`) so Reza's G1 approvals trace.
- Silent or music-only beats are lines with `AUDIO — (music 3 s)` or `AUDIO — (silence 2 s)`. At least 2 per chapter.
- Allocation rules: the narrator never describes what the image already shows; the key emotional line goes to a character. A quoted speech is spoken by its character: drop the narrator tag ("she says") and move the gesture to the SCREEN note. Speakers are TEMPORARY roles until G3 voice cards.
- SCREEN follows the picture, motion and camera rules in STUDIO.md (rule-register.csv): 3/4 views; no wing beats, head turns to camera or bows on screen; one camera move per shot, neighbouring shots different; `speaker` push on a character line; name the accepted master (cast-xx, loc-xx, prop-xx) each picture is built from; do not show a location element before the story reaches it.
- Delivery notes go in parentheses. Quoted dialogue that renders the Persian is [SOURCE] with a verse ref; connective scenes we add are [INVENTED].
- Metrics: spoken words, lines, silence seconds, estimated runtime at 140 wpm plus 0.4 s per spoken line, per chapter and total.

### Line-by-line fields (format file 03_templates/review/g2-line-review-format.md)
Every line in the G2 packet carries: Original; Proposed spoken wording (plain spoken English, exactly what the actor says); Why / source boundary (SOURCE/INTERP/INVENTED, G1 trace id, and whether the wording changes what the poem says: no / adds / drops / changes meaning); Performance / situation (not spoken: for the voice and for the pictures); Proposed change in order and Propose remove (with justification) only where they apply. Mark every line that may change meaning, whose Persian reading is uncertain, or that crosses the source boundary with "FLAG:" in its trim note. These flagged lines are the only input to Stage 2.

### Trim rule (G2, toward the target length)
Trim in this order: (1) wording inside kept passages (narrator tags, repeated clauses); (2) passages the G1 notes mark trim-first; (3) STOP: any cut of a kept beat or bridge goes to Reza as a short list with seconds saved, not done on your own. Every trim is written in the line's `TRIM:` note. FLAG any trim, merge or reorder that changes what the poem says (dropped clause, changed order of events, removed contradiction) and put it in the packet's flag list first. Never trim silently, and do not trim Reza's own wording without flagging it.

Also write (in 01_story/): glossary.md (every Persian name: spelling, proposed IPA, source form), source-card.md (sources and the source/interp/invented map for the closing segment and description), changelog.md (what changed since the G1 story and each version).

## Stage 2 audit (Opus 5.5, fresh chat, flagged lines only)
Input: only the FLAG lines, the Persian passage reference and the literal translation. For each line say exactly one of: wording only / adds / drops / changes meaning. Quote the words that changed and say what the Persian supports. If the Persian reading is uncertain, say so; do not guess. The result goes first in the packet's flag list. In a revision round, Sonnet applies exactly what Reza listed and Opus audits only the lines whose words Reza changed.

## Table read (S3 step 4, Sonnet 5.5, only AFTER Stage 2) → 05_sound/tableread_v<n>/
1. State the fal estimate in chat (lines × characters, price per unit) BEFORE any call, then wait for Reza's yes. Temporary voices: one narrator + one per speaking role (nothing speaks in a table read before it has a voice card; at G2 use clearly temporary voices). Use the fal connector's ElevenLabs TTS (look up the current endpoint with recommend_model). Do not use the ElevenLabs Starter quota (see the Money, time and models section of STUDIO.md).
2. Submit lines as one batch (submit_jobs), collect with wait_for_jobs. Silent beats = silence of the stated length; 0.4 s gap between lines. Run an onset check (speech-to-text on the first 2 s) and make 3 seeds for the first line of every scene.
3. Concatenate with ffmpeg into tableread_v<n>.mp3 and write tableread_v<n>.json: `{line_id, start_s, end_s, words}`.
4. Claude cannot listen. Report metrics: runtime vs. target, words per minute per chapter (target 130–150; George runs ~161), longest stretch of narration without a character line or silence, sentences over 30 words, name-dense lines. Flag lines to cut.
5. Log the cost to your own cost log (05_ops/cost-log.csv for Reza, cost-log_<name>.csv for others; `python3 03_templates/agents/tools/sarv_logs.py path cost` prints it) (stage table-read).

## Cue map (G2, as soon as the script locks) → 05_sound/cue_map.csv
Mark emotional beats and silences; choose 4–6 cues per ten-minute film (opening, sorrow, nature/Simurgh, tension, reunion, close) plus opening/closing sting and the hero's theme; one ambience bed per location and about ten spot sounds. Columns: `cue_id,type,scene,line_from,line_to,description,source_track,licence_row,duration_s`. Rules: no single track under the whole film; no audible fades mid-film; no cue over ~3 min.

## Gate 2 packet → Output/G2_script/
Build with `03_templates/review/build_packet.py` (spec with the script lines as `line` items, `audio` = the table read, `audio_at` per line, metrics table, Claude's flag list first, the cue map as a decision). One self-contained HTML; Reza replies with IDs. Every line whose audio plays must have a visible item (unchanged lines may be collapsed). Apply only the listed changes; log them in changelog.md and decisions.md. Max 2 rounds. Ask Reza one question at a time.

## Not in v0.7
Story room review (done by hand in chat), automatic STT round trip beyond the onset check, final voices.