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
**Sprint 3 · shot 03 locked (user 2026-10-03).** Span (user 2026-10-03): a 42 h day always contains the
noon eclipse, so 03 runs **39 h, eclipse to eclipse, no eclipse inside**, centred on midnight, time rate eased
(`physics.SHOT['03']`, `lapse03(t)` → hours, `lapse03_elong(h)`): 0.6 h/s at both ends, ramps 2 s in / 3 s out, peak
3.95 h/s. Sun from 14.7° W of Jupiter (2 % crescent, lit limb right, 4.9° clear of the limb) → sunset 3.1 s → full
Jupiter 5.8 s → sunrise 8.5 s (inside the caption) → 14.7° E (crescent, lit limb left; 04 starts after). Counter
`[0, 39]` in the clip, eased: compile must read `physics.lapse03` (Sprint 4). `blender/shots/s03_eternity.py`: 20 mm,
tripod 1.5 m, locked, pitch +6.5° (Jupiter 5.6–23.9° in a −14.2…+27.2° frame), **the 01 landing site from 22 m back**
(new `lib/landing.py`: lander, trail, relief, massif moved out of s01; 01 pixel-identical after), lander right of the
disc at az 19°, 24 m: its shadow sweeps. Stars turn about Io's pole (`sky.stars(axis=…)`, keyed `StarTurn`/`StarSmear`,
12 taps → trails over the shutter); Jupiter spins 12.95 h per turn **seen from Io** (3×; GRS on the meridian at
midnight); Cycles motion blur 0.5; Sun disc for the camera (`sky.sun_disc`, true size + radiance) + Fog Glow glare
(`sky.glare`, compositor); exposure −4.5 with a +1.5 EV night lift keyed on Sun elevation (+2 washed Jupiter out).
**Io's shadow transit:** at full Jupiter the scaled scene's real-size ground shadowed the scaled Jupiter (a black
saucer). `jupiter.io_shadow` (opt-in): light linking, a second Sun lights only Jupiter and only a scaled Io (R·k =
4.32 km sphere, sunk 30 m) blocks it → Io's real shadow, a ≈ 0.4° black dot crossing the full disc (~0.6 s).
Animatic (EEVEE, 1.9 s/frame at 50 %; no Jupiter-shine in EEVEE, Cycles has it) `out/03-eternity-animatic.mp4`;
Cycles check `frames/03-eternity-check.png` (0.5 / 3.0 / 5.8 / 8.5 / 11.5 s, 50 %, ≈ 3.5 s/still) → full clip
≈ 288 × ~10 s ≈ 45–50 min. physics: Io sidereal 42.459 h + synodic corrected 42.456 → 42.477 h (table only).
User review 2026-10-03: locked as is (night ground dark at +1.5 EV, black-sky open/close with the Sun beside the
hairline crescent). **Next: shot 04 (eclipse; fix its ~10× vs ~280× time compression) in a new session.**
**Sprint 3 · shot 04 locked (user 2026-10-03).** 20 s version (user 2026-10-03; was 14 s, film ≈ 66 s,
trim 01/03 or not at the whole-film animatic). Time compression fixed by easing, not a constant: `physics.SHOT['04']`
(dur 20, pre 2°, contact 4.0 s, gone 9.0 s), `fit04` fits a log-rate smoothstep from 03's end rate (2160×) to 1× →
619× at 0 s (Sun/stars 1.5°/s), 33× at first contact, 1.4× at second contact, real time from 10.9 s (`lapse04`,
`lapse04_elong`, `rate04`); `sun_limb_sep` / `sun_visible` (oblate limb, uncovered fraction of the 0.1° disc).
`s04_eclipse.py` animated (28 mm, locked, 40 m rise, lake + 22 vents as in the spike): the main Sun's energy keyed by
`sun_visible` with `jupiter.own_sun` (Jupiter lit by its own Sun via light linking, casts no shadow) → Cycles and
EEVEE agree; Sun disc + glare; stars turn about the pole (3 taps), dense (0.8, gain 8) so the black disc reads as a
starless hole after the eyes adjust; Jupiter spins with real time; ring controls now keyable (`_ring`: RingArc,
RingHaze, RingFocus, RingDir; `jupiter.ring_dir`): haze ring from 4° out (the 1 % Lambert crescent alone doesn't read
at day exposure), Sun-side arc from 3° out flaring while the Sun goes, keeps 6 %; exposure −4.5 → 0 EV over
10.5–14.5 s (`ADAPT`). Animatic (EEVEE, 1.9 s/frame at 50 %, rendered before the star change: sparse stars)
`out/04-eclipse-animatic.mp4`; Cycles check `frames/04-eclipse-check.png` (0 / 6.5 / 16 s, 50 %, ≈ 3 s/still).
**Freeze** (`clip.freeze: 9.5`, render.mjs → `--freeze 229`, `shot.freeze`): frames to 9.5 s rendered (228 × ~9 s
≈ 35 min), then one linear EXR (after the glare) shown by an empty Workbench post scene through the same AgX view with
each frame's keyed exposure (478 frames in 5 s; frozen = rendered at PSNR 51 dB in a test). Real renders only.
User review 2026-10-03: locked as is (flat sunlit plain at 0–4 s and night EV 0 accepted). **Next: shot 05 (forever:
rise + pull back, plume umbrella, the Sun's diamond on the limb) in a new session.**
**Sprint 3 · shot 05 locked (user 2026-10-03).** User picks: rise to the height that looks
best → **100 km** (horizon dip 18.6°, bulges ≈ 140 px at 17 mm; 3 km only ~20 px); plume lights with the diamond;
start 5 m from the astronaut (knee-cut); reference points for the dark climb; far ground from real imagery.
`physics.SHOT['05']` + `egress05 / lapse05 / rise05 / lens05 / sun_offset_dir / dip / umbrella`: the cut skips 137 min
of the eclipse; real time to third contact at 5.0 s (Sun el 14.8°, az +10°, west limb), eased to 21× over 2 s, whole
Sun out at 8.0 s; camera holds 1 s, rises log-eased 0.8 m → 100 km by 9 s (5 m at 3 s, 283 m at 5 s, 16 km at 7 s),
29 → 17 mm, disc top held 1° under the frame top, pull-back due north (site 3.8° → 18° below). New `lib/globe.py`:
exact-sphere cap 4–1500 km (`cap`; io_world.terrain's parabola is 2.7 km low at 600 km), `massifs` (scarps over
debris aprons), `far_layer` (km tone from `textures/src/io_far_1km.png` = `tools/maps.py far`: the USGS mosaic at
48° N, lon −90°, a stand-in for the smeared polar site, as map / its mean; noise fallback; Prometheus-type deposit
ring), `egress` (per-point Sun fraction: Jupiter's parallax makes the shadow's 753 km penumbra sweep the ground west →
east at 17 km/s × rate), `hotspots`, `plume` (umbrella volume: shell on z = 1 − ρ², 100 km apex, ring 143 km, at
450 km az −6° so the light reaches it ≈ 2 s after the diamond; bluish forward scatter, colour × egress).
`s05_forever.py`: astronaut (idle) at the end of 01's out-trail, helmet lamps (spots on 'Lamparas'), **the lander's
floodlight on** (from behind the suit was a starless hole), 84 hot cracks 15 m–5 km (bands, size ∝ distance) + 15 hot
paterae 15–650 km; light: near Sun keyed by the site's fraction (near ground, suit, lander), far Sun full with the
per-point fraction (globe, plume), Jupiter's own Sun; Jupiter + ring follow the camera; ground/plume bounce off
(seen from the scaled Jupiter the real-size sunlit ground lit its night side); stars camera-only and their Voronoi
lattice turned (`sky.stars` `camera_only`, `orient`: default off, 03/04 unchanged); the Sun drawn as a ≥ 1.5 px bead
in front of the limb, strength = `sun_visible` × radiance × (true/drawn)² (the true 1-px disc's sliver was missed by
adaptive sampling: no diamond at 6 s). Exposure EV 0 → −4.5 over 5.3–8.5 s. Animatic (EEVEE draft, 1.0 s/frame)
`out/05-forever-animatic.mp4`; Cycles check `frames/05-forever-check.png` (0.5 / 3 / 6 / 9.5 s, 50 %, ≈ 5 s/still +
build). EEVEE shows the plume green (volume artefact; Cycles bluish white). User review 2026-10-03: locked as is
(lander floodlight accepted). **Next: shot 06 (title card) in a new session, then Sprint 4.**
**Sprint 3 · shot 06 (title card) locked (user 2026-10-03).** No Blender: the card is all type, so
`tools/card.mjs` draws it in headless Chrome (kit puppeteer-core, Google Fonts) with 巨物's title type and colours on its
640×360 grid ×3: Cinzel 600 tracked caps, 中文 Noto Serif SC spaced, a two-line JetBrains Mono readout (ZH over EN)
filled from `python3 tools/physics.py --card` (Jupiter 19.6°, 38× the Moon, moves 0°/h, eclipse every 42.48 h, 2.29 h
of dark). Clip `card: { variant }` replaces `shot`; `render.mjs` / `preview.mjs` route it to card.mjs (1 s for 96
frames, full 1920×1080 since it's black; the animatic is the real thing). Timing: black 0–0.4 s, title in 0.4–1.2,
readout 1.1–1.9, both out 2.7–3.5, black to 4.0 (05's fade to black is at compile). User 2026-10-03: IO / 永 恒 kept; most viewers don't know Io, so a small kicker above it: 木 卫 一 over A MOON OF
JUPITER (Noto Serif SC 7 + Cinzel 5.5, dim, fades with the title). Variants: `io` (IO / 永 恒) and
`apeiro` (APEIROPHOBIA / 永 恒 恐 惧 症, as MEGALOPHOBIA / 巨物恐惧症). Strip `frames/06-title-strip.png`, animatic
`out/06-title-animatic.mp4`. The same canvas route can carry the captions + 03 counter in Sprint 4.
**Sprint 3 done. Next: Sprint 4 (whole-film animatic, score + foley cut to it, caption + counter overlay) in a new session.**
**Animatic speed (2026-10-03, side-chat list checked):** `render.mjs --animatic` passes `--draft` → `shot.engine`
(EEVEE: TAA 16, no motion blur). Measured on 05 (11 frames): TAA 16 and volume tiles 8/32 changed nothing (4.2 s/frame);
the cost was EEVEE redrawing the helmet lamps' spot shadow maps of the 1.1 M-vertex ground every frame: lamp shadows
off in draft → 1.0 s/frame. Sprint 4 batch-renderer checklist (not done): resume as opt-in `--resume` (default
re-render; a default resume keeps stale frames after a shot edit; delete 0-byte placeholders first; test 04's freeze
EXR); `use_persistent_data` (likely the biggest Cycles win: static 1 M-vertex grounds re-synced per frame; check keyed
world/material values, light linking, 04's freeze post scene); bounces (`rig.render_settings` keeps eyes' glass values
16/16, caustics on: open Io scenes end paths early, expect < 10 %, A/B on the heaviest shot); `adaptive_threshold`
stays 0.01 for 03/04/05 (1-px stars, eclipse EV lift); **check 04's shrinking bead (4–9 s) for the same sub-pixel
sampling flicker** as 05's diamond. Every speed change: 1 full-res still per shot, A/B PSNR + s/frame. Skill notes
(EEVEE draft, bounce defaults, opt-in resume, A/B method) after those measurements.
**Sprint 4.01 · whole-film animatic (2026-10-03).** `out/io-animatic.mp4`, **65.5 s** (strip
`frames/io-animatic-strip.png`). Joints (user 2026-10-03, after a /cinematic-video-prompt pass): hard cuts everywhere
(01→02 scale cut 24 → 135 mm, day → night; 02→03 cut, the counter starts; 03→04 cut on the slowing time, Sun left of
Jupiter in both), **one dissolve, 04 → 05, 1.5 s on the ring**; head = 1.0 s black (sound first) + 0.5 s fade up;
05's last 1.0 s fades to black, 06 opens on its own black. Ring match: 05 now opens at 04's framing (`SHOT['05']`
lens 29 → **28** mm, disc top 1° → **0.7°** under the frame top, as s04): ring centre (960, 261) and 522 vs 523 px in
both (was 17 px and 3 % off). Film-local `compile.mjs` (replaces the kit wrapper; JOINTS / HEAD / FADE_OUT at the top;
dissolve overlaps real frames: film = Σ clips − 1.5 + 1.0) + `tools/overlay.mjs` (captions + 03 counter in 巨物's
cg-lab type on a transparent canvas → qtrle .mov per clip, overlaid before the joints; counter from `physics.lapse03`
per frame, `+00.0 h` → `+39.0 h`, top-left of the picture). Clip starts → `out/timeline.json` (git-ignored; rerun
`node compile.mjs --animatic`): 01 @ 1.0 · 02 @ 10.0 · 03 @ 21.0 · 04 @ 33.0 · 05 @ 51.5 · 06 @ 61.5, end 65.5.
Animatics refreshed in EEVEE (13.5 min for all four): 05 50 % 4.3 min, 04 50 % 4.8 min (dense stars now), 01 50 %
1.8 min, 02 100 % 2.6 min (14-px astronaut); 03 and 06 unchanged. EEVEE draws 05's plume green (Cycles bluish).
Trims (66 → 60 s target) not decided: judge in motion. **Next: user reviews the animatic → 4.02 (score + suit foley
cut to `out/timeline.json`) in a new session.**
**Sprint 4.02 · score + breath + heartbeat locked (user 2026-10-03).** `audio/music.mjs` (synth,
no samples, seed 20261003) → `audio/build/film.wav` at the film's exact length; `compile.mjs` (animatic and final)
mixes it in: one gain to −16 LUFS + `alimiter` at −2 dB, **not loudnorm** (the eclipse's near-silence gives a
loudness range that flips loudnorm to dynamic mode, which would lift the silence); `--silent` skips it. Layout now in
`tools/timeline.mjs` (HEAD / JOINTS / FADE_OUT + `layout()`), shared by compile and the score; compile asserts both
agree. Physical cue times from `python3 tools/physics.py --sound` (03: the counter's 38 whole hours, sunset 3.098,
full 5.788, sunrise 8.478; 04 contact/gone; 05 contact/full/hold); directing cues in each clip's `sfx`.
**Suit silent, breath only (user 2026-10-03):** the first draft's suit hum (fan + airflow + pump), creaks and weight
shift read as surf (plain band noise swelling every 4–5 s is how 巨物 made its waves) and pulled focus; now the only
human sound is ~9 breaths, each a reaction, with true digital silence between them. **Breaths are recorded
(user 2026-10-03: the synth whispered-vowel breath still read as fake):** two CC0 Freesound files the user downloaded
to `../../_assets/audio/breath/` (mlitty 387620 slow deep breaths, one voice for all but one; drewsimko 682884 shaky
breaths for 01's release; REFERENCES.md, `_assets/index.json`). `music.mjs` TAKES = [source, from, to] cut at the
breath edges (1–6 kHz envelope; inhales bright with no mic pop, exhales with a < 150 Hz pop → high-pass 180 Hz ×2),
afftdn, fades, levelled to one RMS (0.0063 × GS; user 2026-10-03: breath was a little forward); a cue's `take` plays the recording, else the synth `breath()`
fallback with the cue's own options; `far` darkens and lowers. 01's catch is not the Freesound gasp (user: too
theatrical) but the first 0.65 s of mlitty's steepest inhale (65.8 s, 0.27 s rise): a small quick intake.
Schedule: head inhale −0.9 + exhale 1.0 (sound before picture) → 01 catch at 3.5 s as the limb enters, held 2.3 s,
shaky release 6.4 s → 02 drone J-cut −0.6, in 2.2 s with the arm, held, out 6.2 s → 03 no breath (pad turning with
the light: Am9 → Fmaj7 → G6/9-ish → Esus4; a glass tick per counter hour) → 04 one inhale 0.15 s held, Esus swell +
riser to −11 LUFS at first contact, **music cut dead (gated after the reverb)**, silence, three heartbeats growing out of it, **recorded** (Freesound 332819, loudernoises, user-downloaded: one lub-dub cut from the 80 bpm loop, 2.985–3.70 s, TAKES `heart`, no high-pass) on the picture's beats: 9.0 s (second contact, black), 11.75 s (eyes adjusting), 14.5 s (stars up), 2.75 s apart, v 0.6 / 0.8 / 1 (user 2026-10-03: more immersive, slower than 80 bpm) → 05 long
exhale 0.4 s, one faint receding breath 2.9/4.6 s, drone back, diamond rings (A5/E6/A6 glass), chord
blooms to A add9 by the whole Sun (≈ −11), shimmer 7.0 s → fade with the picture, 0.5 s silence → 06 held A4.
`out/io-animatic.mp4`: −16 LUFS, TP −1.9 dBTP, check OK (silences 5.2 +2.3 held breath, 37.0 → 51.9 between the heartbeats: intended). Breath ≈ −19…−21 momentary, music −16…−18, climaxes −11, heartbeats −24 / −21.6 / −19.7 dB RMS, peaks ≤ 0.66 (the synth beat, kept as the
fallback: sub thump at 0.45 + a 100–200 Hz body + a skin tap; the first all-60 Hz beat was the film's sample peak, so the loudness gain
(+7 dB) drove it ~6 dB into the limiter; now +0.9 dB. (Measure peaks in stereo: ffmpeg `-ac 1` sums L+R.)
Levels judged on K-weighted momentary loudness (ffmpeg ebur128), not RMS (the 55 Hz sub dominated RMS and the meter:
drone 0.3 → 0.11). Sprint 5 note: `check.mjs` compares `out/io.mp4` with the kit's film() (66 s, no head / dissolve);
ours is 65.5 s, so it will report "duration off by −0.50 s" (expected).
**Trims: none (user 2026-10-03): the film stays 65.5 s.** Sprint 5 started 2026-10-03 (branch `sprint-5-render`).
User 2026-10-03: captions unchanged, poster = 02 night, **no overnight batch: the user runs each shot by hand**
(`node render.mjs <id> --resume`, any order, as many as fit). **Sprint 5.01 · renderer done (2026-10-03).**
`render.mjs --resume` keeps `frames/<id>/` and skips frames on disk (Blender `use_overwrite` off; 0-byte frames from a
Ctrl-C deleted first; tested: 99 kept, 165 rendered); persistent data on for every real render (`shot.py --persist`).
A/B, 6 full-res frames per shot, 64 spp, off → on: 01 6.5 → 6.0 s (PSNR 93 dB), 02 30.4 → 28.4 (92), 03 7.2 → 5.8
(99), 04 5.4 → 3.8 (107/113), 05 10.6 → 9.5 (57): identical. **02 at 64 spp was 30 s/frame** (the old "7 s" was a
lower-sample still): 32 spp = 15.6 s/frame, 54 dB vs 64, silhouettes unchanged → clip `samples: 32`
(render.mjs reads `C.samples`). 04's bead (8.2–9.0 s, full res): monotonic fade, out at 9.0 s, no flicker. Bounces
and `adaptive_threshold` left as they are (not worth the risk at these times).
Estimates (persist on): 04 ≈ 15–25 min · 01 ≈ 22 · 03 ≈ 30–40 · 05 ≈ 40–50 · 02 ≈ 70 · 06 seconds → ≈ 3–3.5 h.
**Renders (user, 2026-10-03):** 01, 03 (4:2:0, kept: their bright limb is a luma edge, raw = mp4), 05 and 04
(4:4:4, see below) done; 02 rendering. **4:2:0 stepped the eclipse ring:** the 1–2 px orange ring on black lost half its
chroma (blue-grey dashes, steps); raw PNG and 4:4:4 clean → `render.mjs` encodes real renders `yuv444p` (masters; QuickTime
won't play them), 04 re-rendered (frame 200 = raw at 59 dB). A wider Cycles pixel filter (2.0/2.5) killed the Sun bead's
glare: rejected. What remains is a 1-px line on the user's 27" 1080p monitor (81 ppi). **Delivery = 4K** (user
2026-10-03): compile upscales to 3840×2160 lanczos, yuv420p (chroma then at the render's full resolution; preview
`out/04-eclipse-4k-preview.mp4`). compile.mjs still converts to yuv420p at 1080 on input (line ~41): change both.
**Next (new session): 02 lands → compile at 4K, check.mjs, srt, poster (02 night).**

## Sprints
0. ✅ Treatment, physics, scaffold.
1. ✅ Look spike: 02 night (1 km ridge), 04 eclipse (28 mm), 14K Jupiter map, polar ground palette (2026-10-02).
2. ✅ Astronaut (EMU #12622 cleaned, look + Breathing Idle retarget approved 2026-10-03): pick a rigged model (show author/licence/preview first), Mixamo clip (user downloads), `retarget.py`,
   turntable still → user approves.
3. Shots 01 → 06: action + Workbench animatic + 3-still Cycles check → locked (one shot per session). 01 ✅ 02 ✅ 03 ✅ 04 ✅ 05 ✅ 2026-10-03; 06 ✅ (title card, no Blender).
4. 4.01 ✅ whole-film animatic + joints + caption/counter overlay in compile (2026-10-03); 4.02 ✅ score + recorded breath + heartbeat cut to it (2026-10-03).
5. 5.01 ✅ renderer (--resume, persistent data, 02 at 32 spp) 2026-10-03; renders by the user, shot by shot → compile, `check.mjs`, srt, poster (02 night).

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
- 05 locked (user 2026-10-03): rise to 100 km, 28 → 17 mm (was 29; 4.01 ring match with 04); start 5 m from the astronaut; diamond 5.0 s, whole Sun
  8.0 s, caption 5.0–9.4; plume lights after the diamond; vents for the dark climb; far ground = USGS mosaic stand-in
  (48° N) as relative colour over the polar palette; lander floodlight on in the eclipse; EEVEE animatic.
- 06 locked (user 2026-10-03): title card drawn by `tools/card.mjs` (Chrome canvas, 巨物's type), IO / 永 恒 with a
  木 卫 一 / A MOON OF JUPITER kicker above, physics readout from `physics.py --card`; 4 s, black head and tail.
- 03: 39 h, eclipse to eclipse (no eclipse inside), eased rate (user 2026-10-03); EEVEE animatic (light is the beat).
- 04: 20 s, time eased 619× → real time (Sun in at 4 s, gone at 9 s, black to 10.5, eyes adjust to 14.5, heartbeat,
  hold); still tail rendered as one EXR + keyed exposure (user 2026-10-03); EEVEE animatic.
- Scale cues: distant astronaut (ready-made rigged + Mixamo), code-built lander, boot prints.
- Astronaut = Blend Swap #12622 NASA EMU (user 2026-10-02), gold visor down (the helmet is empty). The helmet is fixed
  to the hard upper torso as on a real EMU: "looking up" (02) is a lean of the upper body, keyed as an additive layer
  on `chest`/`spine` over one Mixamo idle. Plain suit, no flags or mission patches (user 2026-10-03).
- Sound (user 2026-10-03): no suit sounds (hum/creaks read as surf); ~9 recorded breaths (CC0 Freesound, `audio/music.mjs`
  TAKES), none in 03; music cut dead at 04's first contact; three recorded heartbeats in 04 at 9.0 / 11.75 / 14.5 s;
  mixed by one gain to −16 LUFS + a −2 dB limiter (no loudnorm) in `compile.mjs`.
- Standalone episode 2; grade matched to 巨物.
- Length: 65.5 s, no trims (user 2026-10-03). Delivery 3840×2160 (4K upscale at compile, yuv420p); clip masters 4:4:4.
- 01 locked (user 2026-10-03): day, Sun elongation 70°; tilt −30° → +14°; lander only as a footpad in frame; prints 0.8 cm;
  one massif on the horizon (right).

## Open technical checks
- Eclipse ring colour/width (Cassini / New Horizons eclipse images) and how it brightens near contact.
- Exposure: AgX can't hold sunlit sulfur and a 6-stop-darker eclipse in one exposure: key `film exposure` per shot
  (04 ramps it up after second contact, "eyes adjust").

## Notes / lessons
- A true-size Sun (0.1° ≈ 1 px) as a sliver is sub-pixel: adaptive sampling stops on a black pixel before a sample
  hits it. Draw the camera Sun ≥ 1.5 px, strength scaled to keep flux, visible fraction keyed from physics (05).
- Real-size ground + scaled-down Jupiter: the ground's bounce light, seen from Jupiter's scaled place, lights its
  night side. Turn off diffuse/glossy visibility of the ground (05). Parallax over hundreds of km is real: Jupiter
  shifts deg(Δ/d), so the eclipse ends at different moments across the ground (`globe.egress`).
- EEVEE: a shadowed spot light redraws its shadow maps of every mesh in range each frame (05: 3.5 s/frame for two
  helmet lamps over a 1.1 M-vertex ground); time an EEVEE draft by elimination over ≥ 10 frames (3 stills mostly
  measure the shader compile).
- EEVEE draft of a Cycles scene: a negative view exposure drops the sub-pixel Sun disc (key the exposure in the
  compositor for EEVEE); Dithered drops a transparent+emission shell (ring material is BLENDED). In skill REALISM.md.
- Scaled-far scenes: near real-size occluders shadow the scaled Jupiter whenever the Sun is opposite it. Fix with
  light linking (Jupiter's own Sun, only a scaled Io as blocker), which also gives Io's real shadow transit.
- Jupiter seen from Io turns in 12.95 h, not 9.925 h (Io orbits the same way). World-shader animation gets no Cycles
  motion blur: smear stars by hand (several rotated lookups over the shutter).
- `Collection.collection_objects` takes an index, not a name, in 5.2.
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
- File size ≠ render cost: 02 (locked camera, static Jupiter and stars, only a 14-px astronaut moving) cost 70 min of
  Cycles for an 848 kB mp4. For a locked shot with a small moving part: render one full plate, then per frame only a
  border region around the mover (`render.use_border`, fixed seed, a margin of a few px for the denoiser) composited
  over it → minutes, not an hour. Check what moves before a long render. Tested on 02 f121 (`shot.py --border
  x0,y0,x1,y1`, 120 px box, 80 px pasted onto f1's plate): 2.7 vs 17.6 s/frame; outside the box ≤ 1/255 (static
  background identical), inside 54 dB (≤ 9/255 on 47 ridge-edge pixels: denoiser, as 32 vs 64 spp). Same only when
  the camera, light, glare and motion blur don't change outside the box (the box must cover shadows/bounce).
