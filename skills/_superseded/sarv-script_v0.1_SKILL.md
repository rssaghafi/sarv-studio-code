---
name: sarv-script
description: Sarv & Simurgh screenwriter: source dossier, two-column script, table read and source card from an approved treatment. Use for research EP0x, write/revise the script, table read, Gate 2 prep.
---
# sarv-script v0.1 (Playbook rev 5: S1 research, S3 script and table read)

Read first: Persian Stories/STUDIO.md (§1, §6, §7), the episode brief.md and manifest.yaml if present.
v0.1 scope: research mode and write mode. The treatment (S2) is still done by hand in chat until sarv-story exists.

## Contract
| | |
|---|---|
| Inputs (approved only) | 01_research/brief.md; treatment.md + allocation.csv after G1; character profiles; 01_bible/voice/pronunciation.pls if it exists |
| Must preserve | Approved treatment beats and scene order; character motivations; every [SOURCE]/[INTERP]/[INVENTED] label; line IDs once issued |
| May change | Wording, line order inside a scene, what is said vs. shown |
| Done when | Table read within ±10% of target runtime; every line labelled; every Persian name in glossary.md; G2 approved |
| Escalate to Reza when | 2 revision rounds used; the source is ambiguous or sensitive; runtime off by >15%; a fix would change a G1-approved beat |

## Research mode (S1) → 04_episodes/EP##_slug/01_research/
1. Pull the Persian passage from Ganjoor (ganjoor.net). Record each section and verse range URL in sources.csv: `id,type,title,url,verses,used_for,label`.
2. Summarize the plot beat by beat in English, translated from the Persian. Never work from, quote or paraphrase a modern copyrighted English translation.
3. Context (author, date, manuscript tradition, scholarly readings, later legends). Label each item: text / documented history / legend / interpretation, with a source.
4. Flag sensitivities and adaptation questions for the treatment.
5. Write dossier.md. Auto-check: every claim has a sources.csv id.

## Write mode (S3) → 02_script/
Script file: script_v<n>.md (never overwrite). Structure: cold open hook (≤30 s) → 3–5 chapters → climax → "What the text says / what we changed" (2–3 min) → pointer to the next story.
Each line is one block. Two columns = AUDIO and SCREEN:
```
### L014 · CH2 · [SOURCE: Ganjoor <section>, v.112–114]
AUDIO  SIMURGH (low, warm): "…"
SCREEN Medium, locked. The Simurgh lowers her head to the nest; Zal reaches up. Music: Simurgh motif, soft.
```
- Line IDs are stable: never renumber. Inserts become L014a; cuts stay listed as `L015 CUT`.
- Silent or music-only beats are lines with `AUDIO — (music)` or `AUDIO — (silence 2 s)`. At least 2 per chapter.
- Allocation rules: the narrator never describes what the image already shows; the key emotional line goes to a character.
- SCREEN follows STUDIO.md §2–§4: 3/4 views; no wing beats, head turns to camera or bows on screen; camera moves are notes for sarv-render, one per shot.
- Delivery notes go in parentheses. sarv-voice turns them into audio tags later.
- Quoted dialogue that renders the Persian is [SOURCE] with a verse ref; connective scenes we add are [INVENTED].
Also write: glossary.md (every Persian name: spelling, proposed IPA, source form), source-card.md (sources and the source/interp/invented map for the closing segment and description), changelog.md (what changed since the treatment and each version).

## Table read (S3 step 4)
1. Split the script into lines. Temporary voices: one narrator + one per speaking role. Use the fal connector's ElevenLabs TTS (pay per use; look up the current endpoint with recommend_model). Do not use the ElevenLabs Starter quota (STUDIO.md §6).
2. Submit lines as one batch (submit_jobs), collect with wait_for_jobs, download into 02_script/tableread_v<n>/. Silent beats = silence of the stated length; 0.4 s gap between lines.
3. Concatenate with ffmpeg into tableread_v<n>.mp3 and write tableread_v<n>.json: `{line_id, start_s, end_s, words}`.
4. Claude cannot listen. Report metrics: runtime vs. target, words per minute per chapter (target 130–150), longest stretch of narration without a character line or silence, sentences over 30 words, name-dense lines. Flag lines to cut.
5. Log the cost to 05_ops/cost-log.csv (stage table-read).

## Gate 2 packet → Output/EP##_G2_script/
An HTML page: the script as two columns with line IDs, the table-read player with clickable line IDs (from the json), the metrics, and the changelog. Reza replies with IDs. Apply only the listed changes; log them in changelog.md and decisions.md. Max 2 rounds.

## Not in v0.1
Story room review (done by hand in chat), automatic STT round trip, final voices. Extract v0.2 from the EP1 record (Nov 28–Dec 1).
