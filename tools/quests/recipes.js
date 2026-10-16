// node tools/quests/recipes.js <dump.json> <item-id regex> [--uses]
const fs=require('fs');const [dumpF,pat,mode]=process.argv.slice(2);const d=JSON.parse(fs.readFileSync(dumpF,'utf8'));const re=new RegExp(pat);
const short=x=>{if(!x)return'';if(typeof x==='string')return x;if(Array.isArray(x))return x.map(short).join('|');
 if(x.item)return x.item+(x.amount||x.count?'x'+(x.amount||x.count):'')+(x.probability!==undefined&&x.probability<1?'@'+x.probability:'');
 if(x.tag)return '#'+x.tag+(x.amount||x.count?'x'+(x.amount||x.count):'');
 if(x.fluid)return 'FLUID '+x.fluid+' '+x.amount+'mb';
 if(x.id)return x.id+(x.count?'x'+x.count:'');
 if(x.ingredient)return short(x.ingredient)+(x.count?'x'+x.count:'');
 if(x.items)return short(x.items);return JSON.stringify(x).slice(0,80);};
for(const [id,r] of Object.entries(d)){const j=r.json;const s=JSON.stringify(j);
 const outs=JSON.stringify(j.result||j.results||j.item_outputs||j.fluid_outputs||j.output||j.outputs||'');
 const hit=mode==='--uses'? re.test(s.replace(outs,'')) : re.test(outs);
 if(!hit)continue;
 let line=id+' ['+r.type+']';
 if(j.eu)line+=' '+j.eu+'EU/t '+j.duration+'t';
 if(j.pattern)line+=' pattern='+JSON.stringify(j.pattern)+' key='+Object.entries(j.key).map(([k,v])=>k+':'+short(v)).join(',');
 if(j.ingredients)line+=' in='+short(j.ingredients);
 if(j.item_inputs)line+=' in='+short(j.item_inputs);
 if(j.fluid_inputs)line+=' fin='+short(j.fluid_inputs);
 if(j.item_outputs)line+=' out='+short(j.item_outputs);
 if(j.fluid_outputs)line+=' fout='+short(j.fluid_outputs);
 if(j.result)line+=' => '+short(j.result);
 if(!j.pattern&&!j.ingredients&&!j.item_inputs)line+=' '+s.slice(0,300);
 console.log(line);}
