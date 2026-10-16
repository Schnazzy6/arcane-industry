// Preserve IDs and progress: redundant collection tasks become un-rewarded practical notes.
module.exports=chapters=>{
  const all=new Map(chapters.flatMap(c=>c.quests.map(q=>[q.k,q])));
  const notes={
    p_series_gears:['cgear','Серийная сборка шестерён'],
    overclock:['lubricant','Как разгонять машины смазкой'],
    mount_m:['mount_t','Применение ритуальной оправы'],
    p_electrum:['electrum','Электрум: подготовка к MV'],
    end_table_l:['end_table','Верстак 7×7 в позднем производстве'],
    extreme_g:['extreme','Для чего нужен верстак 9×9'],
    core_t8:['gear_core8','Финальное применение каркаса T8'],
  };
  for(const [key,[primary,title]] of Object.entries(notes)){
    const q=all.get(key),p=all.get(primary);if(!q||!p)continue;
    q.icon ||= typeof q.task[0]==='string'?q.task[0]:'minecraft:book';
    q.task='check';q.t=title;delete q.xp;delete q.xpPoints;delete q.box;delete q.r;
    q.d.unshift('Это справочная заметка, повторно получать предмет не требуется. Предметное задание: «'+p.t+'».','');
    q.reference=primary;
  }
  for(const key of ['start_done','steam_done','power_done']){
    const q=all.get(key);q.task='check';q.completion=true;
    q.d=q.d.filter(s=>!s.startsWith('Для завершения предъявите'));
    q.d.push('Глава завершается после выполнения указанных предметных заданий. Повторная сдача машин и материалов не нужна.');
  }
  all.get('power_done').dep=['assembler','ebf'];
  all.get('hammer').t='Кузнечный молот — станция';
  all.get('iron_hammer').t='Железный молот — инструмент';
};
