# Io · 永恒 (Eternity): Treatment

Episode 2 of the planet series (恐惧 / Fear), after *Megalophobia · 巨物* (`../imagnation`). Standalone film.

## 1. Brief (confirmed 2026-10-02)
- ~60 s, 24 fps, 1920×1080 with a 2.39:1 letterbox (picture rendered 1920×804), grade matched to 巨物 (AgX, grain,
  vignette). Picture: Blender 5.2 Cycles from Python (blender-film skill); Workbench/EEVEE animatics.
- No narration. 4–5 captions, English (Cinzel caps) over 简体中文 (Noto Serif SC), as in 巨物.
- Scale cues: a distant astronaut (ready-made rigged suit + one Mixamo idle/head-turn clip, retargeted by script),
  a code-built lander, a trail of boot prints. The astronaut is only ever small (02, 05).
- 03 time-lapse carries a small corner counter `+0 h → +42 h` in 巨物's readout style, added at compile.
- Everything is real physics (table §3); nothing needs 巨物's "dream time".

## 2. Logline and arc
On Io, Jupiter never comes for you. It is already there, a fifth of the sky, and it will be there forever.
- **Hook (01):** ground level, boot prints in sulfur frost; tilt up into a black sky with stars by day, and the
  lower limb of something enormous enters the frame and doesn't stop.
- **Scale (02):** long lens: a tiny astronaut and lander on a ridge, mountains, a 300 km plume umbrella rising
  behind, and Jupiter behind all of it, wider than the frame.
- **Eternity (03):** locked-off time-lapse over one Io day (42 h): stars, Sun and shadows wheel; Jupiter's phase
  runs full → half → crescent and the Great Red Spot rolls past, but **Jupiter itself never moves**.
- **Peak (04):** eclipse. The crescent thins, the Sun touches the limb and is gone: a black disc ringed in red,
  the ground goes dark, lava lakes and vents glow, the stars flood in. Near-silence, one heartbeat.
- **Ending (05):** rise and pull back from the astronaut to the curve of Io under the black disc; the Sun returns
  as a diamond on the limb. "Every 42 hours. Forever." Title.
- **Native move at the peak:** nothing moves. The fear is a camera that holds still on a thing that never will.
- **Opposite of 巨物:** there the giant approached (countdown, ending); here it is fixed (no ending at all).

## 3. Physics (`python3 tools/physics.py`)
| fact | value |
|---|---|
| Jupiter angular diameter | **19.6°** equatorial, 18.3° polar (38× the Moon from Earth) |
| Jupiter's place in the sky | fixed (Io is tidally locked); elevation set by where you stand: 60° from the sub-Jupiter point → centre 29.8°, 70° → 19.8°, **75° → 14.8° (lower limb 5.0°, our location)**, 80° → limb on the horizon |
| Sun | 0.10° wide, 50.3 W/m² = 1/27 of Earth; moves 8.48°/h across Io's sky (stars likewise) |
| Phase ↔ ground light | Sun 90° from Jupiter → half-Jupiter, ground sunlit · Sun near Jupiter → crescent · Sun behind → **eclipse** · Sun opposite (below our horizon) → full Jupiter, **ground lit only by Jupiter-shine: 0.78 W/m² = 1.6 % of sunlight (6 stops down), ≈ 290× full moonlight** |
| Eclipse | every 42.46 h, lasts 2.29 h (142 984 km shadow at 17.3 km/s); Jupiter = black disc + thin orange-red refracted ring |
| Jupiter rotation | 9.925 h; Great Red Spot 2.2° across, crosses the disc in ≈ 5 h |
| Gravity | 1.80 m/s² = 0.18 g |
| Plumes | 300 km: vent 962 m/s, 22 min flight; 400 km: 1085 m/s, 26 min; ballistic umbrella, sharp edges (no air) |
| Curvature | R = 1821.6 km; horizon at 2 m eye height 2.7 km; 300 km plume at 500 km: 71 km hidden, top at 21°; at 300 km: top at 38° |
| Mountains | Boösaule Montes ~17 km: at 100 km top at 8.0°, at 200 km 1.7° |
| No air | no sky colour, no haze, no sound outside the suit; shadows razor-sharp |

**Jupiter on screen** (1920 px wide, 36 mm sensor): 24 mm 442 px · 35 mm 645 px · 50 mm 922 px · 85 mm 1567 px ·
135 mm 2488 px. The picture is 804 px tall, so the **whole disc only fits at ≤ ~35 mm**; at 50 mm and longer
Jupiter is a wall with no edges, which is the megalophobia image (02).

## 4. Benchmark
- *2001: A Space Odyssey* (Jupiter and beyond), Cassini and Juno imagery, New Horizons' Io/Tvashtar plume frames,
  Apollo surface photography (hard light, black sky, no haze). **Learn:** stillness, vacuum light, scale by
  the human figure. **Don't take:** shots, the monolith, any spacecraft design (the lander is ours).
- Jupiter is the real Jupiter (public-domain map, §7). Io's surface is procedural, coloured from Galileo mosaics.

## 5. Clip list (≈ 60 s; final times after the whole-film animatic)
| # | clip | dur | lens / camera | action | caption |
|---|---|---:|---|---|---|
| 01 | horizon | 9 s | 24 mm, eye 1.6 m, slow tilt −30° → +14° | prints and a lander foot in frost → black starry sky → Jupiter's lower limb enters, ends filling the upper third | IO · 木卫一 |
| 02 | scale | 11 s | 135 mm, locked, 1.5 km from the ridge | astronaut (idle, head turns up) + lander on a ridge; Jupiter (half-lit) wider than the frame behind; a plume umbrella rises at the left | JUPITER · 19° OF SKY / 它占据五分之一个天空 |
| 03 | eternity | 12 s | 20 mm, locked, wide | 42 h in 12 s: Sun + stars wheel, shadows sweep, phase full → half → crescent, GRS rolls past; Jupiter still; counter +0 h → +42 h | IT NEVER RISES. IT NEVER SETS. / 它不升起，也不落下 |
| 04 | eclipse | 14 s | 35 mm, locked, whole disc in frame | real time compressed ~10×: crescent thins, Sun meets the limb, gone → black disc + red ring, ground dark, Loki-type lava glows, stars bloom | — (silence) |
| 05 | forever | 10 s | 35 → 24 mm, rise + pull back 2 m → 3 km | astronaut → plain → the curve of Io under the black disc; the Sun's diamond on the limb; fade to black | EVERY 42 HOURS. FOREVER. / 每 42 小时，永远 |
| 06 | title | 4 s | card | IO · 永恒 on black | — |

## 6. Beat sheet (key clip 04)
0.0 crescent a hair-thin arc, Sun 2° from the limb, long shadows · 3.0 Sun touches the limb, the arc flares ·
5.0 Sun gone: ring appears red-orange, ground drops 6 stops · 6.0–9.0 eyes adjust (exposure ramps up): stars
bloom, vents and a lava lake glow on the plain, the ring's colour steadies · 9.0 one heartbeat · 9.0–14.0 hold.

## 7. Assets (log every download in REFERENCES.md; files in the shared `../../_assets/`)
- Jupiter global map: NASA/JPL Cassini PIA07782 (public domain); Hubble OPAL map if 135 mm needs more detail.
- Io colour reference: USGS Galileo/Voyager global mosaic (public domain), palette only.
- Astronaut: rigged suit model (Blend Swap → Sketchfab, shown to the user first) + Mixamo clip (user downloads).
- Stars: procedural, or a public-domain star map (Gaia/Tycho-based).

## 8. Sound design
| clip | ambience | foley (through the suit) | music | silence |
|---|---|---|---|---|
| 01 | suit hum, faint fan | breath, boot crunch felt not heard | — | — |
| 02 | suit hum | slow breath; a low thud through the ground as the plume vents | sub drone enters | — |
| 03 | suit hum | breath sped up with time (ticks) | drone + slow pulse, one chord per Io "hour" | — |
| 04 | hum fades | breath held | drone drops out at contact | **near-silence 5–9 s**, then one heartbeat |
| 05 | hum returns | breath out | the chord returns with the Sun's diamond, resolves | before the title |
