// Kit config for this film (see ../../_kit/README.md). Picture comes from Blender (blender/), not engine.html:
// clips/NN-*.js hold timing + captions so the kit's audio, compile and QC tools work unchanged.
// Format: 1920×1080, 24 fps; the picture is rendered 1920×804 (2.39:1, blender/lib/shot.py RES), render.mjs letterboxes.
export default {
  title: 'Io · 永恒',
  style: 'blender',
  clipDir: 'clips', global: 'CLIP', param: 'clip',
  film: 'out/io.mp4',
  fps: 24,
  crf: 16,
  samples: 64,          // Cycles samples per frame (+ OIDN denoise); render.mjs --samples overrides
  blackGround: true,    // black sky, an eclipse and fades: check.mjs reports black frames without failing
  soundtrack: 'none',   // no narration; a film-local score + suit foley (Sprint 4) is laid on the compiled film
  subtitles: (A) => (A.caps || []).map(([a, b, en, zh]) => [a, b, `${en}\n${zh}`]),
  narration: null,
};
