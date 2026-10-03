// Film-local render (picture from Blender, not engine.html): clip → out/<id>.mp4, then its sound via the kit's mix.
// Usage: node render.mjs <id> [--silent] [--samples N] [--pct P] [--look L] [--engine cycles|eevee|workbench] [--animatic] [--keep]
//   The clip file (clips/<id>.js) names its Blender script in `shot`; frames = duration × fps.
//   Frames go to frames/<id>/ (deleted after encoding unless --keep). BLENDER env overrides the app path.
//   --animatic: motion draft → out/<id>-animatic.mp4 (frames/<id>-animatic/), never touches out/<id>.mp4; default
//   --engine workbench --pct 50. Free like previews: run it before any Cycles render.
//   clips/<id>.js `freeze: S` (real renders only): frames from S on come from one EXR + keyed exposure (shot.py freeze).
//   clips/<id>.js `card: {…}` instead of `shot`: a type-only card drawn by tools/card.mjs (headless Chrome), no Blender.
//   --resume: keep frames/<id>/ and skip frames already on disk (stop with Ctrl-C any time, rerun to continue);
//   without it the folder is cleared first. Real renders keep the synced scene between frames (persistent data:
//   8–30 % faster, pixel-identical in the Sprint 5 A/B). clips/<id>.js `samples: N` overrides config.samples.
//   Real renders are encoded 4:4:4 (the 1-px eclipse ring on black breaks into colour steps at 4:2:0); compile makes
//   the delivery. Frames are the 2.39:1 picture (blender/lib/shot.py RES 1920×804); encoding pads them to 1920×1080 (letterbox).
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import { loadClip, rel, config, argv, kitRoot } from '../../_kit/lib/film.mjs';

const BLENDER = process.env.BLENDER ?? '/Applications/Blender.app/Contents/MacOS/Blender';
const A = argv(undefined, ['silent', 'keep', 'animatic', 'resume']);
const anim = A.has('animatic');
const [id] = A.positional();
if (!id) { console.error('usage: node render.mjs <id> [--silent] [--samples N] [--pct P] [--look L] [--engine E] [--animatic] [--keep]'); process.exit(1); }
const C = loadClip(id);
if (C.card) {                                         // title card: type on black, the animatic is the real thing
  execFileSync('node', [rel('tools/card.mjs'), id, '--out', rel(`out/${anim ? `${id}-animatic` : id}.mp4`)], { stdio: 'inherit' });
  process.exit(0);
}
if (!C.shot) { console.error(`clips/${id}.js has no \`shot\` (blender/shots/<file>.py)`); process.exit(1); }
const name = anim ? `${id}-animatic` : id;
const frames = Math.round(C.duration * config.fps), dir = rel(`frames/${name}`);
const resume = A.has('resume') && !anim;
if (!resume) fs.rmSync(dir, { recursive: true, force: true });
else if (fs.existsSync(dir)) for (const f of fs.readdirSync(dir))    // a frame cut off mid-write by Ctrl-C
  if (f.endsWith('.png') && fs.statSync(`${dir}/${f}`).size === 0) fs.rmSync(`${dir}/${f}`);

const opt = (k) => A.opt(k) ?? (anim ? { engine: 'workbench', pct: '50' }[k] : undefined);
const pass = ['samples', 'pct', 'look', 'engine'].flatMap((k) => (opt(k) ? [`--${k}`, opt(k)] : []));
// clip.freeze (s): from that second on, frames are one EXR shown with each frame's exposure (blender/lib/shot.py freeze);
// real renders only, the animatic renders every frame
if (C.freeze && !anim) pass.push('--freeze', String(Math.round(C.freeze * config.fps) + 1));
if (anim) pass.push('--draft', '1');
else pass.push('--persist', '1');
if (resume) pass.push('--resume', '1');                  // EEVEE: 16 TAA samples, no motion blur (shot.engine)
const t0 = Date.now();
const log = execFileSync(BLENDER, ['-b', '--factory-startup', '-P', rel(`blender/shots/${C.shot}`), '--',
  '--frames', String(frames), '--samples', String(A.opt('samples', C.samples ?? config.samples)), ...pass, '--out', dir],
{ encoding: 'utf8', maxBuffer: 1 << 28 });
const err = log.split('\n').filter((l) => /Traceback|Error:/.test(l) && !/Not freed memory/.test(l));   // Blender's exit leak report is harmless
if (err.length) { console.error(err.join('\n')); process.exit(1); }
console.log(log.split('\n').filter((l) => l.startsWith('SHOT')).join('\n'));

fs.mkdirSync(rel('out'), { recursive: true });
execFileSync('ffmpeg', ['-y', '-v', 'error', '-framerate', String(config.fps), '-i', `${dir}/%04d.png`,
  '-vf', 'scale=1920:-2,pad=1920:1080:0:(oh-ih)/2:black', '-c:v', 'libx264', '-preset', 'slow', '-crf', String(config.crf), '-pix_fmt', anim ? 'yuv420p' : 'yuv444p', '-movflags', '+faststart', rel(`out/${name}.mp4`)]);
if (!A.has('keep')) fs.rmSync(dir, { recursive: true, force: true });   // (the freeze EXR goes with the frames)
console.log(`${id}: ${frames} frames → out/${name}.mp4 in ${((Date.now() - t0) / 60000).toFixed(1)} min`);
if (anim && config.soundtrack !== 'none') console.log('animatic: no sound yet (the kit mix writes out/<id>.mp4 only)');
else if (!A.has('silent') && config.soundtrack !== 'none')
  execFileSync('node', [`${kitRoot}/audio/mix.mjs`, id], { stdio: 'inherit', env: { ...process.env, FILM_DIR: rel('') } });
