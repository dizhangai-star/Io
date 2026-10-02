# Io · 永恒: progress

## State (2026-10-03)
**Sprint 1 (look spike) done 2026-10-02.** Stills in `frames/spike/` (sheet.png):
02 day (Sun 2.6° up, Jupiter 41 % lit, sunlit ridge), 02 night (Sun −13°, Jupiter 93 % lit, ridge + figures in
silhouette), 04 eclipse peak (28 mm, black disc + red ring, lava lake, stars). Libs: `blender/lib/io_world.py`
(polar terrain on the curved surface, Io surface, lava lake, vents, Io-body occluder, astronaut/lander proxies),
`jupiter.py` (true angle/place, Cassini map, eclipse ring shell), `sky.py` (Sun lamp, stars, exposure); shots
`s02_scale.py`, `s04_eclipse.py` are static spike versions (`--x k=v` options through `preview.mjs`).
Cost: **≈ 7 s/frame** at 1920×804, 64 spp (all three looks), + ~15 s scene build per process.

**User 2026-10-02:** 02 = night (`frames/spike/02-night-1km.png`), 04 = 28 mm, ridge at 1 km. Asked for a sharper
Jupiter map and real Io imagery to dress the code-built ground. Done the same day: Jupiter 14K map (Jónsson, Cassini
+ Juno poles) is the default in `jupiter.py` (`frames/spike/02-night-14k.png`, sharp at 135 mm, near true colour so
paler than PIA07782; 02 exposure −4.8). Downloaded the USGS Io colour mosaic + 7 Galileo close-ups; `tools/maps.py io`
cuts our real site (75° N on the sub-Jupiter meridian) out of the mosaic: **the data there is smeared (no good
coverage poleward of ~60°)**, and its colours are the polar orange-brown (site mean linear 0.31/0.20/0.08), not the
yellow equatorial plains the code palette assumed.
**Ground colour (user 2026-10-02: compromise):** `io_world.surface` base = the site's six measured polar browns
(`POLAR`), laid out by km noise + the Galileo PIA02507 pattern (5.5 m/px, mirrored, mask only), with frost fields
(~10 %), sulfur deposits (~6 %), red sulfur and dark lava on top (`frames/spike/ground-polar-test.png`: 04 framing
with the Sun 11° up, and 02 day). Low sun + AgX makes the plain read grey-tan; judge saturation in 01/03 look-dev.
**Sprint 2 (astronaut) done 2026-10-03.** Model chosen by the user: Blend Swap #12622 NASA EMU suit, rigged
(jgilhutton, CC-BY 4.0), in `../../_assets/models/astronaut-emu-12622/`. `tools/prep_astronaut.py` writes
`emu_clean.blend` beside it (multires L3 applied, 2 stray sculpt vertices relaxed, IK/FK helpers + 6 dependency cycles
removed, plain deform bones, gold sun visor kept down, soles on z = 0, no emblems). `blender/lib/astronaut.py` `load(sc, loc,
heading)` appends it under an empty root (proxy fallback). Look board `blender/shots/board_astronaut.py` →
`frames/astronaut/sheet.png` (4 headings Sun-lit, 2 against the light, 200 mm helmet): ≈ 5 s/still at 50 %.
**Look approved (user 2026-10-03), emblems plain** (the original's UN flags, ISS patch and shoulder patch removed).
Motion: Mixamo "Breathing Idle" (`../../_assets/mocap/`, 9.93 s, loops cleanly) → `blender/lib/retarget.py`
`retarget(sc, arm, 'Breathing Idle.fbx', extra={'chest': f→Quaternion})` bakes it to an Action (≈ 3 s for 240 frames):
rest-aligned world-rotation transfer in the character's own frame, hips → root bone, 30 → 24 fps, loop, additive
direction layer (02 look-up = chest lean back, 20° tested). Feet slide ≤ 23 mm, hips sway 14 cm. Board `--clip` mode
→ `frames/astronaut/idle.png`; Workbench motion draft `out/astronaut-idle-animatic.mp4` (0.1 s/frame).
**Motion approved (user 2026-10-03).**
**Sprint 3 · shot 01 locked (user 2026-10-03).** `blender/shots/s01_horizon.py`: 24 mm, eye
1.6 m, one tilt −30° → +14° (trapezoid speed, smooth ramps, 0.8–7.4 s; hold after), Sun elongation 70°
(`physics.SHOT['01']`: Sun 5.1° up at az −71°, out of frame left; Jupiter 33 % lit, its lit lower limb enters the
frame top at 3.4 s). Ground: frost plain (`surface(frost=1, clod=0.06, prints=True)`), two terrain patches (near
0.5–24 m, 1201 seg; far 24 m–9 km, 401 seg, seam crack-free), 124 boot prints (`blender/lib/prints.py`: out-trail from
the ladder foot toward Jupiter, return trail to the camera, milling at the ladder; 0.8 cm deep, rim, 2 mm chevron
lugs fading by 6 m, 'prints' attribute half-darkens the trodden frost), one tilted-block massif on the horizon right
at true distance (115 km, curvature hides 3 km). Lander: new `blender/lib/lander.py` (generic, ours: 8 m pad to pad,
gold-foil stage, white cabin, telescoping struts, ladder on leg 1); in 01 only one footpad + leg + ladder foot show.
Animatic `out/01-horizon-animatic.mp4` (0.2 s/frame); Cycles check `frames/01-horizon-strip.png` (0.5 / 4.5 / 8.5 s):
≈ 9 s/frame full res, 64 spp → ≈ 33 min for the clip. Shared-lib changes keep 02/04 identical (new `surface` args
default off; Workbench now resets the film exposure to 0).
User review 2026-10-03: end pitch +14°, prints shallower (were 1.5 cm, read as dark slots), left massif removed:
all done (strip + animatic refreshed); **01 locked**. **Next: shot 02 (animate the spike: astronaut idle + look-up,
plume rising) in a new session.**
**Sprint 3 · shot 02 locked (user 2026-10-03).** Plume dropped from 02 (user 2026-10-03): with the crest at 8° only
8–13.8° of sky is in frame, and any plume whose top lands there is wider than the frame (100 km Prometheus-type at
330 km spans 43°), its 22-min flight moves ~7 km in 11 s, and Jupiter covers the left side so it would be haze on the
disc; **the plume moves to 05** (24 mm from 3 km, sunlit canopy above Io's night shadow, which ends 100–250 km up).
`s02_scale.py` animated: EMU + Breathing Idle on the crest (heading 125°, facing right and away), real `lander.build`
6 m behind the crest edge. At 1 km the suit is ≈ 14 px tall (7.2 px/m), so a lean alone moves the helmet ~1.5 px: the
look-up = chest lean back 15° + the near (right) arm raised 115° to point at Jupiter (retarget `extra` on `chest` and
`upper_arm.R`): idle 0–2.5 s, raise 2.5–4.5 s, hold, lower 8.0–9.8 s, lean held. Animatic (Workbench, 100 %,
0.3 s/frame) `out/02-scale-animatic.mp4` + review crop `out/02-scale-animatic-crop.mp4` (full frame over a 4×
figure crop; mp4s are padded to 1080, crop from the PNGs); Cycles check `frames/02-scale-check.png` (1 / 5 / 10.5 s,
full res, 64 spp, 3 stills in 56 s ≈ 7 s/frame + build): the raised arm reads as a 1-px line against the disc.
User review 2026-10-03: arm raise reads, 02 = night only (the `--elong 80` day variant is a spike option, not a
second shot); **02 locked**. **Next: shot 03 (42 h time-lapse) in a new session.**

## Sprints
0. ✅ Treatment, physics, scaffold.
1. ✅ Look spike: 02 night (1 km ridge), 04 eclipse (28 mm), 14K Jupiter map, polar ground palette (2026-10-02).
2. ✅ Astronaut (EMU #12622 cleaned, look + Breathing Idle retarget approved 2026-10-03): pick a rigged model (show author/licence/preview first), Mixamo clip (user downloads), `retarget.py`,
   turntable still → user approves.
3. Shots 01 → 06: action + Workbench animatic + 3-still Cycles check → locked (one shot per session). 01 ✅ 2026-10-03.
4. Whole-film animatic; score + suit foley cut to it; caption + counter overlay in compile.
5. Overnight batch render (one yes for the list + hours) → compile, `check.mjs`, srt, poster.

## Decisions (locked)
- Format: 1920×1080, 24 fps, picture 1920×804 (2.39:1) rendered, letterboxed at encode (saves ~25 % render time).
- Location: 75° from the sub-Jupiter point → Jupiter centre at 14.8°, lower limb 5.0°, fixed in every shot.
- Site direction (user 2026-10-02): toward Io's north pole → Jupiter due south, bands horizontal, Sun ≤ 15° up,
  up only while Jupiter < half lit; full Jupiter happens at night. Shot Sun positions = `physics.SHOT` elongations.
- Renderer: Cycles for every shot (light is the subject: phase, eclipse, vacuum shadows); Workbench animatics.
- No narration; EN (Cinzel) + 简中 (Noto Serif SC) captions in clip `caps`; 03 counter `+0 h → +42 h`.
- Ground: the site's real polar orange-brown (USGS mosaic) + scattered frost/sulfur patches (user 2026-10-02).
- 02: night (Sun −13°, Jupiter 93 % lit), ridge 1 km out, figures in silhouette; 04: 28 mm from a 40 m rise
  (35 mm leaves no ground) (user 2026-10-02).
- 02 has no plume; the plume umbrella is in 05 (user 2026-10-03, geometry in State).
- Scale cues: distant astronaut (ready-made rigged + Mixamo), code-built lander, boot prints.
- Astronaut = Blend Swap #12622 NASA EMU (user 2026-10-02), gold visor down (the helmet is empty). The helmet is fixed
  to the hard upper torso as on a real EMU: "looking up" (02) is a lean of the upper body, keyed as an additive layer
  on `chest`/`spine` over one Mixamo idle. Plain suit, no flags or mission patches (user 2026-10-03).
- Standalone episode 2; grade matched to 巨物.
- 01 locked (user 2026-10-03): day, Sun elongation 70°; tilt −30° → +14°; lander only as a footpad in frame; prints 0.8 cm;
  one massif on the horizon (right).

## Open technical checks
- Eclipse ring colour/width (Cassini / New Horizons eclipse images) and how it brightens near contact.
- Treatment 04 says "real time compressed ~10×", but its beats (Sun 2° from the limb → contact in 3 s) need ~280×:
  fix in the 04 shot sprint.
- Caption + counter overlay route for Blender frames (kit compile has no overlay for style `blender`; film-local
  ffmpeg drawtext/ASS pass or a canvas overlay, decide in Sprint 4).
- Exposure: AgX can't hold sunlit sulfur and a 6-stop-darker eclipse in one exposure: key `film exposure` per shot
  (04 ramps it up after second contact, "eyes adjust").

## Notes / lessons
- Hubble OPAL maps are 0.1°/px, no sharper than Cassini PIA07782; the 14K Jónsson map is the sharpest global one.
- USGS GeoTIFFs: the pixel-scale tag is positive but rows run south (dlat < 0); planetarymaps.usgs.gov 403s Python's
  default User-Agent.
- macOS numpy (Accelerate) warns "divide by zero in matmul" on large `@` products with valid results; use `* w).sum`.
- 2.39:1 at 135 mm is 15.2° × 6.4° (vertical fov uses the half-height 7.5 mm, not 15 mm): Jupiter is a slice.
- The terrain patch covers only the view sector: a Sun behind or below lights it through the gap. `io_world.io_body`
  (shadow-only curved skirt) closes it; keep it ≤ ~100 km or it shadows the scaled-down Jupiter (1000 km out).
- `world_to_camera_view` in a headless probe needs `view_layer.update()` first (matrices are identity until then).
- Sun elongation 0 puts the Sun behind Jupiter (eclipse): a board lit "at the Sun's highest" rendered black. For a
  sunlit look use elong ±25…60 (Sun 13.6…7.4° up); the Sun is always in the southern half of the sky when up.
- Painting a decal out of a texture: clone neighbouring fabric into colour *and* normal map (a median fill, or a
  colour-only clone, leaves a smooth blank label).
- Retarget: transfer rotations in each character's own frame (source world at the origin ≡ target armature space),
  never the target's world (a turned root flipped the arms up). Align rest poses only for bones within ~60° of
  their twin (Mixamo Hips points up, the EMU hips down: the shortest arc of opposite vectors is undefined and folded
  the legs). The file's thighs didn't inherit the hips' rotation; prep turns inherit on for every bone.
- 2.6x Rigify-style files keep the look in pose bones (here the helmet visors): don't reset every pose bone in a prep.
- Workbench hides camera-invisible objects (the Io-body skirt, the ring shell) automatically (`shot.engine`).
