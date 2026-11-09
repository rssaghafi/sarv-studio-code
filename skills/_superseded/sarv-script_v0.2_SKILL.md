---
name: sarv-script
description: Sarv & Simurgh screenwriter: source dossier, two-column script, table read, cue map and source card from an approved treatment. Use for research EPxx, write/revise the script, table read, Gate 1/2 prep.
---
# sarv-script v0.2 (Playbook rev 6: S1 research, S3 script and table read; STUDIO.md v1.3 layout)

Read first: Persian Stories/STUDIO.md v1.3 (§1, §6, §7, §9) and the film's `Films/EPxx_<slug>/film.yaml` (status, gate state, budget). Every path below is relative to the film folder `Films/EPxx_<slug>/` unless it starts with a root folder name (01_bible, 02_library, 03_templates, 05_ops). EP1 (still under 04_episodes/EP01_zal-and-the-simurgh with its old numbering) is read-only reference until the Nov 9 migration check.
v0.2 scope: research mode, write mode, table read, cue map. The treatment (S2) is still done by hand in chat until sarv-story exists.

## Contract
| | |
|---|---|
| Inputs (approved only) | 01_story/brief.md; treatment.md + allocation.csv after G1; the pronunciation list collected at G1 (02_cast/pronunciation.csv, 01_bible/voice/pronunciation.pls); character names; voice cards after G3 |
| Must preserve | Approved treatment beats and scene order; character motivations; every [SOURCE]/[SCHOLAR]/[INTERP]/[INVENTED] label; line IDs once issued |
| May change | Wording, line order inside a scene, what is said vs. shown |
| Done when | Table read within ±10% of target runtime; every line labelled; every Persian name in glossary.md and the pronunciation list; cue map drafted; G2 approved |
| Escalate to Reza when | 2 revision rounds used; the source is ambiguous or sensitive; runtime off by >15%; a fix would change a G1-approved beat |

## Research mode (S1) → 01_story/research/
1. Pull the Persian passage from Ganjoor (ganjoor.net). Record each section and verse range URL in sources.csv: `id,type,title,url,verses,used_for,label`.
2. Summarize the plot beat by beat in English, translated from the Persian. Never work from, quote or paraphrase a modern copyrighted English translation.
3. Context (author, date, manuscript tradition, scholarly readings, later legends). Label each item: text / documented history / legend / interpretation, with a source.
4. Flag sensitivities and adaptation questions for the treatment.
5. Write dossier.md. Auto-check: every claim has a sources.csv id.
6. G1 deliverable also lists EVERY proper name with a proposed respelling, so Reza records the ones the machine fails (02_cast/pronunciation.csv).

## Write mode (S3) → 01_story/
`script.md` is always the current script. Before replacing it, move the old one to `_history/script_v<n>_<YYYYMMDD>.md` (never overwrite or delete). Structure: cold open hook (≤30 s) → 3–5 chapters → climax → "What the text says / what we changed" (2–3 min) → pointer to the next story.
Each line is one block. Two columns = AUDIO and SCREEN:
```
### L014 · CH2 · [SOURCE: Ganjoor <section>, v.112–114]
AUDIO  SIMURGH (low, warm): "…"
SCREEN Medium, locked. The Simurgh lowers her head to the nest; Zal reaches up. Music: Simurgh motif, soft.
```
- Line IDs are stable: never renumber. Inserts become L014a; cuts stay listed as `L015 CUT`.
- Silent or music-only beats are lines with `AUDIO — (music)` or `AUDIO — (silence 2 s)`. At least 2 per chapter.
- Allocation rules: the narrator never describes what the image already shows; the key emotional line goes to a character.
- SCREEN follows STUDIO.md §2–§5: 3/4 views; no wing beats, head turns to camera or bows on screen; camera moves are notes for sarv-render, one per shot.
- Delivery notes go in parentheses. Quoted dialogue that renders the Persian is [SOURCE] with a verse ref; connective scenes we add are [INVENTED].
Also write (in 01_story/): glossary.md (every Persian name: spelling, proposed IPA, source form), source-card.md (sources and the source/interp/invented map for the closing segment and description), changelog.md (what changed since the treatment and each version).

## Table read (S3 step 4) → 05_sound/tableread_v<n>/
1. Split the script into lines. Temporary voices: one narrator + one per speaking role (nothing speaks in a table read before it has a voice card; at G2 use clearly temporary voices). Use the fal connector's ElevenLabs TTS (pay per use; look up the current endpoint with recommend_model). Do not use the ElevenLabs Starter quota (STUDIO.md §6).
2. Submit lines as one batch (submit_jobs), collect with wait_for_jobs. Silent beats = silence of the stated length; 0.4 s gap between lines. Run an onset check (speech-to-text on the first 2 s) and make 3 seeds for the first line of every scene.
3. Concatenate with ffmpeg into tableread_v<n>.mp3 and write tableread_v<n>.json: `{line_id, start_s, end_s, words}`.
4. Claude cannot listen. Report metrics: runtime vs. target, words per minute per chapter (target 130–150; George runs ~161), longest stretch of narration without a character line or silence, sentences over 30 words, name-dense lines. Flag lines to cut.
5. Log the cost to 05_ops/cost-log.csv (stage table-read).

## Cue map (G2, as soon as the script locks) → 05_sound/cue_map.csv
Mark emotional beats and silences; choose 4–6 cues per ten-minute film (opening, sorrow, nature/Simurgh, tension, reunion, close) plus opening/closing sting and the hero's theme; one ambience bed per location and about ten spot sounds. Columns: `cue_id,type,scene,line_from,line_to,description,source_track,licence_row,duration_s`. Rules: no single track under the whole film; no audible fades mid-film; no cue over ~3 min.

## Gate 2 packet → Output/G2_script/
Build with `03_templates/review/build_packet.py` (spec with the script lines as `line` items, `audio` = the table read, `audio_at` per line, metrics table, Claude's flag list first, the cue map as a decision). One self-contained HTML; Reza replies with IDs. Apply only the listed changes; log them in changelog.md and decisions.md. Max 2 rounds.

## Not in v0.2
Story room review (done by hand in chat), automatic STT round trip beyond the onset check, final voices.
