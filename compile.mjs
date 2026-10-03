// Film-local compile (Sprint 4.01): every clip in order → the film, with its captions + 03 counter (tools/overlay.mjs)
// and the joints in tools/timeline.mjs, then the score + suit foley (audio/music.mjs, 4.02) under it. The kit's
// compile (plain cuts, no overlay) and the kit's mix (clips end to end, loudnorm) are not used.
// Usage: node compile.mjs [--animatic] [--silent] [--out path]
//   --animatic: out/<id>-animatic.mp4 → out/io-animatic.mp4 (EEVEE / Workbench drafts; 06 is the real card)
// Joints (user 2026-10-03): hard cuts everywhere (vacuum, Apollo-photo plainness; the sound bridges them) except
// one dissolve, 04 → 05: the ring sits on the same pixels in both (05 opens at 04's 28 mm and 0.7° top margin), so
// the world changes under a Jupiter that doesn't move while the cut skips 137 min. The dissolve overlaps real frames
// (04's still hold and 05's hold before the rise), so the film is the sum of the clips − the dissolve + the head.
// Sound: audio/build/film.wav (the film's exact length) → one gain to −16 LUFS + a −2 dB peak limiter (not
// loudnorm: the eclipse's near-silence gives a loudness range it would answer by switching to dynamic mode and
// lifting the silence). Clip start times (film seconds) → out/timeline.json.
import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { root, config, clipIds, loadClip, argv } from '../../_kit/lib/film.mjs';
import { HEAD, JOINTS, FADE_OUT, layout } from './tools/timeline.mjs';

const A = argv(undefined, ['animatic', 'silent']);
const anim = A.has('animatic');
const out = path.resolve(root, A.opt('out', anim ? 'out/io-animatic.mp4' : config.film));
const ids = clipIds();
const files = ids.map((id) => path.join(root, 'out', `${id}${anim ? '-animatic' : ''}.mp4`));
const missing = ids.filter((_, k) => !fs.existsSync(files[k]));
if (missing.length) { console.error(`missing: ${missing.join(', ')} (node render.mjs <id>${anim ? ' --animatic' : ''})`); process.exit(1); }
const fps = config.fps;
const C = ids.map((id) => loadClip(id));
const len = C.map((c) => c.duration);

// caption / counter layers, one per clip that has any (regenerated each time: a few seconds each)
const ov = ids.map((id, k) => {
  if (!(C[k].caps?.length || C[k].counter)) return null;
  const f = path.join(root, 'out', `.overlay-${id}.mov`);
  execFileSync('node', [path.join(root, 'tools/overlay.mjs'), id, '--out', f], { stdio: 'inherit' });
  return f;
});
const inputs = [...files], ovIn = ov.map((f) => (f ? inputs.push(f) - 1 : -1));

const f = [];
ids.forEach((id, k) => {
  let s = `[${k}:v]fps=${fps},scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p,settb=1/${fps}`;
  if (k === 0) s += `,tpad=start_duration=${HEAD.black}:start_mode=add:color=black,fade=t=in:st=${HEAD.black}:d=${HEAD.fade}`;
  if (FADE_OUT[id]) s += `,fade=t=out:st=${(len[k] - FADE_OUT[id]).toFixed(4)}:d=${FADE_OUT[id]}`;
  if (ovIn[k] >= 0) {                                         // the layer fades with its clip only where captions sit
    f.push(`${s}[p${k}]`);
    const pad = k === 0 ? `,tpad=start_duration=${HEAD.black}:start_mode=add:color=black@0` : '';
    f.push(`[${ovIn[k]}:v]format=rgba,settb=1/${fps}${pad}[o${k}]`, `[p${k}][o${k}]overlay=0:0:eof_action=pass:format=auto,format=yuv420p,settb=1/${fps}[c${k}]`);
  } else f.push(`${s}[c${k}]`);
});
let cur = 'c0', curLen = len[0] + HEAD.black;
const starts = [HEAD.black];
for (let k = 1; k < ids.length; k++) {
  const j = JOINTS[ids[k - 1]] ?? { kind: 'cut' };
  if (j.kind === 'dissolve') {
    const off = curLen - j.d / fps;
    f.push(`[${cur}][c${k}]xfade=transition=fade:duration=${(j.d / fps).toFixed(4)}:offset=${off.toFixed(4)}[j${k}]`);
    starts.push(off);
    curLen = off + len[k];
  } else {
    f.push(`[${cur}][c${k}]concat=n=2:v=1:a=0,settb=1/${fps}[j${k}]`);   // concat resets the timebase; xfade wants equal ones
    starts.push(curLen);
    curLen += len[k];
  }
  cur = `j${k}`;
}

const tmp = path.join(path.dirname(out), `.${path.basename(out)}`);
execFileSync('ffmpeg', ['-y', '-v', 'error', ...inputs.flatMap((c) => ['-i', c]), '-filter_complex', f.join(';'),
  '-map', `[${cur}]`, '-c:v', 'libx264', '-preset', 'medium', '-crf', String(config.crf), '-pix_fmt', 'yuv420p',
  '-r', String(fps), '-movflags', '+faststart', tmp], { stdio: 'inherit' });
fs.renameSync(tmp, out);
ov.forEach((o) => o && fs.rmSync(o, { force: true }));
let dur = +execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], { encoding: 'utf8' });
const L = layout();
L.clips.forEach((c, k) => { if (Math.abs(c.start - starts[k]) > 1e-3) throw new Error(`${c.id}: layout ${c.start} ≠ compile ${starts[k]}`); });
const timeline = ids.map((id, k) => ({ id, start: +starts[k].toFixed(3), duration: len[k], joint_out: JOINTS[id]?.kind ?? (k < ids.length - 1 ? 'cut' : 'end') }));
if (!A.opt('out')) fs.writeFileSync(path.join(root, 'out/timeline.json'), `${JSON.stringify({ head: HEAD, timeline, total: +dur.toFixed(3) }, null, 1)}\n`);
console.log(timeline.map((c) => `${c.id} @ ${c.start.toFixed(2)} s`).join(' · '));
console.log(`${ids.length} clips → ${path.relative(root, out)}, ${dur.toFixed(2)} s`);

if (!A.has('silent') && fs.existsSync(path.join(root, 'audio/music.mjs'))) {
  const wav = path.join(root, 'audio/build/film.wav');
  execFileSync('node', [path.join(root, 'audio/music.mjs')], { cwd: root, stdio: 'inherit' });
  const e = spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-i', wav, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'], { encoding: 'utf8' }).stderr;
  const m = JSON.parse(e.slice(e.lastIndexOf('{'), e.lastIndexOf('}') + 1)), gain = -16 - +m.input_i;
  const tmpA = path.join(path.dirname(out), `.a-${path.basename(out)}`);
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', out, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
    '-af', `volume=${gain.toFixed(2)}dB,alimiter=limit=${(10 ** (-2 / 20)).toFixed(4)}:attack=2:release=60:level=0,aresample=48000`,
    '-c:a', 'aac', '-b:a', '192k', '-t', dur.toFixed(3), '-movflags', '+faststart', tmpA], { stdio: 'inherit' });
  fs.renameSync(tmpA, out);
  console.log(`sound: ${m.input_i} LUFS ${gain >= 0 ? '+' : ''}${gain.toFixed(1)} dB → −16, limited at −2 dB → ${path.relative(root, out)}`);
}
