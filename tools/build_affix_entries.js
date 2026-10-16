// Rebuilds every Apotheosis affix_loot_entry on the gear tier scale (GEAR-TIERS.md), so mob
// gear and Gateways follow the same world-tier ceilings as chest loot (gear_loot.js).
// Usage: node tools/build_affix_entries.js tools/affix-jar-entries.txt <registered-items.txt>
//   lines "namespace|path|item id" for entries shipped inside mod jars.
// Writes overrides/common/kubejs/data/<ns>/affix_loot_entries/<path>.json.
// Ceiling per world tier: Haven III, Frontier IV, Ascent V, Summit VI, Pinnacle VII; the
// ceiling is rare, one and two tiers below are common, three below is rare, lower is out.
// Items above VII or outside the table get weight 0 everywhere (never generated).
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const data = path.join(root, 'overrides/common/kubejs/data');
const table = JSON.parse(fs.readFileSync(path.join(root, 'overrides/common/kubejs/config/gear-tiers.json'), 'utf8'));
const CAPS = {haven: 3, frontier: 4, ascent: 5, summit: 6, pinnacle: 7};
const WEIGHT_BY_GAP = [2, 6, 6, 2];

function weights(id) {
  const tier = table.tiers[id], w = {};
  for (const [wt, cap] of Object.entries(CAPS)) {
    const gap = tier === undefined || tier > 7 ? -1 : cap - tier;
    w[wt] = {weight: gap >= 0 && gap < WEIGHT_BY_GAP.length ? WEIGHT_BY_GAP[gap] : 0, quality: 0.0};
  }
  return w;
}
function readStackId(file) {
  try { const j = JSON.parse(fs.readFileSync(file, 'utf8')); return j.stack && (j.stack.id || j.stack.item); } catch (e) { return null; }
}
function write(file, id) {
  fs.mkdirSync(path.dirname(file), {recursive: true});
  fs.writeFileSync(file, JSON.stringify({type: 'apotheosis:affix_loot_entry', stack: {count: 1, id: id}, weights: weights(id)}, null, 2) + '\n');
}

// Items known to work as affix entries: everything that had an entry before (old generator
// output and earlier overrides) plus everything a mod jar ships.
const known = {}; // file (relative to data) -> item id
for (const ns of fs.readdirSync(data)) {
  const dir = path.join(data, ns, 'affix_loot_entries');
  if (!fs.existsSync(dir)) continue;
  const walk = d => fs.readdirSync(d, {withFileTypes: true}).forEach(e => {
    const f = path.join(d, e.name);
    if (e.isDirectory()) walk(f); else { const id = readStackId(f); if (id) known[path.relative(data, f)] = id; }
  });
  walk(dir);
}
const jarLines = fs.readFileSync(process.argv[2], 'utf8').split(/\r?\n/).filter(Boolean);
// argv[3]: registered item ids, one per line (a server dump or the scratch known-items list).
const registry = new Set(fs.readFileSync(process.argv[3], 'utf8').split(/\r?\n/).filter(Boolean));
for (const rel of Object.keys(known)) if (!registry.has(known[rel])) { fs.rmSync(path.join(data, rel), {force: true}); delete known[rel]; }
let fromJar = 0;
for (const line of jarLines) {
  const [ns, p, id] = line.split('|');
  const rel = path.join(ns, 'affix_loot_entries', p + '.json');
  // Jar entries for mods that are not installed carry a mod_loaded condition; overriding them
  // without it would fail, so only items present in the registry are taken.
  if (!known[rel] && id && registry.has(id)) { known[rel] = id; fromJar++; }
}let live = 0, off = 0;
for (const [rel, id] of Object.entries(known)) {
  write(path.join(data, rel), id);
  if (Object.values(weights(id)).some(w => w.weight > 0)) live++; else off++;
}
console.log('entries written', Object.keys(known).length, '(from jars', fromJar + ')', 'generating', live, 'switched off', off);
