// Regression checks for progression, recipe indexing and generator guardrails.
const assert=require('assert/strict'),load=require('./load'),validate=require('./validate'),C=require('./catalog');
const ch=load(), early=ch.slice(0,3);
assert.deepEqual(early.map(c=>c.quests.length),[40,93,100]);
assert.deepEqual(validate(ch),[]);
assert(C.members('minecraft:beds').includes('minecraft:red_bed'));
const bronze=C.sources('modern_industrialization:bronze_dust');
assert(bronze.some(r=>r.json.result?.count===3));
assert(bronze.some(r=>r.json.item_outputs?.[0]?.amount===4));
assert(C.sources('modern_industrialization:soldering_alloy_bucket').length>0);
assert(C.uses.get('modern_industrialization:bronze_plate')?.length>0);
assert(!C.name('minecraft:torch').includes(':'));
assert(early.every(c=>c.quests.every(q=>q.task==='check' ? q.completion||!q.xpPoints&&!q.box&&!q.r : q.xpPoints<=20)));
assert(!ch[0].quests.find(q=>q.k==='waystone').dep.includes('iron_tools'));
const copy=()=>structuredClone(load());
let bad=copy();bad[0].quests.find(q=>q.k==='wood').dep=['table'];
assert(validate(bad).some(e=>e.includes('cycle')));
bad=copy();bad[0].quests.find(q=>q.k==='welcome').xpPoints=500;
assert(validate(bad).some(e=>e.includes('reading reward')));
bad=copy();bad[0].links.push({k:'wood',at:[0,0]});
assert(validate(bad).some(e=>e.includes('overlap')||e.includes('aliases')));
const fixtures=[{k:'a',at:[0,0]},{k:'b',at:[4,4],dep:['a']},{k:'c',at:[0,4]},{k:'d',at:[4,0],dep:['c']}].map(q=>({...q,task:['minecraft:stone',1],xpPoints:3,d:['Test']}));
assert(validate([{k:'start',quests:fixtures}]).some(e=>e.includes('crossing')));
const G=require('./gear'),equipment=ch.flatMap(c=>c.quests).filter(q=>q.gear);
assert.equal(equipment.length,124);
assert(!equipment.some(q=>q.gear.group==='chest'&&q.gear.tier===11));
assert(!equipment.some(q=>q.task[0].any.includes('minecraft:shulker_shell')));
for(const q of equipment){
  assert.deepEqual(q.task[0].any,G.items(q.gear.group,q.gear.tier));
  const prev=ch.flatMap(c=>c.quests).find(p=>p.k===q.dep[0]);
  if(prev.gear){assert.equal(prev.gear.group,q.gear.group);assert(prev.gear.tier<q.gear.tier);}
  assert(q.xpPoints>=3&&q.xpPoints<=12);assert(q.r?.length&&!q.box);
}
assert.equal(ch.flatMap(c=>c.quests).filter(q=>/^gear_module_/.test(q.k)).length,G.modules.length);
for(let n=1;n<=8;n++)assert(ch.flatMap(c=>c.quests).some(q=>q.k===(n<=3?'core'+n:'gear_core'+n)));
bad=copy();bad.find(c=>c.k==='armor_ladder').quests.find(q=>q.gear).task[0].any.push('minecraft:stone');
assert(validate(bad).some(e=>e.includes('differs from registry')));
bad=copy();bad.find(c=>c.k==='weapon_ladder').quests=bad.find(c=>c.k==='weapon_ladder').quests.filter(q=>q.k!=='gear_shield_t10');
assert(validate(bad).some(e=>e.includes('coverage missing')));
assert(!ch.flatMap(c=>c.quests).flatMap(q=>q.d||[]).some(s=>s.includes('I–XIII')));
assert(ch.find(c=>c.k==='gear').quests.find(q=>q.k==='tiers').d.some(s=>s.includes('крафтов II–XI')));
assert(G.station(G.source('minecraft:iron_axe')).includes('5×5'));
assert(G.station(G.source('techreborn:nanosaber')).includes('3×3'));
assert(!ch.find(c=>c.k==='weapon_ladder').quests.find(q=>q.k==='gear_weapon_t12').d.some(s=>s.startsWith('Для этого примера допустимые основы')));
assert(ch.every(c=>!c.links.length));
for(const c of ch)for(const im of c.images){
  assert(/^#[0-9a-f]{6}$/i.test(im.color));
  assert.notEqual(im.color.toUpperCase(),'#FFFFFF');
  if(im.text)assert(im.h<=1,'Header can enlarge text beyond a safe size');
}
assert(ch.find(c=>c.k==='steam').quests.filter(q=>q.task!=='check'&&q.task[0]==='modern_industrialization:forge_hammer').length===1);
for(const c of ch)for(const q of c.quests)if(!q.hideLines)for(const dep of q.dep||[]){const p=ch.flatMap(c=>c.quests).find(p=>p.k===dep);assert(p.at[0]===q.at[0]||p.at[1]===q.at[1]);}
for(const c of ch)for(const q of c.quests){
  if(q.task!=='check')assert(q.r?.length,'Missing physical reward '+q.k);
  else if(!q.completion)assert(!q.r&&!q.xpPoints&&!q.box,'Reading reward '+q.k);
}
for(const tb of require('./tables'))for(const [id,n]of tb.items){assert(require('./rewards').allowed.has(id));assert(n<=32);}
bad=copy();bad[1].quests.find(q=>q.k==='hammer').r=[['kubejs:reborn_interface',64]];
assert(validate(bad).some(e=>e.includes('unsafe or excessive reward')));
bad=copy();delete bad[1].quests.find(q=>q.k==='hammer').r;
assert(validate(bad).some(e=>e.includes('physical reward missing')));
console.log('PASS: recipe index, progression, gear filters, geometry, physical rewards and reward budgets');
