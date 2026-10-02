# References and downloaded assets

Every downloaded file: URL, author, licence, local path (shared library `../../_assets/`), which shot uses it.

| asset | source | author | licence | path | used in |
|---|---|---|---|---|---|
| Jupiter global map, Cassini 2000 (PIA07782), 3601×1801 cylindrical | https://assets.science.nasa.gov/content/dam/science/psd/photojournal/pia/pia07/pia07782/PIA07782.tif | NASA/JPL/Space Science Institute | public domain | `../../_assets/textures/jupiter/PIA07782.png` (+ .tif) | `blender/lib/jupiter.py` (every shot) |
| Jupiter global map, Cassini + Juno poles, 14400×7200 (Björn Jónsson 2018) | https://www.planetary.org/space-images/merged-cassini-and-juno | NASA/JPL-Caltech/SSI/SwRI/MSSS/ASI/INAF/JIRAM/Björn Jónsson | credit; private non-commercial | `../../_assets/textures/jupiter/jupiter_map_css_plus_juno_bj.png` | `blender/lib/jupiter.py` (default) |
| Io colour-merged global mosaic 1 km (Galileo SSI + Voyager) | https://astrogeology.usgs.gov/search/map/io_galileo_ssi_voyager_color_merged_global_mosaic_1km | USGS Astrogeology / PDS | public domain | `../../_assets/textures/io/Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_1km.tif` → `blender/textures/src/io_site_1km.png` (`tools/maps.py io`) | site colours |
| Galileo Io close-ups PIA02562, 02533, 02507, 02566, 02568, 02586, 02545 | https://photojournal.jpl.nasa.gov (assets.science.nasa.gov/…/PIAxxxxx.tif) | NASA/JPL/University of Arizona | public domain | `../../_assets/textures/io/galileo/` | reference, detail masks |
| Astronaut, NASA EMU suit, rigged (Blend Swap #12622), .blend 2.6x | https://blendswap.com/blend/12622 | jgilhutton (Juan Ignacio) | CC-BY 4.0: credit in the end card | `../../_assets/models/astronaut-emu-12622/Astronauta.blend` → `emu_clean.blend` (`tools/prep_astronaut.py`) | `blender/lib/astronaut.py` (02, 05) |
| Mixamo "Breathing Idle" (FBX, without skin, 30 fps, 9.93 s) | https://www.mixamo.com | Adobe Mixamo | Mixamo terms (royalty-free in projects) | `../../_assets/mocap/Breathing Idle.fbx` | `blender/lib/retarget.py` (02, 05) |
