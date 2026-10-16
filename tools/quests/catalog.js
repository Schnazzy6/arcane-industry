// Recipe index shared by authoring, descriptions and the command-line inspector.
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '../..');
const dump = JSON.parse(fs.readFileSync(path.join(root, 'build/server/kubejs/config/recipe-dump.json'), 'utf8'));
const lang = JSON.parse(fs.readFileSync(path.join(root, 'build/quest-languages.json'), 'utf8'));
const tags = JSON.parse(fs.readFileSync(path.join(root, 'build/quest-tags.json'), 'utf8'));
function members(tag, seen = new Set()) {
  if (seen.has(tag)) return [];
  const next = new Set(seen); next.add(tag);
  return [...new Set((tags[tag] || []).flatMap(v => {
    const id = typeof v === 'string' ? v : v.id;
    return id.startsWith('#') ? members(id.slice(1), next) : [id];
  }))];
}
function name(id) {
  const module=id.match(/^kubejs:(tech_module|aura_seed|dark_essence|spirit_contract)_t(\d+)$/);
  if(module) return ({tech_module:'Технический модуль',aura_seed:'Семя ауры',dark_essence:'Тёмная эссенция',spirit_contract:'Договор духа'})[module[1]]+' тира '+['','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII'][+module[2]];
  if (id.startsWith('#')) return 'тег ' + id.slice(1);
  const [ns, p] = id.split(':');
  const keys = ['item.', 'block.', 'fluid.'].map(k => k + ns + '.' + p.replaceAll('/', '.'));
  for (const l of ['ru_ru', 'en_us']) for (const k of keys) if (lang[l][k]) return lang[l][k];
  if (!p.endsWith('_bucket')) {
    for (const l of ['ru_ru', 'en_us']) for (const prefix of ['item.', 'block.']) {
      const k = prefix + ns + '.' + p + '_bucket';
      if (lang[l][k]) return lang[l][k].replace(/Ведро (с )?/i, '').replace(/ Bucket$/, '');
    }
  }
  return id;
}
function refs(value, result = []) {
  if (typeof value === 'string' && /^[a-z0-9_]+:[a-z0-9_/.-]+$/.test(value)) result.push(value);
  else if (Array.isArray(value)) value.forEach(v => refs(v, result));
  else if (value && typeof value === 'object') {
    if (value.tag) result.push('#' + value.tag);
    for (const [k,v] of Object.entries(value)) if (k !== 'tag' && k !== 'type') refs(v, result);
  }
  return [...new Set(result)];
}
const produces = new Map(), uses = new Map(), records = [];
for (const [id, r] of Object.entries(dump).sort(([a],[b]) => a.localeCompare(b))) {
  const j = r.json;
  const output = refs([j.result, j.results, j.item_outputs, j.fluid_outputs, j.output, j.outputs]);
  const input = refs([j.key, j.ingredients, j.ingredient, j.item_inputs, j.fluid_inputs, j.input, j.inputs, j.reagent, j.pedestalItems]);
  const rec = {id, type: j.type || r.type, input, output, eu: j.eu ?? j.power, duration: j.duration ?? j.time, json: j};
  records.push(rec);
  for (const item of output) { if (!produces.has(item)) produces.set(item, []); produces.get(item).push(rec); }
  for (const item of input) { if (!uses.has(item)) uses.set(item, []); uses.get(item).push(rec); }
}
for (const [tag, recipes] of [...uses]) if (tag.startsWith('#')) for (const item of members(tag.slice(1))) {
  if (!uses.has(item)) uses.set(item, []);
  uses.set(item, [...new Set([...uses.get(item), ...recipes])]);
}
function description(item) {
  const products = [...new Set((uses.get(item) || []).flatMap(r => r.output))].filter(x => x !== item && !x.startsWith('#'));
  if (!products.length) return 'Применение: смотрите U в JEI; специальные механики модов могут отсутствовать в выгрузке рецептов.';
  return '&6Где пригодится&r: ' + products.slice(0, 6).map(name).join(', ') + (products.length > 6 ? ' и другие рецепты.' : '.');
}
function sources(item) {
  const fluid = item.endsWith('_bucket') ? item.slice(0,-7) : item;
  return [...(produces.get(item) || []), ...(fluid !== item ? produces.get(fluid) || [] : [])]
    .filter(r => !/scrapbox|recycling|:unpacker$/.test(r.type));
}
const stations = {assembler:'Сборщик MI', mixer:'Смеситель MI', compressor:'Компрессор MI', macerator:'Измельчитель MI',
  cutting_machine:'Режущий станок MI', wiremill:'Волочильный станок MI', furnace:'Печь MI', packer:'Упаковщик MI',
  forge_hammer:'Кузнечный молот MI', polarizer:'Поляризатор MI', alloy_smelter:'Плавильня сплавов',
  crafting_shaped:'Верстак', crafting_shapeless:'Верстак', smelting:'Печь', blasting:'Плавильная печь',
  steam_blast_furnace:'Паровая доменная печь', electric_blast_furnace:'Электрическая доменная печь',
  cutting:'Разделочная доска', cooking:'Кастрюля Farmer’s Delight', coke_oven:'Коксовая печь',
  shaped_table:'Верстак Avaritia (размер смотрите в JEI)', tree_ritual:'Древесный ритуал Nature’s Aura',ritual:'Ритуальная станция своей школы',
  enchanting_apparatus:'Аппарат зачарований Ars',spirit_infusion:'Духовный алтарь Malum'};
function recipeLines(r) {
  const j = r.json, type = r.type.split(':')[1];
  const station = stations[type] || name(r.type);
  function ingredient(v) {
    if (Array.isArray(v)) return '(' + v.map(ingredient).join(' или ') + ')';
    if (typeof v === 'string') return name(v);
    if (!v) return '';
    const id = v.item || v.id || v.fluid || (v.tag ? '#'+v.tag : null);
    if (!id) return v.ingredient ? ingredient(v.ingredient) : 'ингредиент из JEI';
    return name(id) + (v.fluid ? ' — ' + (v.amount || 1) + ' мВ' : ' ×' + (v.amount || v.count || 1)) +
      (v.probability !== undefined && v.probability < 1 ? ' (шанс '+Math.round(v.probability*100)+'%)' : '');
  }
  let ingredients = j.item_inputs || j.ingredients;
  if (j.pattern && j.key) {
    const counts = {};
    for (const row of j.pattern) for (const key of row) if (key !== ' ') counts[key] = (counts[key] || 0)+1;
    ingredients = Object.entries(counts).map(([k,n]) => {
      const v = j.key[k];
      return typeof v === 'object' && !Array.isArray(v) ? {...v, count:n} : v;
    });
  }
  const lines = ['&6Один из способов изготовления&r: ' + station +
    (r.eu !== undefined ? ', '+r.eu+' EU/т' : '') + (r.duration !== undefined ? ', '+(r.duration/20)+' с' : '') + '.'];
  if (ingredients) lines.push('Предметы: ' + ingredients.map(ingredient).join('; ') + '.');
  if (j.fluid_inputs) lines.push('Жидкости: ' + j.fluid_inputs.map(ingredient).join('; ') + '.');
  const outputs = j.item_outputs || j.fluid_outputs || (j.result ? [j.result] : null);
  if (outputs) lines.push('Выход: ' + outputs.map(ingredient).join('; ') + '.');
  return lines;
}
module.exports = {name, refs, produces, uses, records, description, sources, recipeLines, members};
if (require.main === module) {
  const item = process.argv[2];
  console.log(name(item));
  console.log(JSON.stringify((process.argv.includes('--uses') ? uses : produces).get(item) || [], null, 2));
}
