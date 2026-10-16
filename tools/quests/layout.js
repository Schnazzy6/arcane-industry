// Place a thematic branch by dependency depth, leaving authored coordinates intact when requested.
// Independent branches occupy separate rows, so they cannot share a dependency segment.
module.exports = function layoutBranch(entries, row, options = {}) {
  const step = options.columnGap || 3, base = options.x || 0;
  const depth = new Map(), keys = new Set(entries.map(e => e.k));
  const active = new Set();
  function level(q) {
    if (depth.has(q.k)) return depth.get(q.k);
    if (active.has(q.k)) throw new Error('Branch dependency cycle: '+q.k);
    active.add(q.k);
    const parents = (q.dep||[]).filter(k=>keys.has(k)).map(k=>entries.find(p=>p.k===k));
    const n = parents.length ? 1+Math.max(...parents.map(level)) : 0;
    active.delete(q.k); depth.set(q.k,n); return n;
  }
  const lanes = new Map();
  for (const q of entries) {
    const d = level(q), lane = lanes.get(d)||0;
    lanes.set(d,lane+1);
    if (!q.at || options.force) q.at = [base+d*step, row+lane*4];
  }
  return entries;
};
