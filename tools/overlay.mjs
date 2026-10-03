// Film-local caption + counter layer (Sprint 4.01): a clip's `caps` and 03's `counter` drawn in headless Chrome with
// 巨物's overlay type (cg-lab: Cinzel caps over 中文 in the lower letterbox bar, a JetBrains Mono readout top-left of
// the picture), on a transparent 1920×1080 canvas → a qtrle .mov that compile.mjs lays over the clip. The ffmpeg here
// has no drawtext, and this keeps the captions in the series' type.
// Usage: node tools/overlay.mjs <id> [--out out/.overlay-<id>.mov] [--stills t1,t2,… (→ frames/<id>-overlay-tNN.png)]
//   Counter hours per frame come from physics.lapse03 (eased), never from a straight line.
//   Logical units are 巨物's 640×360 grid (letterbox bars 46 = 138 px: 1080 − 804 over 2), drawn ×3.
import { execFileSync, spawn } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { loadClip, rel, config, argv, chrome, kitRoot } from '../../../_kit/lib/film.mjs';

const puppeteer = createRequire(`${kitRoot}/package.json`)('puppeteer-core');
const A = argv(undefined, ['4k']);
const K = A.has('4k') ? 2 : 1, W = 1920 * K, H = 1080 * K;   // --4k: the same layout drawn ×6 for the 4K delivery (sharp type)
const [id] = A.positional();
const C = loadClip(id);
const n = Math.round(C.duration * config.fps);
// counter: hours at each frame from the clip's own lapse (03 only so far)
const hours = C.counter ? JSON.parse(execFileSync('python3', ['-c',
  `import sys, json; sys.path.insert(0, ${JSON.stringify(rel('tools'))}); import physics as P; ` +
  `print(json.dumps([round(P.lapse03(i / ${config.fps}), 3) for i in range(${n + 1})]))`], { encoding: 'utf8' })) : null;
const S = { caps: C.caps || [], counter: C.counter ?? null, hours, fps: config.fps };

const page_ = `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=JetBrains+Mono:wght@400&family=Noto+Serif+SC:wght@400&display=block" rel="stylesheet">
<style>html,body{margin:0;background:transparent}</style><canvas id="cv" width="${W}" height="${H}"></canvas>
<script>
const S = ${JSON.stringify(S)};
const EN = '"Cinzel", serif', ZH = '"Noto Serif SC", serif', MONO = '"JetBrains Mono", "Noto Serif SC", monospace';
const BAR = 46;
const x = document.getElementById('cv').getContext('2d');
const seg = (t, a, b) => { const u = Math.min(1, Math.max(0, (t - a) / (b - a))); return u * u * (3 - 2 * u); };
const alphaIn = (t, a, b, fade = 0.45) => seg(t, a, a + fade) * (1 - seg(t, b - fade, b));   // cg-lab's caption fade
function text(s, px, py, font, color, a, align = 'center', spacing = 0) {
  if (a <= 0) return;
  x.save(); x.globalAlpha = a; x.font = font; x.fillStyle = color; x.textAlign = align; x.textBaseline = 'middle';
  if (spacing) x.letterSpacing = spacing + 'px';
  x.fillText(s, px + (align === 'center' ? spacing / 2 : 0), py); x.restore();
}
window.renderAt = (t, f) => {
  x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, ${W}, ${H}); x.setTransform(${3 * K}, 0, 0, ${3 * K}, 0, 0);
  for (const [a0, a1, en, zh] of S.caps) {             // lower bar: English (Cinzel, tracked) over 中文
    const a = alphaIn(t, a0, a1);
    text(en.toUpperCase(), 320, 360 - BAR + 16, '600 10px ' + EN, '#e9e2d0', a, 'center', 3);
    text(zh, 320, 360 - BAR + 31, '400 9px ' + ZH, '#b9b2a2', a, 'center', 2);
  }
  if (S.hours) {                                       // 03 counter, 巨物's readout: top-left of the picture
    const a = seg(t, 0, 0.25), h = S.hours[Math.min(f, S.hours.length - 1)], y0 = BAR + 14, L = 18;
    text('距上次日食  SINCE THE LAST ECLIPSE', L, y0, '400 6px ' + MONO, '#8a8f96', a * 0.8, 'left', 1);
    text('+' + h.toFixed(1).padStart(4, '0') + ' h', L, y0 + 11, '400 8px ' + MONO, '#c9c2b4', a, 'left', 1);
  }
};
window.ready = (async () => {
  const fonts = ['600 10px "Cinzel"', '400 9px "Noto Serif SC"', '400 6px "JetBrains Mono"'];
  const all = S.caps.map((c) => c[2].toUpperCase() + c[3]).join('') + '距上次日食SINCETHELASTECLIPSE+0123456789.h';
  await Promise.all(fonts.map((f) => document.fonts.load(f, all)));
  await document.fonts.ready;
  return fonts.filter((f) => !document.fonts.check(f, all));
})();
</script>`;

const html = rel(`frames/.overlay-${id}.html`);
fs.mkdirSync(rel('frames'), { recursive: true });
fs.writeFileSync(html, page_);
const browser = await puppeteer.launch({ executablePath: chrome(), headless: true, args: ['--allow-file-access-from-files'] });
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('page error:', e.message));
await page.setViewport({ width: W, height: H });
await page.goto(`file://${html}`, { waitUntil: 'networkidle0' });
const missing = await page.evaluate(() => window.ready);
if (missing.length) { console.error(`fonts missing: ${missing.join(', ')}`); await browser.close(); process.exit(1); }
const shot = (f) => page.evaluate((ff, fps) => { window.renderAt(ff / fps, ff); return document.getElementById('cv').toDataURL('image/png').split(',')[1]; }, f, config.fps);

const stills = A.opt('stills');
if (stills) {
  for (const t of stills.split(',').map(Number)) {
    const f = rel(`frames/${id}-overlay-t${t.toFixed(2)}.png`);
    fs.writeFileSync(f, Buffer.from(await shot(Math.round(t * config.fps)), 'base64'));
    console.log(`OVERLAY ${id}: ${f.replace(rel(''), '')}`);
  }
} else {
  const out = A.opt('out', rel(`out/.overlay-${id}.mov`)), t0 = Date.now();
  fs.mkdirSync(rel('out'), { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(config.fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'qtrle', '-pix_fmt', 'argb', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    if (!ff.stdin.write(Buffer.from(await shot(i), 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log(`OVERLAY ${id}: ${n} frames → ${out.replace(rel(''), '')} in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
}
await browser.close();
fs.rmSync(html, { force: true });
