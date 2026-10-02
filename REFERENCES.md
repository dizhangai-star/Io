# References and downloaded assets

Every downloaded file: URL, author, licence, local path (shared library `../../_assets/`), which shot uses it.

| asset | source | author | licence | path | used in |
|---|---|---|---|---|---|
| Jupiter global map, Cassini 2000 (PIA07782), 3601×1801 cylindrical | https://assets.science.nasa.gov/content/dam/science/psd/photojournal/pia/pia07/pia07782/PIA07782.tif | NASA/JPL/Space Science Institute | public domain | `../../_assets/textures/jupiter/PIA07782.png` (+ .tif) | `blender/lib/jupiter.py` (every shot) |
| Jupiter global map, Cassini + Juno poles, 14400×7200 (Björn Jónsson 2018) | https://www.planetary.org/space-images/merged-cassini-and-juno | NASA/JPL-Caltech/SSI/SwRI/MSSS/ASI/INAF/JIRAM/Björn Jónsson | credit; private non-commercial | `../../_assets/textures/jupiter/jupiter_map_css_plus_juno_bj.png` | `blender/lib/jupiter.py` (default) |
| Io colour-merged global mosaic 1 km (Galileo SSI + Voyager) | https://astrogeology.usgs.gov/search/map/io_galileo_ssi_voyager_color_merged_global_mosaic_1km | USGS Astrogeology / PDS | public domain | `../../_assets/textures/io/Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_1km.tif` → `blender/textures/src/io_site_1km.png` (`tools/maps.py io`) | site colours |
| Galileo Io close-ups PIA02562, 02533, 02507, 02566, 02568, 02586, 02545 | https://photojournal.jpl.nasa.gov (assets.science.nasa.gov/…/PIAxxxxx.tif) | NASA/JPL/University of Arizona | public domain | `../../_assets/textures/io/galileo/` | reference, detail masks |

Planned: a sharper Jupiter map for 135 mm (Hubble OPAL) if the Cassini map is judged too soft; Io colour reference (USGS
Galileo/Voyager mosaic, public domain), astronaut rigged model (Blend Swap/Sketchfab, licence to be checked),
Mixamo idle/head-turn clip (user downloads).
