# Io · 永恒 (Eternity): Treatment

Episode 2 of the planet series (恐惧 / Fear), after *Megalophobia · 巨物* (`../imagnation`). Standalone film.

## 1. Brief (confirmed 2026-10-02)
- ~60 s, 24 fps, 1920×1080 with a 2.39:1 letterbox (picture rendered 1920×804), grade matched to 巨物 (AgX, grain,
  vignette). Picture: Blender 5.2 Cycles from Python (blender-film skill); Workbench/EEVEE animatics.
- No narration. 4–5 captions, English (Cinzel caps) over 简体中文 (Noto Serif SC), as in 巨物.
- Scale cues: a distant astronaut (ready-made rigged suit + one Mixamo idle/head-turn clip, retargeted by script),
  a code-built lander, a trail of boot prints. The astronaut is only ever small (02, 05).
- 03 time-lapse carries a small corner counter `+0 h → +39 h` (eased, follows `physics.lapse03`) in 巨物's readout style, added at compile.
- Everything is real physics (table §3); nothing needs 巨物's "dream time".

## 2. Logline and arc
On Io, Jupiter never comes for you. It is already there, a fifth of the sky, and it will be there forever.
- **Hook (01):** ground level, boot prints in sulfur frost; tilt up into a black sky with stars by day, and the
  lower limb of something enormous enters the frame and doesn't stop.
- **Scale (02):** long lens: a tiny astronaut and lander on a ridge, mountains, and Jupiter behind all of it, wider than the frame.
- **Eternity (03):** locked-off time-lapse over 39 h, from just after one eclipse to just before the next (no
  eclipse inside; user 2026-10-03): stars, Sun and shadows wheel; Jupiter's phase runs crescent → full → crescent and the Great Red Spot rolls past, but **Jupiter itself never moves**.
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
| Site (user 2026-10-02) | 75° from the sub-Jupiter point **toward Io's north pole** (lat 75° N): Jupiter due south, bands horizontal; the Sun circles low (≤ 15°), is up only while Jupiter is < half lit, and the eclipse is at local noon. Sun place/phase/light per elongation: `physics.py` site rows |
| Jupiter's place in the sky | fixed (Io is tidally locked); elevation set by where you stand: 60° from the sub-Jupiter point → centre 29.8°, 70° → 19.8°, **75° → 14.8° (lower limb 5.0°, our location)**, 80° → limb on the horizon |
| Sun | 0.10° wide, 50.3 W/m² = 1/27 of Earth; moves 8.48°/h across Io's sky (stars likewise) |
| Phase ↔ ground light | Sun 90° from Jupiter → half-Jupiter, ground sunlit · Sun near Jupiter → crescent · Sun behind → **eclipse** · Sun opposite (below our horizon) → full Jupiter, **ground lit only by Jupiter-shine: 0.78 W/m² = 1.6 % of sunlight (6 stops down), ≈ 290× full moonlight** |
| Eclipse | every 42.48 h, lasts 2.29 h (142 984 km shadow at 17.3 km/s); Jupiter = black disc + thin orange-red refracted ring |
| Jupiter rotation | 9.925 h inertial, **12.95 h seen from Io** (Io follows it round); Great Red Spot 2.2° across, crosses the disc in ≈ 6.5 h |
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

## 5. Clip list (≈ 66 s with the 20 s 04; trim 01 / 03 or not at the whole-film animatic)
| # | clip | dur | lens / camera | action | caption |
|---|---|---:|---|---|---|
| 01 | horizon | 9 s | 24 mm, eye 1.6 m, slow tilt −30° → +14° | prints and a lander foot in frost → black starry sky → Jupiter's lower limb enters, ends filling the upper third | IO · 木卫一 |
| 02 | scale | 11 s | 135 mm, locked, 1 km from the ridge | night (Sun 13° down): astronaut (idle, leans back, raises an arm to Jupiter) + lander in silhouette on a ridge; Jupiter (93 % lit) wider than the frame behind (plume moved to 05, 2026-10-03) | JUPITER · 19° OF SKY / 它占据五分之一个天空 |
| 03 | eternity | 12 s | 20 mm, locked, wide, the 01 site from 22 m back | 39 h in 12 s, eased (0.6 → 4 → 0.6 h/s): Sun just off the right limb (2 % crescent) → sets 3.1 s → night, full Jupiter 5.8 s (GRS on the meridian) → rises 8.5 s → nearing the left limb; stars wheel, the lander's shadow sweeps, Jupiter turns 3×; Jupiter still; counter +0 h → +39 h | IT NEVER RISES. IT NEVER SETS. / 它不升起，也不落下 |
| 04 | eclipse | 20 s | 28 mm, locked, whole disc in frame, from a 40 m rise | time slows from 619× to real time (`physics.lapse04`): the Sun glides into the limb (4 s), is swallowed as a shrinking bead (4–9 s), gone → black, wait → eyes adjust: stars flood in round a starless disc, red ring, lava glows; still from 10.9 s | — (silence) |
| 05 | forever | 10 s | 28 → 17 mm (opens on 04's framing: ring match), rise + pull back 0.8 m → 100 km (log-eased, 1–9 s; user 2026-10-03) | the cut skips 137 min of the eclipse: astronaut in the dark (helmet lamps) → plain, hot spots → the curve of Io (horizon dip 18.6°) under the black disc; third contact 5.0 s: the Sun's diamond on the west limb, the light sweeps the ground west → east (parallax), the plume umbrella under the disc lights ≈ 2 s later, backlit; fade to black | EVERY 42 HOURS. FOREVER. / 每 42 小时，永远 |
| 06 | title | 4 s | card (`tools/card.mjs`, no Blender) | 木卫一 · A MOON OF JUPITER over IO · 永恒 + physics readout on black | — |

## 6. Beat sheet (key clip 04, 20 s, user 2026-10-03)
| t (s) | rate | picture | exposure | sound |
|---|---|---|---|---|
| 0.0–4.0 slide in | 619× → 33× | the Sun 2° off the left limb, glare, gliding toward Jupiter and visibly slowing; no stars (day exposure); hairline limb; plain backlit, shadows toward the camera | −4.5 EV | suit hum fades, breath held |
| 4.0 first contact | 33× | the Sun's edge touches the limb, the red arc on the left lights | — | drone cuts |
| 4.0–9.0 swallowed | 33× → 1.4× | the Sun shrinks to a bead on the limb, ever slower; the glare closes; the ground dims through the penumbra (main Sun keyed by `sun_visible`) | −4.5 EV | near-silence |
| 9.0 second contact | 1.4× | the Sun is gone: near black, a thread of dark red arc, a few lava points | −4.5 EV | silence |
| 9.0–10.5 black | → 1× | nothing to see: the audience waits in the dark | −4.5 EV | silence |
| 10.5–14.5 eyes adjust | 1× | exposure climbs: stars flood the whole frame except a 19.6° hole, the black disc shows by its missing stars; the ring steadies; lava lake and vents come up | −4.5 → ~0 EV (set on stills) | silence |
| 14.5 | 1× | nothing moves | — | one heartbeat |
| 14.5–20.0 hold | 1× | nothing moves → cut to 05 | held | silence |

Time: log-rate eased (smoothstep) from 03's end rate (2160×) to 1×, fit by `physics.fit04` to the Sun 2° off the
limb at 0 s, first contact 4.0 s, second contact 9.0 s (0–4 s covers 850 s real, 4–9 s the 43.5 s the disc takes to
go). A constant ~10× can't reach contact (2° is 14 min real); a constant 280× would drift the stars 6° in the hold.
Render: frames up to 9.5 s one by one (228 × ~9 s ≈ 35 min); from 9.5 s one linear EXR shown with each frame's
exposure (`clip.freeze`, `shot.freeze`: stars drift ≤ 1 px, the lava is static), grain added at compile.

## 7. Assets (log every download in REFERENCES.md; files in the shared `../../_assets/`)
- Jupiter global map: NASA/JPL Cassini PIA07782 (public domain); Hubble OPAL map if 135 mm needs more detail.
- Io colour reference: USGS Galileo/Voyager global mosaic (public domain), palette only.
- Astronaut: rigged suit model (Blend Swap → Sketchfab, shown to the user first) + Mixamo clip (user downloads).
- Stars: procedural, or a public-domain star map (Gaia/Tycho-based).

## 8. Sound design
| clip | ambience | foley (through the suit) | music | silence |
|---|---|---|---|---|
| 01 | suit hum, faint fan | breath, boot crunch felt not heard | — | — |
| 02 | suit hum | slow breath; a suit creak as the arm rises | sub drone enters | — |
| 03 | suit hum | breath sped up with time (ticks) | drone + slow pulse, one chord per Io "hour" | — |
| 04 | hum fades (0–4 s) | breath held | drone cuts at first contact (4.0 s) | **near-silence 4–14.5 s**, one heartbeat at 14.5 s, silence to the cut |
| 05 | hum returns | breath out | the chord returns with the Sun's diamond, resolves | before the title |
