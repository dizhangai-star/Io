// Clip timing, shared by the kit's Node tools. Picture timing lives in the Blender shot scripts.
window.TIMELINE = (A) => {
  const d = A.duration ?? 6;
  return { voice: 0.6, fade: [0, d], ...(A.timing || {}) };
};
