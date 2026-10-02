// Film-local preview (Blender stills, low res): frames at chosen times → one grid PNG, frames/<id>-strip.png.
// Usage: node preview.mjs <id> <t…> | --every S   [--pct 25] [--samples 24] [--cols 3] [--look L] [--engine eevee]
//        [--x k=v,k=v]   shot-specific options, passed as --k v (e.g. --x elong=150,exposure=-2.5)
//        node preview.mjs film [--at 0.5]           contact sheet, one frame per film clip (from out/<id>.mp4 renders)
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import { loadClip, rel, config, argv, film } from '../../_kit/lib/film.mjs';

const BLENDER = process.env.BLENDER ?? '/Applications/Blender.app/Contents/MacOS/Blender';
const A = argv();
const [id, ...ts] = A.positional();
const cols = +A.opt('cols', 3);
const grid = (files, out) => {
  const n = files.length, c = Math.min(cols, n), r = Math.ceil(n / c);
  const pad = [...files]; while (pad.length < c * r) pad.push(files[0]);          // xstack needs a full grid
  const layout = pad.map((_, k) => `${k % c === 0 ? '0' : Array.from({ length: k % c }, () => 'w0').join('+')}_${Math.floor(k / c) === 0 ? '0' : Array.from({ length: Math.floor(k / c) }, () => 'h0').join('+')}`).join('|');
  execFileSync('ffmpeg', ['-y', '-v', 'error', ...pad.flatMap((f) => ['-i', f]),
    '-filter_complex', pad.length > 1 ? `xstack=inputs=${pad.length}:layout=${layout}` : 'null', '-frames:v', '1', '-update', '1', out]);
  console.log(`${n} frames → ${out.replace(rel(''), '')}`);
};

if (id === 'film') {
  const at = +A.opt('at', 0.5), files = [];
  for (const s of film().clips) {
    const f = rel(`frames/.sheet-${s.id}.png`), v = rel(`out/${s.id}.mp4`);
    if (!fs.existsSync(v)) { console.log(`skip ${s.id} (no render)`); continue; }
    execFileSync('ffmpeg', ['-y', '-v', 'error', '-ss', String(s.duration * at), '-i', v, '-frames:v', '1', '-vf', 'scale=640:-2', f]);
    files.push(f);
  }
  grid(files, rel('frames/film-sheet.png'));
  process.exit(0);
}

const C = loadClip(id);
if (C.card) {                                         // title card (tools/card.mjs): stills from Chrome, no Blender
  const times = (A.opt('every') ? Array.from({ length: Math.floor(C.duration / +A.opt('every')) + 1 }, (_, k) => k * +A.opt('every')) : ts.map(Number));
  execFileSync('node', [rel('tools/card.mjs'), id, '--stills', times.join(','), ...(A.opt('x') ? ['--variant', A.opt('x').replace('variant=', '')] : [])], { stdio: 'inherit' });
  grid(times.map((t) => rel(`frames/${id}-t${t.toFixed(2)}.png`)), rel(`frames/${id}-strip.png`));
  process.exit(0);
}
if (!C.shot) { console.error(`clips/${id}.js has no \`shot\``); process.exit(1); }
const every = A.opt('every');
const times = every ? Array.from({ length: Math.floor(C.duration / +every) + 1 }, (_, k) => k * +every) : ts.map(Number);
if (!times.length) { console.error('give times (s) or --every S'); process.exit(1); }
const fr = times.map((t) => Math.min(Math.round(C.duration * config.fps), Math.max(1, Math.round(t * config.fps) + 1)));
const pass = ['look', 'engine'].flatMap((k) => (A.opt(k) ? [`--${k}`, A.opt(k)] : []))
  .concat(String(A.opt('x', '')).split(',').filter(Boolean).flatMap((kv) => { const [k, ...v] = kv.split('='); return [`--${k}`, v.join('=')]; }));
const log = execFileSync(BLENDER, ['-b', '--factory-startup', '-P', rel(`blender/shots/${C.shot}`), '--',
  '--frames', String(Math.round(C.duration * config.fps)), '--samples', A.opt('samples', '24'), '--pct', A.opt('pct', '25'),
  ...pass, '--id', id, '--stills', fr.join(','), '--stills-dir', rel('frames')], { encoding: 'utf8', maxBuffer: 1 << 28 });
const err = log.split('\n').filter((l) => /Traceback|Error:/.test(l) && !/Not freed memory/.test(l));   // Blender's exit leak report is harmless
if (err.length) { console.error(err.join('\n')); process.exit(1); }
console.log(log.split('\n').filter((l) => /^(SHOT|NOTE)/.test(l)).join('\n'));
grid(fr.map((f) => rel(`frames/${id}-f${String(f).padStart(4, '0')}.png`)), rel(`frames/${id}-strip.png`));
