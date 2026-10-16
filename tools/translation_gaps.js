// Lists en_us keys that have no Russian translation, either in the mod jar or in the pack's
// kubejs/assets/<ns>/lang/ru_ru.json overrides.
// Usage: node tools/translation_gaps.js <extracted-lang-dir> <kubejs-dir> [out.json]
//   extracted-lang-dir/<ns>/en_us.json and ru_ru.json, extracted from the mod jars.
// Groups: name (item/block/enchantment/effect/entity/biome names), desc (tooltips, descriptions),
// other (GUI, config, advancements, books...).
const fs = require('fs'), path = require('path');
const [langDir, kubejs, outFile] = process.argv.slice(2);
const read = f => { try { return JSON.parse(fs.readFileSync(f, 'utf8').replace(/^﻿/, '')); } catch (e) { return {}; } };
const NAME = /^(item|block|enchantment|effect|entity|biome|fluid|attribute|potion|painting|trim_material|trim_pattern|jukebox_song)\.[a-z0-9_.-]+$/;
const DESC = /(desc|tooltip|lore|info|\.hint)/;
const result = {}, summary = [];
for (const ns of fs.readdirSync(langDir)) {
  const en = read(path.join(langDir, ns, 'en_us.json'));
  const ru = Object.assign({}, read(path.join(langDir, ns, 'ru_ru.json')), read(path.join(kubejs, 'assets', ns, 'lang', 'ru_ru.json')));
  const miss = {name: {}, desc: {}, other: {}};
  for (const [k, v] of Object.entries(en)) {
    if (typeof v !== 'string' || ru[k] !== undefined || !/[A-Za-z]/.test(v)) continue;
    const g = NAME.test(k) && !DESC.test(k) ? 'name' : DESC.test(k) ? 'desc' : 'other';
    miss[g][k] = v;
  }
  const n = Object.keys(miss.name).length, d = Object.keys(miss.desc).length, o = Object.keys(miss.other).length;
  if (n + d + o) { result[ns] = miss; summary.push([ns, n, d, o, Object.keys(en).length]); }
}
summary.sort((a, b) => b[1] - a[1]);
const tot = summary.reduce((s, r) => [s[0] + r[1], s[1] + r[2], s[2] + r[3]], [0, 0, 0]);
console.log('missing: names', tot[0], 'descriptions', tot[1], 'other', tot[2]);
summary.slice(0, 45).forEach(r => console.log(r[0].padEnd(28), 'names', String(r[1]).padStart(5), 'desc', String(r[2]).padStart(5), 'other', String(r[3]).padStart(5), '/', r[4]));
if (outFile) fs.writeFileSync(outFile, JSON.stringify(result, null, 1));
