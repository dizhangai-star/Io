// The film's layout, shared by compile.mjs (picture) and audio/music.mjs (score + foley), so both put every clip at
// the same film second. The kit's film() can't: it lays clips end to end, without the head or the 04 → 05 dissolve.
// Joints (user 2026-10-03): hard cuts everywhere except one dissolve, 04 → 05 (ring match). Head: black with sound
// first, then 01 fades up. 05's last second fades to black; 06 opens on its own black.
import { config, clipIds, loadClip } from '../../../_kit/lib/film.mjs';

export const HEAD = { black: 1.0, fade: 0.5 };               // s: black (breath, suit hum), then 01 fades up
export const JOINTS = {                                      // the joint after each clip; d in frames (24 fps)
  '04-eclipse': { kind: 'dissolve', d: 36 },                 // ring match: 1.5 s, stars → stars, the astronaut appears
};
export const FADE_OUT = { '05-forever': 1.0 };               // s at the clip's end, to black

// → { clips: [{ id, start, duration, joint_out, A }], total }: the dissolve overlaps real frames, so
// total = Σ clips − dissolves + head.
export function layout() {
  const ids = clipIds(), fps = config.fps;
  let at = HEAD.black;
  const clips = ids.map((id, k) => {
    const A = loadClip(id), j = JOINTS[id];
    const c = { id, start: +at.toFixed(4), duration: A.duration, joint_out: j?.kind ?? (k < ids.length - 1 ? 'cut' : 'end'), A };
    at += A.duration - (j?.kind === 'dissolve' ? j.d / fps : 0);
    return c;
  });
  return { clips, total: +at.toFixed(4), at: (id) => clips.find((c) => c.id === id).start };
}
