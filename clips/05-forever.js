window.CLIP = {
  id: '05-forever',
  duration: 10,
  shot: 's05_forever.py',
  caps: [[5.0, 9.4, 'EVERY 42 HOURS. FOREVER.', '每 42 小时，永远']],
  sfx: [[0.4, 'out', { take: 'sigh', d: 3.2, shake: 4, voice: 0.5 }],   // the long breath out with the dissolve
        [2.9, 'in', { take: 'farIn', d: 1.0, v: 0.55, far: 0.5 }], [4.6, 'out', { take: 'farOut', d: 1.6, v: 0.45, far: 0.8 }],   // receding as we rise
        [7.0, 'shimmer']],                                            // the plume lights ≈ 2 s after the diamond
};
