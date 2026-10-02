// Film-local title card (06): text on black, drawn in headless Chrome with 巨物's title type (Cinzel 600 caps tracked,
// 中文 Noto Serif SC spaced, a two-line physics readout in JetBrains Mono) so the series' cards match. No Blender:
// the card is all type, and the same canvas route can carry the captions + 03 counter at compile (Sprint 4).
// Usage: node tools/card.mjs <id> [--variant io|apeiro] [--out out/<id>.mp4] [--stills t1,t2,… (→ frames/<id>-tNN.png)]
//   Numbers come from `python3 tools/physics.py --card`. Frames are full 1920×1080 (black bars are black anyway).
//   Logical units are 巨物's 640×360 overlay grid, drawn ×3.
import { execFileSync, spawn } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { loadClip, rel, config, argv, chrome, kitRoot } from '../../../_kit/lib/film.mjs';

const puppeteer = createRequire(`${kitRoot}/package.json`)('puppeteer-core');
const A = argv();
const [id] = A.positional();
const C = loadClip(id);
const P = JSON.parse(execFileSync('python3', [rel('tools/physics.py'), '--card'], { encoding: 'utf8' }));
const variant = A.opt('variant', C.card?.variant ?? 'io');

const TITLE = {
  io: { en: 'IO', zh: '永 恒', enPx: 30, enSp: 18, zhPx: 13, zhSp: 6, kicker: ['木 卫 一', 'A MOON OF JUPITER'] },   // most don't know Io
  apeiro: { en: 'APEIROPHOBIA', zh: '永 恒 恐 惧 症', enPx: 22, enSp: 9, zhPx: 11, zhSp: 4 },   // as MEGALOPHOBIA / 巨物恐惧症
}[variant];
const LINES = [
  `木星 ${P.jupiter_deg}°，月亮的 ${P.moons} 倍  ·  每小时移动 ${P.moves_deg_h}°  ·  每 ${P.eclipse_every_h} 小时一次日食  ·  黑暗 ${P.eclipse_h} 小时`,
  `JUPITER ${P.jupiter_deg}° WIDE, ${P.moons}× THE MOON · MOVES ${P.moves_deg_h}° AN HOUR · AN ECLIPSE EVERY ${P.eclipse_every_h} H · ${P.eclipse_h} H OF DARK`,
];
const T = { title: [0.4, 3.5, 0.8], lines: [1.1, 3.5, 0.8] };   // [in, out, fade] s: black 0–0.4, both gone by 3.5, black tail

const page_ = `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=JetBrains+Mono:wght@400&family=Noto+Serif+SC:wght@400&display=block" rel="stylesheet">
<style>html,body{margin:0;background:#000}</style><canvas id="cv" width="1920" height="1080"></canvas>
<script>
const S = ${JSON.stringify({ TITLE, LINES, T })};
const EN = '"Cinzel", serif', ZH = '"Noto Serif SC", serif', MONO = '"JetBrains Mono", "Noto Serif SC", monospace';
const x = document.getElementById('cv').getContext('2d');
const ss = (a, b, t) => { const u = Math.min(1, Math.max(0, (t - a) / (b - a))); return u * u * (3 - 2 * u); };
const alphaIn = (t, [a, b, f]) => ss(a, a + f, t) * (1 - ss(b - f, b, t));
function text(s, px, py, font, color, a, spacing = 0) {
  if (a <= 0) return;
  x.save(); x.globalAlpha = a; x.font = font; x.fillStyle = color; x.textAlign = 'center'; x.textBaseline = 'middle';
  if (spacing) x.letterSpacing = spacing + 'px';
  x.fillText(s, px + spacing / 2, py); x.restore();      // letterSpacing trails the last glyph: shift half back to centre
}
window.renderAt = (t) => {
  x.setTransform(1, 0, 0, 1, 0, 0); x.fillStyle = '#000'; x.fillRect(0, 0, 1920, 1080); x.setTransform(3, 0, 0, 3, 0, 0);
  const a = alphaIn(t, S.T.title), b = alphaIn(t, S.T.lines), M = S.TITLE;
  if (M.kicker) {                                    // small label above the title: what Io is
    text(M.kicker[0], 320, 119, '400 7px ' + ZH, '#b9b2a2', a * 0.9, 3);
    text(M.kicker[1], 320, 129, '600 5.5px ' + EN, '#8a8f96', a * 0.9, 2.5);
  }
  text(M.en, 320, 162, '600 ' + M.enPx + 'px ' + EN, '#e9e2d0', a, M.enSp);
  text(M.zh, 320, 162 + M.enPx * 0.5 + 12, '400 ' + M.zhPx + 'px ' + ZH, '#d8d0bf', a, M.zhSp);
  text(S.LINES[0], 320, 210, '400 6px ' + MONO, '#b9b2a2', b, 1);
  text(S.LINES[1], 320, 219, '400 6px ' + MONO, '#8a8f96', b * 0.9, 1);
};
window.ready = (async () => {
  const fonts = ['600 30px "Cinzel"', '400 13px "Noto Serif SC"', '400 6px "JetBrains Mono"'];
  await Promise.all(fonts.map((f) => document.fonts.load(f, S.TITLE.en + S.TITLE.zh + (S.TITLE.kicker || []).join('') + S.LINES.join(''))));
  await document.fonts.ready;
  return fonts.filter((f) => !document.fonts.check(f, S.TITLE.zh + S.LINES[0]));
})();
</script>`;

const html = rel(`frames/.card-${id}.html`);
fs.mkdirSync(rel('frames'), { recursive: true });
fs.writeFileSync(html, page_);
const browser = await puppeteer.launch({ executablePath: chrome(), headless: true, args: ['--allow-file-access-from-files'] });
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('page error:', e.message));
await page.setViewport({ width: 1920, height: 1080 });
await page.goto(`file://${html}`, { waitUntil: 'networkidle0' });
const missing = await page.evaluate(() => window.ready);
if (missing.length) { console.error(`fonts missing: ${missing.join(', ')}`); await browser.close(); process.exit(1); }
const shot = (t) => page.evaluate((tt) => { window.renderAt(tt); return document.getElementById('cv').toDataURL('image/png').split(',')[1]; }, t);

const stills = A.opt('stills');
if (stills) {
  for (const t of stills.split(',').map(Number)) {
    const f = rel(`frames/${id}-t${t.toFixed(2)}.png`);
    fs.writeFileSync(f, Buffer.from(await shot(t), 'base64'));
    console.log(`CARD ${id} ${variant}: ${f.replace(rel(''), '')}`);
  }
} else {
  const out = A.opt('out', rel(`out/${id}.mp4`)), n = Math.round(C.duration * config.fps), t0 = Date.now();
  fs.mkdirSync(rel('out'), { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(config.fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', String(config.crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
  { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    if (!ff.stdin.write(Buffer.from(await shot(i / config.fps), 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log(`CARD ${id} ${variant}: ${n} frames → ${out.replace(rel(''), '')} in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
}
await browser.close();
fs.rmSync(html, { force: true });
