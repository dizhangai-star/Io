window.CLIP = {
  id: '01-horizon',
  duration: 9,
  shot: 's01_horizon.py',
  caps: [[5.5, 8.6, 'IO', '木卫一']],
  sfx: [[-0.9, 'in', { take: 'headIn' }], [1.0, 'out', { take: 'headOut', d: 1.9 }],   // audio/music.mjs: a breath before the picture
        [3.5, 'in', { take: 'catch', d: 0.45, atk: 0.03 }],             // a small quick intake as Jupiter's limb enters (3.4 s), held
        [6.4, 'out', { take: 'shaky', d: 2.6, shake: 5, v: 0.8 }]],   // the shaky release
};
