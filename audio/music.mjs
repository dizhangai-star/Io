// Io · 永恒's soundtrack, synthesized (no narration), cut to the film layout of tools/timeline.mjs (head, cuts, the
// 04 → 05 dissolve). Vacuum: nothing outside the helmet is heard, and the suit itself is silent too (user 2026-10-03:
// the hum and creaks read as surf and pulled focus); the only human sound is breath, ~9 breaths in the film, each a
// reaction, with true silence between them so the silence is what you hear.
//   head + 01  a breath before the picture; calm, then a sharp catch as Jupiter's limb enters, held, a shaky release
//   02         the sub drone enters (J-cut under 01's end); one breath in as the arm rises, held, out before it lowers
//   03         no breath (time-lapse: human time is gone): drone + a pad whose chord turns with the light (sunset, full
//              Jupiter, sunrise) + a glass tick on every whole hour of the counter (they race and slow with the eased time)
//   04         one inhale, held; the pad swells and a riser climbs into first contact, where all music cuts (after the
//              reverb); silence; one heartbeat at 14.5 s; silence to the dissolve
//   05         a long voiced exhale with the dissolve, then one faint breath, receding as we rise; the drone back under
//              the rise; the Sun's diamond rings and the chord resolves (A) as the whole Sun comes out; the plume's
//              light a high shimmer; everything fades with the picture → a breath of silence
//   06         one held note under the title (as 巨物)
// Times: physical events from `python3 tools/physics.py --sound` (03 hours, sunset/full/sunrise; 04 contact; 05
// contact/full/hold), directing cues from each clip's `sfx` ([t, kind, {v, d}], clip seconds; t < 0 = before the cut).
// Usage: node audio/music.mjs → audio/build/film.wav (48 kHz stereo, the film's exact length, peak −1 dBFS);
// compile.mjs calls it and sets the loudness. Balance check: BUS=1 node audio/music.mjs (music | sfx dB per 0.5 s).
import { execFileSync } from 'node:child_process';
import { rel } from '../../../_kit/lib/film.mjs';
import { rng, voices, freeverb, hpf, level, writeWav, hz, panG } from '../../../_kit/audio/dsp.mjs';
import { layout } from '../tools/timeline.mjs';

const SR = 48000, F = layout(), END = F.total, N = Math.ceil(END * SR);
const L = new Float32Array(N), R = new Float32Array(N), MUS = [L, R];           // music (hall, gated at contact)
const SL = new Float32Array(N), SRt = new Float32Array(N), SFX = [SL, SRt];     // breath + heartbeat (dry, helmet)
const TL = new Float32Array(N), TR = new Float32Array(N), TTL = [TL, TR];       // the title's note (own reverb)
const { rnd, jit } = rng(20261003);
const V = voices({ sr: SR, n: N, rnd, music: MUS, sfx: SFX });
const { noise, glide, partials } = V;
const P = JSON.parse(execFileSync('python3', [rel('tools/physics.py'), '--sound'], { encoding: 'utf8' }));
const at = F.at, t3 = at('03-eternity'), t4 = at('04-eclipse'), t5 = at('05-forever'), t6 = at('06-title');
const contact = t4 + P['04'].contact, diamond = t5 + P['05'].contact, sunFull = t5 + P['05'].full;
const S = (t) => Math.max(0, Math.min(N, Math.floor(t * SR)));
const c01 = (x) => Math.min(1, Math.max(0, x));
const sm = (a, b, x) => { const u = c01((x - a) / (b - a)); return u * u * (3 - 2 * u); };

// ---------- voices (svf / syn as in 巨物's music.mjs) ----------
function svf() {
  let lp = 0, bp = 0; const o = { lp: 0, bp: 0, hp: 0 };
  return (x, fc, q = 0.7) => {
    const f = 2 * Math.sin(Math.PI * Math.min(fc, 7000) / SR);
    lp += f * bp; const hp = x - lp - q * bp; bp += f * hp;
    o.lp = lp; o.bp = bp; o.hp = hp; return o;
  };
}
const blep = (p, dt) => p < dt ? (p /= dt, p + p - p * p - 1) : p > 1 - dt ? (p = (p - 1) / dt, p * p + p + p + 1) : 0;
// Subtractive voice: n detuned PolyBLEP saws (or sines) → low-pass whose cutoff follows the envelope (c0 → c1).
function syn(bus, t, d, m, v, pan, o = {}) {
  const rel = o.rel ?? 0.4, s0 = Math.floor(t * SR), n = Math.min(Math.ceil((d + rel * 3) * SR), N - s0);
  if (n <= 0 || s0 < 0) return;
  const nv = o.n ?? 3, det = o.det ?? 8, f0 = hz(m), sine = o.wave === 'sine';
  const ph = Array.from({ length: nv }, () => rnd()), fr = Array.from({ length: nv }, (_, i) => nv === 1 ? 1 : 2 ** (det * (i / (nv - 1) * 2 - 1) / 1200));
  const [gl, gr] = panG(pan), [bl, br] = bus, atk = Math.max(1, (o.atk ?? 0.05) * SR), dn = d * SR, flt = svf();
  const c0 = o.c0 ?? 400, c1 = o.c1 ?? 2400, q = o.q ?? 0.8, vph = rnd() * 6.28;
  for (let i = 0; i < n; i++) {
    const u = i / dn;
    const e = (i < atk ? (o.curve ? (i / atk) ** o.curve : i / atk) : 1) * (i > dn ? Math.exp(-(i - dn) / (rel * SR)) : 1);
    const r = 2 ** ((o.vib ?? 0) * Math.min(1, u * 2) * Math.sin(2 * Math.PI * 5 * i / SR + vph) / 1200);
    let x = 0;
    for (let k = 0; k < nv; k++) {
      const dt = f0 * fr[k] * r / SR; ph[k] += dt; if (ph[k] >= 1) ph[k] -= 1;
      x += sine ? Math.sin(2 * Math.PI * ph[k]) : 2 * ph[k] - 1 - blep(ph[k], dt);
    }
    x /= nv;
    const y = sine ? x : flt(x, c0 + (c1 - c0) * e, q).lp;
    bl[s0 + i] += y * e * v * gl; br[s0 + i] += y * e * v * gr;
  }
}
// One breath in the helmet, drawn as a whispered vowel: pinkish noise through the vocal tract's formants (parallel
// resonators, this breath's tract jittered ±6 %, drifting up on the way in, down on the way out), lip turbulence on top,
// a fast-in / slow-out envelope with ~15 Hz airflow flutter. (A symmetric swell of plain band noise reads as surf.)
// o: d (s), v, nose (softer, lower), atk (s; short = a gasp), shake (Hz: a trembling exhale), voice (0..1: a breathy
// glottal buzz at the end of an exhale, a sigh), far (0..1: the camera leaving the helmet, darker and quieter).
function breath(t, kind, o = {}) {
  const IN = kind === 'in', d = o.d ?? (IN ? 1.1 : 1.8), s0 = S(t), n = Math.min(Math.ceil(d * SR), N - s0);
  if (n <= 0) return;
  const FM = o.nose ? [[290, 1, 0.22], [1050, 0.25, 0.18], [2300, 0.08, 0.16]]
    : IN ? [[720, 1, 0.16], [1300, 0.65, 0.14], [2650, 0.4, 0.12], [3900, 0.22, 0.12]]
      : [[620, 1, 0.18], [1150, 0.5, 0.16], [2450, 0.25, 0.14], [3500, 0.12, 0.14]];
  const fl = FM.map(() => svf()), jf = FM.map(() => 1 + jit(0.06)), lip = svf(), dk = svf();
  const atk = Math.min(0.9, (o.atk ?? (IN ? 0.12 : 0.06)) / d), far = o.far ?? 0, sh = rnd() * 6.28;
  const g = 0.075 * (o.v ?? 1) * (o.nose ? 0.6 : 1) * (1 - 0.6 * far), [gl, gr] = panG(jit(0.05));
  let p0 = 0, p1 = 0, fq = 0, gph = 0;
  for (let i = 0; i < n; i++) {
    const u = i / n;
    let e = IN ? sm(0, atk, u) * (0.75 + 0.25 * u) * (1 - sm(0.8, 1, u)) : sm(0, atk, u) * (1 - u) ** 1.5;
    const w = rnd() * 2 - 1;
    p0 = 0.985 * p0 + 0.015 * w; p1 = 0.7 * p1 + 0.3 * w;                     // pinkish source
    fq += 0.002 * ((rnd() * 2 - 1) - fq);                                     // airflow flutter
    e *= 1 + 9 * fq;
    if (o.shake) e *= 1 + 0.2 * Math.sin(2 * Math.PI * o.shake * i / SR + sh) * sm(0.1, 0.3, u);
    let src = p0 * 4 + p1 * 0.6;
    if (o.voice) { gph += 105 * (1 - 0.12 * u) / SR; if (gph >= 1) gph -= 1; src += o.voice * 0.5 * (2 * gph - 1) * sm(0.35, 0.65, u) * (1 - sm(0.85, 1, u)); }
    const drift = IN ? 1 + 0.05 * u : 1 - 0.08 * u;
    let y = 0;
    FM.forEach(([f, a, q], k) => { y += a * q * fl[k](src, f * jf[k] * drift, q).bp; });
    y += (IN ? 0.05 : 0.025) * lip(w, 4800, 0.7).hp;
    y = dk(y, (IN ? 7000 : 6500 - 3500 * u) * (1 - 0.75 * far), 0.7).lp;
    SL[s0 + i] += y * e * g * gl; SRt[s0 + i] += y * e * g * gr;
  }
}
// Recorded breaths (user 2026-10-03: the synth breath still read as fake). CC0 Freesound recordings in the shared
// library (REFERENCES.md); takes = [source, from s, to s], cut at the breath's soft edges (band 0.8–6 kHz envelope,
// inhales bright with no mic pop, exhales with one), high-passed at 180 Hz twice (the pops are < 150 Hz), lightly
// denoised, faded, and levelled to one RMS so a cue's v is its loudness. A cue with `take` plays the recording when
// the file exists, else falls back to the synth breath above with the cue's own options. A 4th element overrides
// the filter chain / level (the heartbeat: no high-pass, no denoise).
const LIB = rel('../../_assets/audio/breath');
const SRC = { mlitty: '387620__mlitty__slow-breath-relax.mp3', drew: '682884__drewsimko__shaky_breaths.wav',
  heart: '332819__loudernoises__heartbeat-80bpm-limited.wav' };
const TAKES = {
  headIn: ['mlitty', 0.85, 2.60],      // a slow, soft inhale (0.9 s rise)
  headOut: ['mlitty', 3.95, 5.90],
  catch: ['mlitty', 65.70, 66.35],     // the first 0.65 s of the steepest inhale (0.27 s rise): a small, quick intake
  shaky: ['drew', 0.85, 3.10],         // the shaky release: out, a hitch, a trailing out
  armIn: ['mlitty', 39.15, 41.30],
  armOut: ['mlitty', 68.10, 70.10],
  holdIn: ['mlitty', 7.55, 9.30],
  sigh: ['mlitty', 101.90, 104.30],    // 05: the long breath out
  farIn: ['mlitty', 46.90, 48.70],
  farOut: ['mlitty', 49.95, 52.00],
  // one lub-dub of a steady 80 bpm loop (lub every 0.75 s, dub +0.245 s): lub 3.000, dub 3.245, silence from 3.46
  heart: ['heart', 2.985, 3.70, { af: 'highpass=f=25', rms: 0.0112 }],   // +2.9 dB (user 2026-10-03): beats at breath level
};
const fs = await import('node:fs');
function take(name) {
  const [src, a, b, o = {}] = TAKES[name], f = `${LIB}/${SRC[src]}`;
  if (!fs.existsSync(f)) return null;
  const d = b - a, raw = execFileSync('ffmpeg', ['-v', 'error', '-ss', String(a), '-t', d.toFixed(3), '-i', f, '-ac', '1', '-ar', String(SR),
    '-af', `${o.af ?? 'highpass=f=180,highpass=f=180,afftdn=nr=10:nf=-60,afade=t=in:d=0.06'},afade=t=out:st=${(d - 0.18).toFixed(3)}:d=0.18`,
    '-f', 'f32le', '-'], { maxBuffer: 1 << 28 });
  const x = new Float32Array(raw.buffer, raw.byteOffset, raw.length / 4), w = Math.round(0.2 * SR);
  let pk = 0;                                                               // loudest 200 ms window → RMS 0.0063 (breath)
  for (let i = 0; i + w <= x.length; i += w / 4) { let s = 0; for (let k = i; k < i + w; k++) s += x[k] * x[k]; pk = Math.max(pk, s / w); }
  return x.map((v) => v * (o.rms ?? 0.0063) / Math.sqrt(pk || 1));
}
function recorded(t, name, o) {
  const x = take(name); if (!x) return false;
  const far = o.far ?? 0, g = (o.v ?? 1) * (1 - 0.6 * far), [gl, gr] = panG(jit(0.05)), s0 = S(t), dk = svf();
  for (let i = 0; i < x.length && s0 + i < N; i++) {
    const y = far ? dk(x[i], 7000 * (1 - 0.75 * far), 0.7).lp : x[i];
    SL[s0 + i] += y * g * gl; SRt[s0 + i] += y * g * gr;
  }
  return true;
}
// A glass tick: a soft struck partial set + a click, the note from the current chord.
function tick(t, m, v, pan) {
  const f = hz(m);
  partials(t, [[f, v, 0.32], [f * 2.76, v * 0.22, 0.07], [f * 5.4, v * 0.08, 0.025]], pan, 1.6, MUS, 0.002);
  noise(t, 0.006, v * 0.12, pan, MUS, { bp: 5200, q: 1.5 });
}

// ---------- the chords of 03, turning with the light (A drone under all of them) ----------
const H = P['03'];
const CHORDS = [                                            // [film t, midi notes]
  [t3, [45, 52, 59, 64]],                                   // day, a crescent: A2 E3 B3 E4 (Am9, open)
  [t3 + H.sunset, [41, 48, 57, 64]],                        // sunset: F2 C3 A3 E4 (Fmaj7)
  [t3 + H.full, [43, 50, 59, 66]],                          // full Jupiter: G2 D3 B3 F#4 (bright, over the A drone)
  [t3 + H.sunrise, [40, 47, 57, 59, 64]],                   // sunrise: E2 B2 A3 B3 E4 (Esus4, waits for A)
];
const RESOLVE = [45, 52, 57, 61, 64, 71];                   // 05: A2 E3 A3 C#4 E4 B4 (A add9)
const chordAt = (t) => CHORDS.reduce((c, x) => (t >= x[0] ? x : c), CHORDS[0])[1];

// ---------- cue kinds (clip sfx) ----------
const KINDS = {
  // breath: [t, 'in' | 'out', { take, v, far, …synth fallback: d, nose, atk, shake, voice }] (see TAKES, breath)
  in: (t, v, o) => (o.take && recorded(t, o.take, { ...o, v })) || breath(t, 'in', { ...o, v }),
  out: (t, v, o) => (o.take && recorded(t, o.take, { ...o, v })) || breath(t, 'out', { ...o, v }),
  // 02 → 04: the sub drone, A1 + A2, filter slowly opening; runs until the 04 first contact (the gate cuts it)
  drone: (t, v) => {
    const d = contact - t + 0.5;
    syn(MUS, t, d, 33, 0.11 * v, 0, { n: 1, wave: 'sine', atk: 3, rel: 1, curve: 2 });   // one sine: a detuned pair beats
    syn(MUS, t + 0.5, d - 0.5, 45, 0.1 * v, 0, { n: 3, det: 9, atk: 8, rel: 1, c0: 110, c1: 420, q: 1.1, curve: 2 });
  },
  // 04: a heartbeat in the dark: one recorded lub-dub (TAKES.heart), or the synth beat below without the file
  heartbeat: (t, v) => {
    if (recorded(t, 'heart', { v })) return;
    // a sub thump (kept low: 60 Hz is all peak and little loudness, and the film's gain would drive it into the
    // limiter) + a 100–200 Hz body and a soft skin tap so it reads on small speakers
    const thump = (tt, g, f0) => { glide(tt, 0.18, 0.45 * g * v, (u) => f0 - 22 * u, 0, (u) => Math.sin(Math.PI * Math.min(1, u * 6)) * Math.exp(-u * 5));
      glide(tt, 0.12, 0.12 * g * v, (u) => 2.4 * f0 - 40 * u, 0, (u) => Math.sin(Math.PI * Math.min(1, u * 8)) * Math.exp(-u * 7));
      noise(tt, 0.1, 0.25 * g * v, 0, SFX, { bp: 160, q: 0.9, dec: 0.025 });
      noise(tt, 0.03, 0.04 * g * v, 0, SFX, { bp: 420, q: 1.2, dec: 0.008 }); };
    thump(t, 0.18, 62); thump(t + 0.3, 0.12, 54);
  },
  // 05: the plume's canopy catches the light: a high, glassy cluster swelling and fading
  shimmer: (t, v, o) => {
    const d = o.d ?? 2.6;
    [[88, 0.022], [93, 0.016], [95, 0.012], [100, 0.006]].forEach(([m, g], i) =>
      syn(MUS, t + i * 0.12, d, m, g * v, (i - 1.5) * 0.4, { n: 1, wave: 'sine', atk: d * 0.45, rel: 1.4, vib: 6 }));
  },
  // 06: a single held note under the title (A4, glassy; an octave below, faint), as 巨物
  note: (t, v, o) => {
    const d = o.d ?? 3.4, rel = o.rel ?? 1.2;
    syn(TTL, t, d, 69, 0.04 * v, 0.05, { n: 1, wave: 'sine', atk: 1.2, rel, vib: 4 });
    syn(TTL, t + 0.3, d - 0.3, 57, 0.02 * v, -0.1, { n: 3, det: 7, atk: 1.6, rel, c0: 300, c1: 900 });
  },
};
let sfxN = 0;
for (const c of F.clips) for (const [t, kind, o = {}] of c.A.sfx ?? []) {
  if (!KINDS[kind]) throw new Error(`${c.id}: unknown sfx ${kind}`);
  KINDS[kind](c.start + t, o.v ?? 1, o); sfxN++;
}

// ---------- the helmet: two early reflections off the visor colour the breath (a bowl round the head) ----------
for (const a of [SL, SRt]) for (let i = N - 1; i >= 131; i--) a[i] += 0.3 * a[i - 77] + 0.18 * a[i - 131];

// ---------- music: 03 pad + hour ticks, 04 swell into contact, 05 diamond + resolve ----------
CHORDS.forEach(([t, notes], k) => {
  const end = k < CHORDS.length - 1 ? CHORDS[k + 1][0] + 0.5 : t4 + 1.0;      // the last one thins out in 04's first second
  notes.forEach((m, i) => syn(MUS, t, end - t, m, 0.045, (i / (notes.length - 1) - 0.5) * 0.7,
    { n: 3, det: 7, atk: k === 0 ? 0.35 : 1.2, rel: 1.0, c0: 220, c1: 1000, q: 0.7 }));
});
H.hours.forEach((s, k) => {                                               // a tick on every whole hour (+1 h … +38 h)
  const t = t3 + s, sp = (H.hours[k + 1] ?? 12) - (H.hours[k - 1] ?? 0), ch = chordAt(t);
  tick(t, ch[(k % (ch.length - 1)) + 1] + 12, 0.07 * Math.min(1, Math.max(0.4, sp / 1.2)) ** 0.6, (k % 2 ? 0.25 : -0.25));
});
// 04: the Esus pad swells and opens, a riser climbs, both cut at first contact
CHORDS.at(-1)[1].forEach((m, i) => syn(MUS, t4, contact - t4 + 0.3, m + 12, 0.12, (i / 4 - 0.5) * 0.8,
  { n: 3, det: 10, atk: contact - t4, curve: 2.0, rel: 0.5, c0: 300, c1: 3200, q: 0.9 }));
noise(t4 + 0.5, contact - t4 - 0.5, 0.18, 0, MUS, { sweep: [180, 4200], q: 1.1, atk: 0.01, shape: (u) => u ** 3 });
// 05: the drone returns under the rise; the diamond rings; the chord blooms to the whole Sun and resolves
syn(MUS, t5 + P['05'].hold, t6 - t5 - P['05'].hold, 33, 0.09, 0, { n: 1, wave: 'sine', atk: 3.5, rel: 1, curve: 2 });
[[81, 0.11], [88, 0.08], [93, 0.055]].forEach(([m, g], i) =>
  partials(diamond + i * 0.07, [[hz(m), g, 2.4], [hz(m) * 2.01, g * 0.2, 0.6], [hz(m) * 3.02, g * 0.08, 0.25]], (i - 1) * 0.3, 4, MUS, 0.003));
RESOLVE.forEach((m, i) => syn(MUS, diamond + 0.1, t6 - diamond, m, 0.13, (i / (RESOLVE.length - 1) - 0.5) * 0.8,
  { n: 3, det: 8, atk: sunFull - diamond, curve: 1.5, rel: 1.2, c0: 260, c1: 1500, q: 0.7 }));

// ---------- mix: music through a hall, the breath nearly dry, the title its own; gates after the reverb ----------
const GM = 0.45, GS = 3.5, WET = 0.5, WS = 0.08;
[L, R, SL, SRt, TL, TR].forEach((a) => hpf(a, 24, SR));
if (process.env.BUS) {
  const st = (a, g) => { const l = level(a, g); return `rms ${l.rms.toFixed(1)} dB, peak ${l.peak.toFixed(1)} dB`; };
  console.log(`music ${st(L, GM)} | sfx ${st(SL, GS)}`);
  for (let t = 0; t < END; t += 0.5) {
    const a = S(t), b = S(t + 0.5), db = (arr, g) => { let s = 0; for (let i = a; i < b; i++) s += (arr[i] * g) ** 2; return (10 * Math.log10(s / (b - a) + 1e-12)).toFixed(0).padStart(4); };
    console.log(`${t.toFixed(1).padStart(5)}  ${db(L, GM)} | ${db(SL, GS)} | ${db(TL, 1)}`);
  }
}
const hall = { sr: SR, room: 0.86, damp: 0.5, pre: 0.03 }, helmet = { sr: SR, room: 0.3, damp: 0.8, pre: 0.002 };
const mono = (a, b, g) => { const m = a.map((v, i) => (v + b[i]) * 0.5 * g); hpf(m, 140, SR); return m; };
const ms = mono(L, R, GM), ss = mono(SL, SRt, GS), ts = mono(TL, TR, 1);
const wl = freeverb(ms, 0, hall), wr = freeverb(ms, 23, hall);
const hl = freeverb(ss, 0, helmet), hr = freeverb(ss, 23, helmet);
const tl = freeverb(ts, 0, hall), tr = freeverb(ts, 23, hall);
for (let i = 0; i < N; i++) {
  const t = i / SR;
  const gm = t >= contact && t < t5 ? 0 : 1;                              // first contact: the music stops dead, no tail
  const ge = 1 - sm(t6 - 1, t6, t);                                       // 05 fades to black → silence before the title
  L[i] = ((L[i] * GM + wl[i] * WET) * gm + SL[i] * GS + hl[i] * WS) * ge + TL[i] + tl[i] * WET;
  R[i] = ((R[i] * GM + wr[i] * WET) * gm + SRt[i] * GS + hr[i] * WS) * ge + TR[i] + tr[i] * WET;
}
for (let i = Math.floor((END - 0.6) * SR); i < N; i++) { const g = (N - i) / (0.6 * SR); L[i] *= g; R[i] *= g; }
await writeWav(rel('audio/build/film.wav'), L, R, SR);
console.log(`film: ${sfxN} sfx, ${H.hours.length} ticks, ${END}s → audio/build/film.wav`);
