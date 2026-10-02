# Io · 永恒: progress

## State (2026-10-02)
**Sprint 0 done:** brief confirmed, TREATMENT.md (story, physics table, clip list, beat sheet 04, sound),
`tools/physics.py`, scaffold copied from childhood-desktop (render/preview with `--engine` + `--animatic`,
`blender/lib/{rig,nodes,shot}.py`), kit paths `../../_kit`, 6 clips = 60 s (`node ../../_kit/lib/film.mjs`).
No shot scripts yet, nothing rendered.

**Next: Sprint 1, look spike.** Two Cycles stills at the shots' real lenses, approved before any shot work:
(a) 02-scale: 135 mm, ridge + astronaut stand-in (capsule) + lander proxy, half-lit Jupiter as a wall behind;
(b) 04-eclipse at peak: 35 mm, black disc + red ring, dark ground, glowing vents, stars.
Needs: `blender/lib/io_world.py` (curved terrain patch, sulfur/frost/lava materials), `jupiter.py` (true-size sphere
lit by the Sun lamp, real map, eclipse ring shell), `sky.py` (Sun 0.1°, 50 W/m², star dome, Jupiter-shine fill),
the Jupiter map downloaded into `../../_assets/textures/` (log in REFERENCES.md). Start from
`../imagnation/blender/spike/water_spike.py` for the camera/planet/grade code. Measure s/frame on the 04 still.

## Sprints
0. ✅ Treatment, physics, scaffold.
1. Look spike: 2 stills (02, 04) → user approves the look.
2. Astronaut: pick a rigged model (show author/licence/preview first), Mixamo clip (user downloads), `retarget.py`,
   turntable still → user approves.
3. Shots 01 → 06: action + Workbench animatic + 3-still Cycles check → locked (one shot per session).
4. Whole-film animatic; score + suit foley cut to it; caption + counter overlay in compile.
5. Overnight batch render (one yes for the list + hours) → compile, `check.mjs`, srt, poster.

## Decisions (locked)
- Format: 1920×1080, 24 fps, picture 1920×804 (2.39:1) rendered, letterboxed at encode (saves ~25 % render time).
- Location: 75° from the sub-Jupiter point → Jupiter centre at 14.8°, lower limb 5.0°, fixed in every shot.
- Renderer: Cycles for every shot (light is the subject: phase, eclipse, vacuum shadows); Workbench animatics.
- No narration; EN (Cinzel) + 简中 (Noto Serif SC) captions in clip `caps`; 03 counter `+0 h → +42 h`.
- Scale cues: distant astronaut (ready-made rigged + Mixamo), code-built lander, boot prints.
- Standalone episode 2; grade matched to 巨物.

## Open technical checks
- Eclipse ring colour/width (Cassini / New Horizons eclipse images) and how it brightens near contact.
- Jupiter map resolution at 135 mm (2488 px disc) → OPAL map if the Cassini map is soft.
- Caption + counter overlay route for Blender frames (kit compile has no overlay for style `blender`; film-local
  ffmpeg drawtext/ASS pass or a canvas overlay, decide in Sprint 4).
- Exposure: AgX can't hold sunlit sulfur and a 6-stop-darker eclipse in one exposure: key `film exposure` per shot
  (04 ramps it up after second contact, "eyes adjust").

## Notes / lessons
