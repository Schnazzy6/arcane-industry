// The actual equipment registry is the source of truth, including gaps between tiers.
const fs=require('fs'),path=require('path'),C=require('./catalog');
const ROOT=path.resolve(__dirname,'../..');
const data=JSON.parse(fs.readFileSync(path.join(ROOT,'overrides/common/kubejs/config/gear-tiers.json'),'utf8'));
const modules=JSON.parse(fs.readFileSync(path.join(ROOT,'overrides/common/kubejs/config/ladder-modules.json'),'utf8')).modules;
// The registry also assigns a head slot to this crafting material. It is not player armour.
const excluded={'minecraft:shulker_shell':'Реагент, а не шлем игрока'};
const groups=[
  ['head','Шлем','Шлемы','Защита головы. Сравнивайте броню, стойкость, эффекты и совместимость со своей школой магии.'],
  ['chest','Нагрудник','Нагрудники','Основной защитный слот. Крылья, заряд и магические свойства проверяйте отдельно от числового тира.'],
  ['legs','Поножи','Поножи','Подбирайте поножи под комплект и стиль боя; равный тир не означает одинаковые бонусы.'],
  ['feet','Ботинки','Ботинки','Обращайте внимание на мобильность и защиту от падения, а не только на броню.'],
  ['weapon','Оружие','Обычное оружие','Мечи и другое оружие этой группы. Урон за удар, скорость атаки и особые способности нужно сравнивать вместе.'],
  ['weapon_heavy','Тяжёлое оружие','Тяжёлое оружие','Молоты, крупные клинки и другие тяжёлые виды. Медленный удар требует дистанции и правильного момента.'],
  ['weapon_light','Лёгкое оружие','Лёгкое оружие','Кинжалы, рапиры и другие лёгкие виды. Проверяйте дальность и скорость; высокая частота ударов не всегда пробивает защиту.'],
  ['pickaxe','Кирка','Кирки','Проверьте уровень добычи и скорость на нужной породе. Электрические и универсальные инструменты могут относиться к этой группе.'],
  ['axe','Топор','Топоры','Топоры предназначены прежде всего для дерева. Боевые топоры могут относиться к отдельной группе оружия — смотрите список принимаемых предметов.'],
  ['shovel','Лопата','Лопаты','Лопата ускоряет работу с грунтом. Специальные режимы инструмента проверяйте до раскопок возле базы.'],
  ['hoe','Мотыга','Мотыги','Мотыга нужна ферме и обработке подходящих растительных блоков. Не требуется собирать все инструменты ради одной ветки.'],
  ['bow','Лук','Луки и родственные стрелковые предметы','Группа включает луки и отнесённые к ней особые стрелковые предметы. Боеприпасы и способ применения зависят от конкретной вещи.'],
  ['crossbow','Арбалет','Арбалеты','Проверьте боеприпас, зарядку и особые свойства. Между существующими тирами этой группы есть большие промежутки.'],
  ['shield','Щит','Щиты','Щит не блокирует любую атаку. Особые удары и заклинания могут требовать уклонения; учитывайте способности самого щита.'],
];
function items(group,tier) {
  return Object.keys(data.tiers).filter(id=>!excluded[id]&&data.group[id]===group&&data.tiers[id]===tier).sort();
}
function tiers(group){return Array.from({length:12},(_,i)=>i+1).filter(t=>items(group,t).length);}
function icon(list){return list.find(id=>id.startsWith('avaritia:'))||list.find(id=>id.startsWith('minecraft:'))||list.find(id=>id.startsWith('techreborn:'))||list[0];}
const stage={
  2:['modern_industrialization:bronze_plate','minecraft:leather','kubejs:armor_core_t1'],
  3:['modern_industrialization:iron_plate','kubejs:ritual_mount','kubejs:armor_core_t1'],
  4:['modern_industrialization:steel_plate','kubejs:electrical_focus','kubejs:armor_core_t2'],
  5:['modern_industrialization:stainless_steel_plate','kubejs:industrial_focus','kubejs:armor_core_t3'],
  6:['modern_industrialization:titanium_plate','kubejs:soul_stabilizer','kubejs:armor_core_t4'],
  7:['kubejs:enchanted_titanium_plate','kubejs:ritual_frame','kubejs:armor_core_t5'],
  8:['modern_industrialization:iridium_plate','kubejs:convergence_core','kubejs:armor_core_t6'],
  9:['modern_industrialization:iridium_plate','kubejs:engineering_matrix','kubejs:armor_core_t7'],
  10:['avaritia:crystal_matrix_ingot','kubejs:infinity_stabilizer','kubejs:armor_core_t7'],
  11:['avaritia:neutron_ingot','kubejs:boss_seal','kubejs:armor_core_t8'],
};
function station(r){
  if(!r)return 'Особый способ получения — проверьте JEI, справочник мода или трофейную добычу.';
  const type=r.type;
  if(type==='avaritia:shaped_table') {
    const width=Math.max(r.json.pattern?.length||0,...(r.json.pattern||[]).map(row=>row.length));
    const size=({1:'3×3',2:'5×5',3:'7×7',4:'9×9'})[r.json.tier]||(width>7?'9×9':width>5?'7×7':width>3?'5×5':'смотрите размер сетки в JEI');
    return 'Верстак Avaritia: '+size+'.';
  }
  const map={'minecraft:crafting_shaped':'Обычный верстак 3×3','minecraft:crafting_shapeless':'Обычный верстак 3×3',
    'kubejs:shaped':'Обычный верстак 3×3','kubejs:shapeless':'Обычный верстак 3×3',
    'modern_industrialization:assembler':'Сборщик MI','ars_nouveau:enchanting_apparatus':'Аппарат зачарований Ars',
    'malum:spirit_infusion':'Духовный алтарь Malum','eidolon_repraised:crucible':'Тигель Eidolon',
    'eidolon_repraised:ritual':'Ритуал Eidolon','occultism:ritual':'Ритуал Occultism',
    'naturesaura:tree_ritual':'Древесный ритуал Nature’s Aura','goety:ritual':'Тёмный алтарь Goety'};
  return (map[type]||'Специальная станция из категории JEI')+'.'+(r.eu!==undefined?' '+r.eu+' EU/т.':'');
}
function source(item){return C.sources(item).find(r=>r.id.startsWith('kubejs:rework/ladder/'))||C.sources(item)[0];}
function description(group,tier,list){
  const def=groups.find(g=>g[0]===group),rt=data.roman[tier];
  const result=[`Получите один предмет группы «${def[2]}» строго тира &e${rt}&r. Принимается любая из ${list.length} вещей в фильтре задания.`,
    '',def[3],'',
    'Иконка — пример, а не единственный вариант. Чары, аффиксы, имя, повреждение и заряд не меняют принадлежность предмета к этому фильтру.',
    'Для надёжного зачёта положите вещь в обычный инвентарь. Предмет не изымается; надетую броню или вещь в отдельном хранилище при необходимости переложите в инвентарь.'];
  if(tier===1)result.push('','Это начальная ступень. Подойдёт сделанная или найденная вещь из списка; дорогие компоненты не требуются для самого зачёта.');
  else if(tier===12)result.push('','Финальный тир XII. У разных предметов свои рецепты и предшественники; универсального каркаса T12 нет. Подготовьте цепочки Бесконечности и смотрите полный рецепт выбранной вещи.');
  else result.push('','Детали обычной ступени этого этапа: '+stage[tier].map(C.name).join(', ')+'. Это ориентир, а не рецепт всех вещей: точный состав и расход смотрите в JEI.',
    'Столы обычной лестницы: II — 3×3, III — 5×5, IV–VI — 7×7, VII–XI — 9×9. Магические станции и модульная сборка могут заменять стол.');
  // Computed base tags also exist for trophies/final gear; only ladder recipes actually use them.
  const crafted=tier<12?list.find(id=>data.base[id]?.length&&source(id)?.id.startsWith('kubejs:rework/ladder/')):null;
  const example=crafted||icon(list),recipe=source(example);
  result.push('','&6Пример&r: '+C.name(example)+'. '+station(recipe));
  if(crafted) {
    const bases=data.base[crafted];
    result.push('Для этого примера допустимые основы: '+bases.slice(0,3).map(C.name).join(', ')+(bases.length>3?' и другие из тега рецепта.':'.'),
      'Основа подбирается для конкретной вещи. Это ближайший доступный более низкий тир той же группы; иногда более слабой основы нет.');
    const mod=recipe?.input.find(id=>/^kubejs:(tech_module|dark_essence|spirit_contract|aura_seed)_t/.test(id));
    if(mod)result.push('Сначала изготовьте '+C.name(mod)+' на его станции, затем соберите вещь из основы, модуля и материала.');
  }else if(!recipe)result.push('Наличие вещи в тире не означает наличие рецепта: возможны трофеи и особые способы получения. Выбирайте подходящий вам вариант из фильтра.');
  if(tier<=7)result.push('','Крафт и подходящие находки равноправны для задания. Тир обычной сундуковой добычи зависит от уровня мира, технологической эры и опасности места.');
  else result.push('','Обычная сундуковая инъекция лестницы не выдаёт тир VIII и выше. Для выбранной вещи проверяйте крафт, босса или иной особый источник.');
  const next=tiers(group).find(t=>t>tier);
  result.push('','&6Где пригодится&r: '+(next?`развитие группы до следующей существующей ступени ${data.roman[next]}. Не каждая вещь автоматически является основой любой следующей: проверяйте тег основы в рецепте.`:'верхняя существующая ступень этой группы; дальше улучшайте подходящие чары, аффиксы и самоцветы.'),
    'R в JEI — рецепт, U — применение. Прогресс общий для команды FTB Teams, награда личная и одноразовая. Не нужно собирать каждую альтернативу из фильтра.');
  return result;
}
function chapter(armor){
  const defs=groups.filter((_,i)=>armor?i<4:i>=4),quests=[];
  const ch={k:armor?'armor_ladder':'weapon_ladder',order:armor?20.1:20.2,group:'side',strict:false,
    t:armor?'Лестница брони':'Лестница оружия и инструментов',
    s:'Любая подходящая вещь каждого существующего типа и тира I–XII',
    icon:armor?'minecraft:iron_chestplate':'minecraft:iron_sword',quests,links:[{k:'tiers',at:[-6,-4]}]};
  defs.forEach((g,i)=>{
    const available=tiers(g[0]),missing=Array.from({length:12},(_,j)=>j+1).filter(t=>!available.includes(t));
    const intro='gear_intro_'+g[0];
    quests.push({k:intro,t:g[2],at:[-3,i*4],task:'check',dep:['tiers'],hideLines:true,opt:true,icon:icon(items(g[0],available[0])),
      d:[g[3],'','Тиры этой группы: '+available.map(t=>data.roman[t]).join(', ')+'.',
        missing.length?'В текущем реестре отсутствуют: '+missing.map(t=>data.roman[t]).join(', ')+'. Для пустых ступеней заданий нет, линия переходит к следующей существующей.':'В этой группе представлены все двенадцать тиров.',
        'Тип и тир берутся из действующего реестра сборки. Не определяйте их по названию материала: например, части одного набора могут иметь разные тиры.',
        'Каждая строка самостоятельна. Эта глава не требует собрать все классы оружия или полную коллекцию вариантов для продолжения основной истории.']});
    available.forEach((tier,j)=>{
      const list=items(g[0],tier);
      quests.push({k:`gear_${g[0]}_t${tier}`,t:`${g[1]} тира ${data.roman[tier]}`,at:[(tier-1)*3,i*4],
        task:[{any:list},1],icon:icon(list),dep:[j?`gear_${g[0]}_t${available[j-1]}`:intro],opt:true,
        xpPoints:tier<=3?3:tier<=7?5:tier<=11?8:12,d:description(g[0],tier,list),
        gear:{group:g[0],tier}});
    });
  });
  if(armor)for(let t=1;t<=8;t++){
    const id='kubejs:armor_core_t'+t,recipe=source(id);
    if(!recipe)throw Error('Missing core recipe '+id);
    const key=t<=3?'core'+t:'gear_core'+t;
    const used=Object.entries(stage).filter(([,parts])=>parts.includes(id)).map(([n])=>data.roman[+n]);
    quests.push({k:key,t:'Каркас брони T'+t,at:[(t-1)*3,20],task:[id,1],icon:id,opt:true,
      dep:t===1?['tiers']:[t===2?'core1':t===3?'core2':t===4?'core3':'gear_core'+(t-1)],hideLines:t===1,
      xpPoints:t<=2?5:8,d:['Получите один каркас. Не нужно сдавать четыре предмета: для знакомства с компонентом достаточно одного.',
        '', 'Каркас T'+t+' и тир снаряжения '+data.roman[t]+' — разные обозначения. В обычных ступенях этот каркас относится к тирам '+used.join(', ')+'.',
        '',station(recipe),...C.recipeLines(recipe),'',C.description(id),
        'Количество для полного комплекта и конкретного рецепта смотрите в JEI. Предмет сохраняется, награда — фиксированные очки опыта один раз каждому игроку.']});
  }
  else {
    const kinds=[['tech_module','Технические модули','Сборщик MI'],['aura_seed','Семена ауры','Древесный ритуал Nature’s Aura'],
      ['dark_essence','Тёмные эссенции','Тёмный алтарь Goety'],['spirit_contract','Договоры духов','Ритуал Occultism']];
    kinds.forEach(([kind,title,where],i)=>{
      const active=modules.filter(x=>x.startsWith(kind+'_t')).sort((a,b)=>parseInt(a.split('_t').pop())-parseInt(b.split('_t').pop()));
      active.forEach((m,j)=>{
        const id='kubejs:'+m,t=+m.split('_t').pop(),recipe=source(id);
        if(!recipe)throw Error('Missing module recipe '+id);
        quests.push({k:'gear_module_'+m,t:title+': '+data.roman[t],at:[(t-1)*3,44+i*4],task:[id,1],icon:id,opt:true,
          dep:j?['gear_module_'+active[j-1]]:['modules'],hideLines:!j,xpPoints:t<=7?5:8,
          d:['Изготовьте один модуль тира '+data.roman[t]+'. Станция: '+where+'.',
            '', 'Модуль — промежуточная деталь. После станции он соединяется на обычном верстаке с подходящей основой и материалом вещи. Сам модуль не заменяет снаряжение.',
            '',...C.recipeLines(recipe),'',C.description(id),
            'Показаны только реально зарегистрированные и используемые модули. Не нужно искать модуль каждого семейства на каждом тире.',
            'R в JEI — полный рецепт модуля и станции. Предмет не изымается; награда личная и одноразовая.']});
      });
    });
  }
  return ch;
}
module.exports={data,modules,excluded,groups,items,tiers,icon,source,station,chapter};
