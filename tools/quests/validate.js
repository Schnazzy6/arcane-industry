// Additional semantic and geometric checks; no game files are written here.
const C = require('./catalog');
module.exports = chapters => {
  const errors = [], quests = new Map(chapters.flatMap(c => c.quests.map(q => [q.k,q])));
  const visiting = new Set(), done = new Set();
  function visit(k) {
    if (visiting.has(k)) { errors.push('dependency cycle at '+k); return; }
    if (done.has(k) || !quests.has(k)) return;
    visiting.add(k);
    for (const dep of quests.get(k).dep || []) visit(dep);
    visiting.delete(k); done.add(k);
  }
  for (const k of quests.keys()) visit(k);
  for (const ch of chapters) {
    const early = ['start','steam','power'].includes(ch.k);
    const gear = ['gear','armor_ladder','weapon_ladder'].includes(ch.k);
    if (!early && !gear) continue;
    for (const q of ch.quests) {
      if (!q.d?.length) errors.push('description missing: '+q.k);
      if (q.task === 'check') {
        if (!q.completion && (q.xpPoints || q.xp || q.box || q.r?.length)) errors.push('reading reward: '+q.k);
        if(q.completion && (!(q.dep?.length)||q.dep.some(k=>quests.get(k)?.task==='check')))errors.push('completion requires real item goals: '+q.k);
        continue;
      }
      for (const [spec, count] of Array.isArray(q.task[0]) ? q.task : [q.task]) {
        if (!Number.isInteger(count) || count < 1) errors.push('invalid task count: '+q.k);
        if (typeof spec === 'string' && spec.startsWith('#') && !C.members(spec.slice(1)).length) errors.push('empty or unavailable tag: '+spec+' in '+q.k);
        if ((q.k.startsWith('part_') || /^[ps]_/.test(q.k)) && typeof spec === 'string' && !C.sources(spec).length) errors.push('no recipe source: '+spec+' in '+q.k);
      }
      if (!q.xpPoints && !q.r?.length && !q.box) errors.push('reward missing: '+q.k);
      if (q.xp || q.xpPoints > (gear ? 12 : 20)) errors.push('XP exceeds budget: '+q.k);
      if (gear && q.box) errors.push('gear must not award random progression loot: '+q.k);
      if (q.gear) {
        const expected = require('./gear').items(q.gear.group,q.gear.tier);
        const actual = q.task[0]?.any;
        if (!actual?.length || new Set(actual).size!==actual.length || JSON.stringify([...actual].sort())!==JSON.stringify(expected))
          errors.push('gear filter differs from registry: '+q.k);
        if (q.task[1]!==1) errors.push('gear task must require one item: '+q.k);
      }
    }
    const points = ch.quests.map(q => ({k:q.k, at:q.at})).concat((ch.links||[]).map((l,i) => ({k:'link'+i,at:l.at})));
    for (let i=0;i<points.length;i++) for(let j=i+1;j<points.length;j++)
      if (Math.hypot(points[i].at[0]-points[j].at[0],points[i].at[1]-points[j].at[1]) < 1.2)
        errors.push(ch.k+': linked node overlap '+points[i].k+'/'+points[j].k);
    const segments = ch.quests.flatMap(q => q.hideLines ? [] : (q.dep||[]).filter(k => ch.quests.some(p=>p.k===k)).map(k=>({a:quests.get(k),b:q})));
    const cross = (a,b,c) => (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
    for(let i=0;i<segments.length;i++) for(let j=i+1;j<segments.length;j++) {
      const s=segments[i],t=segments[j];
      if(cross(s.a.at,s.b.at,t.a.at)*cross(s.a.at,s.b.at,t.b.at)<-1e-8 && cross(t.a.at,t.b.at,s.a.at)*cross(t.a.at,t.b.at,s.b.at)<-1e-8)
        errors.push(ch.k+': crossing '+s.a.k+'->'+s.b.k+' / '+t.a.k+'->'+t.b.k);
    }
  }
  for(const ch of chapters){
    for(const q of ch.quests){
      if(q.task!=='check'&&!q.r?.length)errors.push('physical reward missing: '+q.k);
      if(q.xp)errors.push('reward must use fixed XP points: '+q.k);
      if(q.box&&!q.completion)errors.push('random reward outside completion: '+q.k);
      for(const [id,n] of q.r||[])if(!require('./rewards').allowed.has(id)||!Number.isInteger(n)||n<1||n>32)errors.push('unsafe or excessive reward: '+q.k);
    }
    if(ch.links?.length)errors.push('quest aliases can draw duplicate edges: '+ch.k);
    for(const q of ch.quests)if(!q.hideLines)for(const key of q.dep||[]){
      const p=quests.get(key);
      if(!p)continue;
      if(p.at[0]!==q.at[0]&&p.at[1]!==q.at[1])errors.push('visible diagonal: '+key+' -> '+q.k);
      if(Math.hypot(p.at[0]-q.at[0],p.at[1]-q.at[1])>4.1)errors.push('visible long edge: '+key+' -> '+q.k);
    }
  }
  if (chapters.some(c=>c.k==='armor_ladder')) {
    const G=require('./gear'),matrix=chapters.flatMap(c=>c.quests).filter(q=>q.gear);
    for(const [group] of G.groups) for(const tier of G.tiers(group))
      if(matrix.filter(q=>q.gear.group===group&&q.gear.tier===tier).length!==1)
        errors.push('gear coverage missing or repeated: '+group+' '+tier);
    for(const q of chapters.flatMap(c=>c.quests))if(/^gear_module_|^gear_core[4-8]$|^core[1-3]$/.test(q.k))
      if(!C.sources(q.task[0]).length)errors.push('gear component has no recipe: '+q.k);
  }
  return errors;
};
