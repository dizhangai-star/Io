window.CLIP = {
  id: '04-eclipse',
  duration: 20,
  shot: 's04_eclipse.py',
  freeze: 9.5,                  // from 9.5 s one EXR + keyed exposure (nothing moves; eyes adjust in post)
  caps: [],                     // silence: no words in the eclipse
  sfx: [[0.15, 'in', { take: 'holdIn', d: 1.1, v: 0.8 }],      // one inhale, held; music cut at first contact (physics)
        [9.0, 'heartbeat'],                                           // second contact: the Sun is gone, black
        [11.75, 'heartbeat', { v: 1.06 }],                            // halfway through the eyes adjusting
        [14.5, 'heartbeat', { v: 1.12 }]],                            // the stars are up (beats 2.75 s apart); all at breath level
};
