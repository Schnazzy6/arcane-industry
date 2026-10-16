// Builds the FTB Quests book (FTB Quests 2101.1.x) from tools/quests/ch_*.js.
// Text goes to quests/lang/<locale>.snbt, structure to chapters/*.snbt.
// Usage: node tools/quests/build.js            -> writes overrides/common/config/ftbquests/quests
//        node tools/quests/build.js --check    -> only validates items and layout
//
// Chapter module: module.exports = {k, group, t, s, icon, order, quests: [...]}.
// Quest: k (unique key), t (title), d (description lines; '' = blank line, '{@pagebreak}' = new page),
//   at: [x, y] grid position (y grows downwards; one cell = 1 unit),
//   task: 'check' | [item, count] | [[item, count], ...]  (fluids: their bucket item);
//     item may be '#tag' or {any: [items]} (FTB Filter System smart filter), give such quests an icon,
//   dep: [keys]  (may point to other chapters), need: 'one' -> any one dependency is enough,
//   opt: true (optional side quest, hexagon), main: true (milestone, bigger gear),
//   r: [[item, count]], xp: levels, box: reward table key, hideLines: true,
//   icon: item (default: first task item).
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.join(__dirname, '..', '..');
const OUT = path.join(ROOT, 'overrides/common/config/ftbquests/quests');
const CHECK_ONLY = process.argv.includes('--check');

// ---------- item registry ----------
const registered = new Set(fs.readFileSync(path.join(ROOT, 'tools/registered-items.txt'), 'utf8').split(/\r?\n/).filter(Boolean));
const STARTUP = path.join(ROOT, 'overrides/common/kubejs/startup_scripts');
for (const f of fs.readdirSync(STARTUP)) {
  const src = fs.readFileSync(path.join(STARTUP, f), 'utf8');
  for (const m of src.matchAll(/create\(\s*["']([a-z0-9_]+)["']/g)) registered.add('kubejs:' + m[1]);
  if (f === 'rework_items.js') for (const m of src.matchAll(/\[\s*'([a-z0-9_]+)'\s*,\s*'/g)) registered.add('kubejs:' + m[1]);
}
const problems = [];
for (const id of JSON.parse(fs.readFileSync(path.join(ROOT,'overrides/common/kubejs/config/ladder-modules.json'),'utf8')).modules) registered.add('kubejs:'+id);
const checkItem = (id, where) => { if (!registered.has(id)) problems.push('unknown item ' + id + ' (' + where + ')'); };

// ---------- helpers ----------
const usedIds = new Set();
function hexId(name) {
  let h = crypto.createHash('sha1').update(name).digest('hex').slice(0, 16).toUpperCase();
  h = '01234567'['0123456789ABCDEF'.indexOf(h[0]) & 7] + h.slice(1);
  if (usedIds.has(h)) throw new Error('id clash ' + name);
  usedIds.add(h);
  return h;
}
const q = s => JSON.stringify(s);
function snbt(v, ind = '') {
  if (v && v.__raw !== undefined) return v.__raw;
  if (Array.isArray(v)) return v.length ? '[\n' + v.map(x => ind + '\t' + snbt(x, ind + '\t')).join('\n') + '\n' + ind + ']' : '[ ]';
  if (v && typeof v === 'object') {
    const keys = Object.keys(v).sort();
    return keys.length ? '{\n' + keys.map(k => ind + '\t' + (/^[A-Za-z0-9_]+$/.test(k) ? k : q(k)) + ': ' + snbt(v[k], ind + '\t')).join('\n') + '\n' + ind + '}' : '{ }';
  }
  return typeof v === 'string' ? q(v) : String(v);
}
const L = n => ({__raw: n + 'L'}), D = n => ({__raw: (Number.isInteger(n) ? n.toFixed(1) : String(n)) + 'd'});
const stack = (id, count = 1) => ({count: count, id: id});
// Task item spec: 'mod:item' | '#tag' (any item of the tag) | {any: ['mod:a', 'mod:b']} (any of them).
// Tags and lists become an FTB Filter System smart filter.
function taskStack(spec, where) {
  if (typeof spec === 'string' && spec[0] !== '#') { checkItem(spec, where); return stack(spec, 1); }
  let filter;
  if (typeof spec !== 'string') spec.any.forEach(i => checkItem(i, where));
  filter = require('./filters')(spec);
  return {count: 1, id: 'ftbfiltersystem:smart_filter', components: {'ftbfiltersystem:filter': filter}};
}
const specIcon = spec => typeof spec === 'string' ? (spec[0] === '#' ? null : spec) : spec.any[0];

// ---------- load data ----------
const TABLES = require('./tables.js');
const GROUPS = [['main', 'Основной путь'], ['magic', 'Магия'], ['side', 'Снаряжение и мир']];
const CHAPTERS = require('./load')();
problems.push(...require('./validate')(CHAPTERS));

const lang = {}, files = {}, tableIds = {}, groupIds = {}, allQuests = {};
for (const [k, title] of GROUPS) { groupIds[k] = hexId('group:' + k); lang['chapter_group.' + groupIds[k] + '.title'] = title; }
TABLES.forEach((tb, i) => {
  const id = hexId('table:' + tb.k);
  tableIds[tb.k] = BigInt('0x' + id).toString();
  lang['reward_table.' + id + '.title'] = tb.t;
  tb.items.forEach(e => checkItem(e[0], 'table ' + tb.k));
  files['reward_tables/' + tb.k + '.snbt'] = {id: id, loot_size: 1, hide_tooltip: false, use_title: true, order_index: i,
    rewards: tb.items.map(e => ({item: stack(e[0], e[1]), weight: D(e[2] || 1)}))};
});
for (const ch of CHAPTERS) {
  ch.id = hexId('chapter:' + ch.k);
  for (const qu of ch.quests) {
    if (allQuests[qu.k]) throw new Error('duplicate quest key ' + qu.k);
    qu.id = hexId('quest:' + qu.k); qu._ch = ch; allQuests[qu.k] = qu;
  }
}

// ---------- layout check ----------
// Draws every dependency inside a chapter as a straight segment between quest centres and reports
// segments passing through another quest, and quests placed on top of each other.
function layoutCheck(ch) {
  const pts = ch.quests.map(qu => ({k: qu.k, x: qu.at[0], y: qu.at[1], r: (qu.main ? 0.75 : 0.55)}));
  for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
    const a = pts[i], b = pts[j];
    if (Math.hypot(a.x - b.x, a.y - b.y) < 1.2) problems.push(ch.k + ': quests too close ' + a.k + ' / ' + b.k);
  }
  const segs = [];
  for (const qu of ch.quests) for (const d of qu.dep || []) {
    const p = allQuests[d];
    if (!p || p._ch !== ch || qu.hideLines) continue;
    segs.push({a: p, b: qu});
  }
  for (const s of segs) {
    const [x1, y1] = s.a.at, [x2, y2] = s.b.at;
    for (const pt of pts) {
      if (pt.k === s.a.k || pt.k === s.b.k) continue;
      const dx = x2 - x1, dy = y2 - y1, len2 = dx * dx + dy * dy;
      const t = Math.max(0, Math.min(1, ((pt.x - x1) * dx + (pt.y - y1) * dy) / len2));
      const dist = Math.hypot(x1 + t * dx - pt.x, y1 + t * dy - pt.y);
      if (t > 0 && t < 1 && dist < pt.r) problems.push(ch.k + ': line ' + s.a.k + ' -> ' + s.b.k + ' passes through ' + pt.k);
    }
  }
  // collinear overlapping segments
  for (let i = 0; i < segs.length; i++) for (let j = i + 1; j < segs.length; j++) {
    const s = segs[i], u = segs[j];
    const v1 = [s.b.at[0] - s.a.at[0], s.b.at[1] - s.a.at[1]], v2 = [u.b.at[0] - u.a.at[0], u.b.at[1] - u.a.at[1]];
    const cross = v1[0] * v2[1] - v1[1] * v2[0];
    if (Math.abs(cross) > 1e-6) continue;
    const w = [u.a.at[0] - s.a.at[0], u.a.at[1] - s.a.at[1]];
    if (Math.abs(v1[0] * w[1] - v1[1] * w[0]) > 1e-6) continue;
    const proj = p => ((p[0] - s.a.at[0]) * v1[0] + (p[1] - s.a.at[1]) * v1[1]) / (v1[0] * v1[0] + v1[1] * v1[1]);
    const lo = Math.min(proj(u.a.at), proj(u.b.at)), hi = Math.max(proj(u.a.at), proj(u.b.at));
    if (hi > 0.01 && lo < 0.99) problems.push(ch.k + ': lines overlap ' + s.a.k + '->' + s.b.k + ' and ' + u.a.k + '->' + u.b.k);
  }
}

// ---------- build ----------
let questCount = 0;
CHAPTERS.forEach((ch, ci) => {
  lang['chapter.' + ch.id + '.title'] = ch.t;
  if (ch.s) lang['chapter.' + ch.id + '.chapter_subtitle'] = [ch.s];
  checkItem(ch.icon, 'chapter icon ' + ch.k);
  layoutCheck(ch);
  const quests = ch.quests.map(qu => {
    questCount++;
    for (const d of qu.dep || []) if (!allQuests[d]) problems.push('unknown dep ' + d + ' in ' + qu.k);
    if (!qu.at) problems.push('no position for ' + qu.k);
    lang['quest.' + qu.id + '.title'] = qu.t;
    if (qu.s) lang['quest.' + qu.id + '.quest_subtitle'] = qu.s;
    if (qu.d) lang['quest.' + qu.id + '.quest_desc'] = qu.d;
    const tasks = [];
    const list = qu.task === 'check' ? [] : (Array.isArray(qu.task[0]) ? qu.task : [qu.task]);
    if (qu.task === 'check') tasks.push({id: hexId('task:' + qu.k), type: 'checkmark'});
    list.forEach((t, ti) => {
      const task = {id: hexId('task:' + qu.k + ':' + ti), type: 'item', item: taskStack(t[0], 'quest ' + qu.k), count: L(t[1] || 1)};
      tasks.push(task);
    });
    const rewards = [];
    (qu.r || []).forEach((r, ri) => { checkItem(r[0], 'reward ' + qu.k); rewards.push({id: hexId('reward:' + qu.k + ':' + ri), type: 'item', item: stack(r[0], r[1] || 1)}); });
    if (qu.xp) rewards.push({id: hexId('reward:' + qu.k + ':xp'), type: 'xp_levels', xp_levels: qu.xp});
    if (qu.xpPoints) rewards.push({id: hexId('reward:' + qu.k + ':xp_points'), type: 'xp', xp: qu.xpPoints});
    if (qu.box) { if (!tableIds[qu.box]) problems.push('unknown table ' + qu.box); else rewards.push({id: hexId('reward:' + qu.k + ':box'), type: 'random', table_id: L(tableIds[qu.box])}); }
    const out = {id: qu.id, x: D(qu.at ? qu.at[0] : 0), y: D(qu.at ? qu.at[1] : 0), tasks: tasks, rewards: rewards};
    if (qu.dep && qu.dep.length) out.dependencies = qu.dep.map(d => allQuests[d] ? allQuests[d].id : d);
    if (qu.need === 'one') out.dependency_requirement = 'one_completed';
    if (qu.hideLines) out.hide_dependency_lines = true;
    if (qu.opt) { out.optional = true; out.shape = 'hexagon'; }
    if (qu.main) { out.shape = 'gear'; out.size = D(1.5); }
    if (qu.task === 'check' && !qu.main && !qu.opt) out.shape = 'rsquare';
    const icon = qu.icon || (list[0] && specIcon(list[0][0]));
    if (icon) { checkItem(icon, 'icon ' + qu.k); out.icon = stack(icon, 1); }
    return out;
  });
  // links to quests of other chapters that this chapter depends on (shown at their position)
  const links = (ch.links || []).map((l, li) => {
    if (!allQuests[l.k]) problems.push('unknown link ' + l.k);
    return {id: hexId('link:' + ch.k + ':' + l.k + (li ? ':' + li : '')), linked_quest: allQuests[l.k] ? allQuests[l.k].id : '', x: D(l.at[0]), y: D(l.at[1]), shape: 'circle', size: D(1.0)};
  });
  files['chapters/' + ch.k + '.snbt'] = {
    id: ch.id, filename: ch.k, group: groupIds[ch.group], order_index: ci, icon: stack(ch.icon, 1),
    default_quest_shape: '', default_hide_dependency_lines: false, hide_quest_until_deps_complete: ch.strict !== false,
    hide_quest_until_deps_visible: false, quest_links: links, quests: quests,
    images: (ch.images||[]).map(im=>({id:hexId('image:'+ch.k+':'+im.key),x:D(im.x),y:D(im.y),width:D(im.w),height:D(im.h),
      // ChapterImageButton.withColor replaces Color4I's original colour when alpha is applied.
      // Put the tint in ChapterImage.color rather than relying on the icon's own colour.
      image:'#FFFFFF',color:parseInt(im.color.slice(1),16),alpha:245,order:im.text?-90:-100,position_locked:true,click_action:'',
      ...(im.text?{hover:[im.text],text_on_image:true,text_inset:10,text_shadow:true,text_h_align:'center',text_v_align:'center'}:{})})),
  };
});
files['data.snbt'] = {version: 13, default_reward_team: false, default_consume_items: false,
  default_quest_shape: 'circle', default_quest_disable_jei: false, drop_loot_crates: false,
  grid_scale: D(0.5), pause_game: false, show_lock_icons: true, drop_book_on_death: false, fallback_locale: 'ru_ru'};
files['chapter_groups.snbt'] = {chapter_groups: GROUPS.map(g => ({id: groupIds[g[0]]}))};
const langOut = {};
Object.keys(lang).sort().forEach(k => langOut[k] = lang[k]);
files['lang/ru_ru.snbt'] = langOut;
files['lang/en_us.snbt'] = langOut;

if (problems.length) { console.error('PROBLEMS (' + problems.length + '):\n  ' + problems.join('\n  ')); process.exit(1); }
console.log('chapters', CHAPTERS.length, 'quests', questCount);
if (CHECK_ONLY) process.exit(0);
fs.rmSync(OUT, {recursive: true, force: true});
for (const [f, v] of Object.entries(files)) {
  const p = path.join(OUT, f);
  fs.mkdirSync(path.dirname(p), {recursive: true});
  let text = snbt(v);
  if (f.startsWith('lang/')) text = '{\n' + Object.keys(v).map(k => '\t' + q(k) + ': ' + snbt(v[k], '\t')).join('\n') + '\n}';
  fs.writeFileSync(p, text + '\n');
}
console.log('written to', OUT);
