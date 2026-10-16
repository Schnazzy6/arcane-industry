// Visual layout only. Quest keys, task IDs and gameplay dependency lists remain intact.
const plans={
  start:[
    ['Первые шаги','welcome wood table stone furnace iron copper tin start_done'],
    ['Лагерь и снаряжение','bed chest leather backpack waystone'],
    ['Кухня и рацион','food1 knife pot diet'],
    ['Подготовка к развитию','coal lead iron_tools notebook'],
  ],
  steam:[
    ['От молота до котла','hammer dusts bronze_dust bronze bplate casing tank boiler'],
    ['Первые машины','compressor pump steam_bucket macerator mixer bfurnace'],
    ['Медная механика','cparts cgear crotor curved pipes bgear'],
    ['Инструменты и магия','iron_hammer drill wrench mount_t'],
    ['Огнеупор и кокс','brick_dust fclay_dust fclay_brick fclay_bricks coke_oven coke'],
    ['Путь к стали','coke_dust steel_dust sbf steel steel_casing wiremill steam_done'],
    ['Смазка и резка','hatches creosote lubricant cutter barrel'],
    ['Обслуживание мастерской','upgrade packer trash quarry'],
  ],
  power:[
    ['Резина и изоляция','p_intro raw_oil synth_oil paper rubber wires cable'],
    ['Электроника LV','resistor capacitor inductor board analog'],
    ['Батареи и корпуса','antimony alloy battery hull'],
    ['Приводы и сборка','magnet motor piston conveyor arm assembler'],
    ['Энергия завода','turbine network storage diesel'],
    ['Электрический парк','emacer efurnace ewire emixer overclock cfg_chest'],
    ['Магия и сплавы','focus invar cupronickel polarizer'],
    ['Доменная печь','heatproof coils ebf ehatch power_done'],
  ],
};
const palette=['#365c78','#665338','#43634f','#625078'];
module.exports=chapters=>{
  const all=new Map(chapters.flatMap(c=>c.quests.map(q=>[q.k,q])));
  for(const ch of chapters){
    // QuestLink clones draw their own outgoing dependency lines. They caused the fans in-game.
    ch.links=[];ch.images=[];ch.strict=false;
    if(plans[ch.k]){
      const used=new Set(),sections=plans[ch.k].map(([title,keys])=>({title,keys:keys.split(' ')}));
      sections.forEach(s=>s.keys.forEach(k=>used.add(k)));
      for(const q of ch.quests)if(!used.has(q.k)){
        const title=q.section||'Дополнительные цели';
        let section=sections.find(s=>s.title===title);
        if(!section){section={title,keys:[]};sections.push(section);}
        section.keys.push(q.k);used.add(q.k);
      }
      const cards=sections.map((s,i)=>({...s,i,rows:Math.ceil(s.keys.length/6)}));
      let top=0;
      for(let i=0;i<cards.length;i+=2){
        const pair=cards.slice(i,i+2),height=Math.max(...pair.map(c=>c.rows))*3.5+3;
        pair.forEach((s,column)=>{
          const left=column*23,accent=palette[Math.floor(i/2)%palette.length];
          ch.images.push({key:'panel_'+s.i,x:left+8,y:top+height/2-0.6,w:20.5,h:height-0.5,color:'#172331'});
          ch.images.push({key:'heading_'+s.i,x:left+8,y:top,w:20.5,h:0.85,color:accent,text:`${String(s.i+1).padStart(2,'0')}  ${s.title}`});
          s.keys.forEach((key,n)=>{
            const q=ch.quests.find(q=>q.k===key);if(!q)throw Error('Unknown visual key '+key);
            // A snake keeps the wrap connection vertical instead of crossing the card.
            const row=Math.floor(n/6),col=row%2?5-n%6:n%6;
            q.at=[left+col*3.2,top+2+row*3.5];q.visualSection=s.title;
          });
        });
        top+=height+2;
      }
    }else{
      const xs=ch.quests.map(q=>q.at[0]),ys=ch.quests.map(q=>q.at[1]);
      ch.images.push({key:'chapter_heading',x:(Math.min(...xs)+Math.max(...xs))/2,y:Math.min(...ys)-3,
        w:Math.max(...xs)-Math.min(...xs)+4,h:0.85,color:palette[ch.group==='magic'?3:0],text:ch.t});
    }
    for(const q of ch.quests){
      const deps=(q.dep||[]).map(k=>all.get(k));
      // An incoming edge is visible only when every incoming edge is short and orthogonal.
      // Hidden prerequisites are still enforced and are written explicitly in the description.
      q.hideLines=deps.some(p=>!p||!ch.quests.includes(p)||
        (Math.abs(p.at[0]-q.at[0])>0.001&&Math.abs(p.at[1]-q.at[1])>0.001)||
        Math.hypot(p.at[0]-q.at[0],p.at[1]-q.at[1])>4.1);
      if(q.hideLines&&deps.length)q.d.push('','&6Открывается после&r: '+deps.filter(Boolean).map(p=>p.t).join('; ')+'.');
    }
  }
};
