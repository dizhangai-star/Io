# Io · 永恒: progress

## State (2026-10-02)
**Sprint 1 (look spike) built, waiting for the user's look approval.** Stills in `frames/spike/` (sheet.png):
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
**Next:** user decides the ground's colour direction (real polar orange-brown vs iconic yellow; how to use the Galileo
close-ups), then wire it into `io_world.surface`; then Sprint 2 (astronaut).

## Sprints
0. ✅ Treatment, physics, scaffold.
1. Look spike: 2 stills (02, 04) → user approves the look. (built 2026-10-02, awaiting approval)
2. Astronaut: pick a rigged model (show author/licence/preview first), Mixamo clip (user downloads), `retarget.py`,
   turntable still → user approves.
3. Shots 01 → 06: action + Workbench animatic + 3-still Cycles check → locked (one shot per session).
4. Whole-film animatic; score + suit foley cut to it; caption + counter overlay in compile.
5. Overnight batch render (one yes for the list + hours) → compile, `check.mjs`, srt, poster.

## Decisions (locked)
- Format: 1920×1080, 24 fps, picture 1920×804 (2.39:1) rendered, letterboxed at encode (saves ~25 % render time).
- Location: 75° from the sub-Jupiter point → Jupiter centre at 14.8°, lower limb 5.0°, fixed in every shot.
- Site direction (user 2026-10-02): toward Io's north pole → Jupiter due south, bands horizontal, Sun ≤ 15° up,
  up only while Jupiter < half lit; full Jupiter happens at night. Shot Sun positions = `physics.SHOT` elongations.
- Renderer: Cycles for every shot (light is the subject: phase, eclipse, vacuum shadows); Workbench animatics.
- No narration; EN (Cinzel) + 简中 (Noto Serif SC) captions in clip `caps`; 03 counter `+0 h → +42 h`.
- 02: night (Sun −13°, Jupiter 93 % lit), ridge 1 km out, figures in silhouette; 04: 28 mm from a 40 m rise
  (35 mm leaves no ground) (user 2026-10-02).
- Scale cues: distant astronaut (ready-made rigged + Mixamo), code-built lander, boot prints.
- Standalone episode 2; grade matched to 巨物.

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
- Workbench hides camera-invisible objects (the Io-body skirt, the ring shell) automatically (`shot.engine`).
