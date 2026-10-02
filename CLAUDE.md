# Io · 永恒

Episode 2 of the planet series: Jupiter seen from Io. Picture from **Blender 5.2 Cycles, built entirely by Python**
(`blender/`), sound / compile / QC from the shared kit (`../../_kit`). Use the **blender-film** skill.

**Start every session by reading `PROGRESS.md`** (state, decisions, next step). `TREATMENT.md` = story, physics,
clip list, sound. Physics numbers come from `python3 tools/physics.py`; never type a number into a shot that the
script doesn't produce.

## Commands (run from this folder)
```bash
python3 tools/physics.py                       # every physical number (Jupiter size/elevation, light, plumes, curvature)
node preview.mjs <id> 1 5 9 --pct 50           # Cycles stills → frames/<id>-strip.png (free)
node preview.mjs <id> --every 2 --engine workbench
node render.mjs <id> --animatic                # Workbench motion draft → out/<id>-animatic.mp4 (free)
node render.mjs <id>                           # full Cycles clip → out/<id>.mp4   ONLY on the user's explicit yes
node compile.mjs                               # every NN-*.js clip → out/io.mp4
node ../../_kit/bin/check.mjs                  # final QC
node ../../_kit/bin/srt.mjs                    # subtitles → out/io.srt
```

## Working rules
- Renders start only on the user's yes; previews and animatics are free. Renders run as one overnight batch after
  the whole-film animatic.
- Real scale: 1 BU = 1 m near the camera; Jupiter, Sun, plumes and the far horizon at true angular size and
  elevation (far objects may be scaled down toward the camera as long as their angle is exact; say so in the module).
- Jupiter never moves in Io's sky. Its phase and the ground light come from the Sun's direction, never set by hand.
- Picture is rendered 1920×804 (2.39:1); `render.mjs` pads to 1920×1080. Captions and the 03 counter are added at
  compile, not in Blender.
- Kit path is `../../_kit` (the film sits two levels down).
