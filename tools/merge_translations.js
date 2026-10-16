// Merges hand-written translation chunks (ru_XX.json) into the pack's
// kubejs/assets/<ns>/lang/ru_ru.json, keeping entries that already exist there.
// Knaves' Needs weapon names are generated from material x weapon tables.
// Usage: node tools/merge_translations.js <missing.json> <chunks-dir> <kubejs-dir>
const fs = require('fs'), path = require('path');
const [missFile, chunkDir, kubejs] = process.argv.slice(2);
const miss = JSON.parse(fs.readFileSync(missFile, 'utf8'));

const tr = {};
for (const f of fs.readdirSync(chunkDir).filter(f => /^ru_\d+\.json$/.test(f)).sort())
  Object.assign(tr, JSON.parse(fs.readFileSync(path.join(chunkDir, f), 'utf8')));

// Knaves' Needs: item.knavesneeds.<mod>.<material>.<weapon>
const KN_WEAPON = {longsword: 'Длинный меч', twinblade: 'Парный клинок', rapier: 'Рапира', katana: 'Катана',
  sai: 'Саи', spear: 'Копьё', glaive: 'Глефа', warglaive: 'Боевая глефа', cutlass: 'Абордажная сабля',
  claymore: 'Клеймор', greataxe: 'Секира', greathammer: 'Боевой молот', chakram: 'Чакрам', scythe: 'Коса',
  halberd: 'Алебарда'};
const KN_MAT = {resonarium: 'из резонариума', ametrine: 'из аметрина', garnet: 'из граната',
  glowing: 'светящийся', steel: 'стальной'};
for (const ns of Object.keys(miss)) for (const k of Object.keys(miss[ns].name)) {
  const m = /^item\.knavesneeds\.[a-z_]+\.([a-z_]+)\.([a-z_]+)$/.exec(k);
  if (!m || tr[k] || !KN_WEAPON[m[2]] || !KN_MAT[m[1]]) continue;
  const mat = KN_MAT[m[1]];
  tr[k] = mat.startsWith('из ') ? KN_WEAPON[m[2]] + ' ' + mat : KN_WEAPON[m[2]] + ' (' + mat + ')';
}

let added = 0, untranslated = [];
for (const ns of Object.keys(miss)) {
  const keys = Object.keys(miss[ns].name).filter(k => tr[k] !== undefined);
  for (const k of Object.keys(miss[ns].name)) if (tr[k] === undefined && !/^(chipped|chisel|rechiseled|rechiseledae2)$/.test(ns)) untranslated.push(k);
  if (!keys.length) continue;
  const file = path.join(kubejs, 'assets', ns, 'lang', 'ru_ru.json');
  let cur = {};
  try { cur = JSON.parse(fs.readFileSync(file, 'utf8').replace(/^﻿/, '')); } catch (e) {}
  for (const k of keys) if (cur[k] === undefined) { cur[k] = tr[k]; added++; }
  fs.mkdirSync(path.dirname(file), {recursive: true});
  fs.writeFileSync(file, JSON.stringify(cur, null, 2) + '\n');
}
console.log('added', added, 'untranslated gameplay names', untranslated.length);
untranslated.slice(0, 30).forEach(k => console.log('  ' + k));
