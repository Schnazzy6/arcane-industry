// Fixed, finite supplies. No machines, progression components or random rare jackpots.
const C=require('./catalog');
const pools={
  start:[['minecraft:bread',2],['minecraft:torch',4],['minecraft:oak_log',4],['minecraft:stick',8]],
  steam:[['minecraft:coal',4],['minecraft:iron_ingot',1],['minecraft:copper_ingot',2],['minecraft:glass',4],['minecraft:brick',4]],
  power:[['minecraft:iron_ingot',2],['minecraft:copper_ingot',2],['minecraft:redstone',2],['minecraft:glass',4],['minecraft:coal',8]],
  industry:[['minecraft:iron_ingot',4],['minecraft:copper_ingot',4],['minecraft:redstone',4],['minecraft:glass',8],['minecraft:gold_ingot',2]],
  late:[['minecraft:iron_ingot',8],['minecraft:gold_ingot',4],['minecraft:redstone',8],['minecraft:obsidian',4],['minecraft:diamond',1]],
  reborn:[['minecraft:gold_ingot',4],['minecraft:redstone',8],['minecraft:quartz',8],['minecraft:diamond',1]],
  infinity:[['minecraft:gold_ingot',8],['minecraft:diamond',2],['minecraft:quartz',16]],
  magic1:[['minecraft:paper',4],['minecraft:lapis_lazuli',2],['minecraft:amethyst_shard',2],['minecraft:candle',2]],
  magic2:[['minecraft:paper',8],['minecraft:lapis_lazuli',4],['minecraft:amethyst_shard',4],['minecraft:gold_ingot',2]],
  explore:[['minecraft:cooked_beef',4],['minecraft:torch',8],['minecraft:arrow',16],['minecraft:bread',4]],
  gear:[['minecraft:bread',2],['minecraft:torch',4]],
  armor_ladder:[['minecraft:iron_ingot',2],['minecraft:leather',2]],
  weapon_ladder:[['minecraft:coal',4],['minecraft:iron_ingot',2],['minecraft:paper',4]],
};
const boxes={start:'era0',steam:'era1',power:'era2',industry:'era3',late:'era4',reborn:'era5',magic1:'magic0',magic2:'magic1'};
function index(k,n){let h=0;for(const c of k)h=(h*31+c.charCodeAt(0))>>>0;return h%n;}
function gearReward(q){
  const {group,tier}=q.gear;
  if(tier===12)return ['minecraft:golden_apple',1];
  if(tier>=8)return ['minecraft:golden_carrot',2];
  if(group==='bow'||group==='crossbow')return ['minecraft:arrow',16];
  if(group==='pickaxe')return ['minecraft:coal',4];
  if(group==='axe')return ['minecraft:oak_log',4];
  if(group==='shovel')return ['minecraft:sand',8];
  if(group==='hoe')return ['minecraft:bone_meal',4];
  return tier<=3?['minecraft:bread',2]:['minecraft:cooked_beef',2];
}
const allowed=new Set(Object.values(pools).flat().map(r=>r[0]).concat(['minecraft:golden_apple','minecraft:golden_carrot','minecraft:arrow','minecraft:sand','minecraft:bone_meal']));
module.exports=chapters=>{
  const all=new Map(chapters.flatMap(c=>c.quests.map(q=>[q.k,q])));
  for(const ch of chapters)for(const q of ch.quests){
    if(q.task==='check'&&/_done$/.test(q.k)&&q.dep?.length&&q.dep.every(k=>all.get(k)?.task!=='check'))q.completion=true;
    const xp=q.xpPoints??(q.xp?Math.min(20,q.xp*3):q.main?12:5);
    delete q.r;delete q.box;delete q.xp;delete q.xpPoints;
    if(q.task==='check'&&!q.completion)continue;
    q.xpPoints=q.completion?20:Math.min(q.gear?12:20,Math.max(3,xp));
    const pool=pools[ch.k];if(!pool)throw Error('No reward pool for '+ch.k);
    const owned=typeof q.task?.[0]==='string'?q.task[0]:null;
    const choices=pool.filter(r=>r[0]!==owned);
    q.r=[q.gear?gearReward(q):[...choices[index(q.k,choices.length)]]];
    if(q.main||q.completion){
      const extra=ch.group==='magic'?['minecraft:paper',8]:['minecraft:torch',8];
      if(q.r[0][0]===extra[0])q.r[0][1]+=extra[1];else q.r.push(extra);
    }
    if(q.completion&&boxes[ch.k])q.box=boxes[ch.k];
    q.d=(q.d||['Получите предметы, указанные в задании. Они сохраняются в инвентаре.','R в JEI — рецепт, U — применение.']).map(s=>s.replace('Награда — 8 очков опыта, лично каждому игроку один раз.','Награда — опыт и припасы, лично каждому игроку один раз.')
      .replace('награда — фиксированные очки опыта','награда — опыт и припасы'));
    q.d.push('','&6Награда&r: '+q.r.map(([id,n])=>C.name(id)+' ×'+n).join(', ')+`; ${q.xpPoints} очков опыта.`+
      (q.box?' Также один случайный набор обычных припасов.':''),
      'Каждый участник команды получает награду лично, один раз. Повторяемая выдача не предусмотрена.');
  }
};
module.exports.allowed=allowed;
