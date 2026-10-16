// Counts, for every kubejs:* item, how many recipes produce it and how many use it as an
// ingredient. Sources: the progression plan (progression.js AI_PLAN, inputs only) and the
// recipe scripts that build JSON in code (rework.js, rework_ladder.js, qol_progression.js...).
// Usage: node tools/audit_kubejs_items.js
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const kjs = path.join(root, 'overrides/common/kubejs');
const items = new Set();
for (const f of fs.readdirSync(path.join(kjs, 'startup_scripts'))) {
  const src = fs.readFileSync(path.join(kjs, 'startup_scripts', f), 'utf8');
  for (const m of src.matchAll(/create\(\s*["']([a-z0-9_]+)["']/g)) items.add('kubejs:' + m[1]);
  for (const m of src.matchAll(/\[\s*'([a-z0-9_]+)'\s*,\s*'[^']+'\s*(?:,\s*\d+)?\s*\]/g)) items.add('kubejs:' + m[1]);
}
// modules: kind_t<min..11>
for (const [k, min] of [['tech_module', 4], ['dark_essence', 7], ['spirit_contract', 4], ['aura_seed', 4]])
  for (let t = min; t <= 11; t++) items.add('kubejs:' + k + '_t' + t);
const made = {}, used = {};
const bump = (o, k) => o[k] = (o[k] || 0) + 1;
// plan
const line = fs.readFileSync(path.join(kjs, 'server_scripts/progression.js'), 'utf8').split('\n')[1];
const plan = JSON.parse(line.slice(line.indexOf('{')).trim().replace(/;$/, ''));
for (const r of plan.recipes.concat(plan.patches)) {
  const j = Object.assign({}, r.json);
  const outs = JSON.stringify([j.result, j.results, j.output, j.item_outputs]);
  delete j.result; delete j.results; delete j.output; delete j.item_outputs; delete j.ritual_dummy;
  for (const m of JSON.stringify(j).matchAll(/"kubejs:([a-z0-9_]+)"/g)) bump(used, 'kubejs:' + m[1]);
  for (const m of outs.matchAll(/"kubejs:([a-z0-9_]+)"/g)) bump(made, 'kubejs:' + m[1]);
}
for (const a of plan.armor) for (const k of ['core', 'material', 'plate', 'binding', 'accent', 'school'])
  if (typeof a[k] === 'string' && a[k].startsWith('kubejs:')) bump(used, a[k]);
// scripts: an id string in source counts as a use unless it sits in a result/output field
for (const f of fs.readdirSync(path.join(kjs, 'server_scripts'))) {
  if (f === 'progression.js' || !f.endsWith('.js')) continue;
  const src = fs.readFileSync(path.join(kjs, 'server_scripts', f), 'utf8');
  for (const m of src.matchAll(/(result|output|item_outputs|out)[^\n]{0,60}?'kubejs:([a-z0-9_]+)'/g)) bump(made, 'kubejs:' + m[2]);
  for (const m of src.matchAll(/'kubejs:([a-z0-9_]+)'/g)) bump(used, 'kubejs:' + m[1]);
}
// rework_ladder builds module ids and uses stage parts from AI_LADDER_STAGE (already counted as strings)
const rows = [...items].sort().map(id => [id, made[id] || 0, Math.max(0, (used[id] || 0) - (made[id] || 0))]);
const unused = rows.filter(r => r[2] === 0);
console.log('items', rows.length, 'unused as ingredient', unused.length);
unused.forEach(r => console.log('  ', r[0], 'made by', r[1]));
console.log('\nleast used:'); rows.filter(r => r[2] > 0).sort((a, b) => a[2] - b[2]).slice(0, 15).forEach(r => console.log('  ', r[0], 'uses', r[2]));
