const C = require('./catalog');
module.exports = chapters => {
  const all = Object.fromEntries(chapters.flatMap(c => c.quests).map(q => [q.k,q]));
  const fix = (k, d) => { if (all[k]) all[k].d = d; };
  for (const ch of chapters) for (const q of ch.quests) if (q.d) q.d = q.d.map(s => s
    .replace(/от I до XI(?!I)/g, 'от I до XII').replace(/(?<!I)I–XI(?!I)/g, 'I–XII')
    .replace('Основа никогда не сильнее результата.', 'Обычно выбирается основа не сильнее результата. Для 17 переходов подходящей более слабой вещи нет: требуется вещь ближайшего предыдущего тира.')
    .replace('электрические машины станут почти бесплатными', 'серийная сборка электрических машин станет удобнее')
    .replace('броню тира II–III', 'ступень снаряжения IV'));
  fix('hammer', ['Кузнечный молот — ранняя станция MI без энергии. Обрабатывайте слитки и руду, сверяя выход с JEI.', '', 'Для части операций в слот нужен молот-инструмент. Обычный молот и молот-инструмент — разные предметы.', '', 'Рецепт станции: три тяжёлые нажимные плиты и четыре железных слитка.']);
  fix('macerator', ['Измельчитель превращает сырое сырьё и детали в пыль. Выход зависит от рецепта; вероятностный дополнительный продукт указан в JEI.', '', 'Сочетайте добычу целой руды, кузнечный молот и машинную переработку. Не рассчитывайте на фиксированное учетверение любого сырья.']);
  fix('iron_tools', ['Подготовьте железную кирку, топор, лопату и меч. Их рецепты в сборке изменены лестницей снаряжения: смотрите JEI и нужный верстак.', '', 'Это дополнительная цель, а не условие доступа к магии. Для книги новичка Ars проверьте фактический рецепт в главе магии.']);
  all.iron_tools.opt = true;
  all.waystone.dep = ['iron'];
  all.waystone.at = [12,-4];
  all.barrel.at = [14,-6];
  all.trash.at = [34,-6];
  all.quarry.at = [36,-2];
  fix('food1', ['Приготовьте запас еды. Поддерживайте разнообразие рациона: показатели и действующие эффекты AppleSeed смотрите в интерфейсе питания.', '', 'Еда не заменяет броню и осторожность. Параллельно заведите небольшое поле и кухню Farmer’s Delight.']);
  all.food1.task = [{any: ['minecraft:cooked_beef','minecraft:cooked_porkchop','minecraft:cooked_chicken','minecraft:cooked_mutton','minecraft:baked_potato']}, 8];
  all.food1.icon = 'minecraft:cooked_beef';
  fix('diet', ['Приготовьте овощной суп в кастрюле. Состав и допустимые замены смотрите в JEI.', '', 'Чередуйте блюда и проверяйте показатели рациона. Точные бонусы зависят от настроек сборки и уже съеденных продуктов.']);
  fix('efurnace', ['Электрическая печь использует EU вместо топлива и пара. Подайте питание допустимым кабелем, настройте вход и выход.', '', 'Непрерывная линия удобнее постоянного ручного переключения слотов.']);
  fix('ewire', ['Электрический волочильный станок делает провод и тонкий провод. Закрепите входной материал и оставьте выход для полной партии.', '', 'Обычный провод, тонкий провод и изолированный кабель — три разных вида деталей.']);
  fix('ebf', ['Электрическая доменная печь — многоблок перехода к промышленности. Точную форму и допустимые люки показывает голограмма с ключом в руке.', '', 'Подведите EU через энергетический вход, предметы и жидкости — через соответствующие люки. Требуемое EU/т, длительность и нагрев проверяйте в рецепте JEI.', '', 'Одного контроллера в инвентаре недостаточно для работы: соберите структуру и проверьте пробную плавку.']);
  fix('p_intro', ['Переход к электричеству начинается с резины и аналоговых схем. До сборщика используйте доступные ручные и паровые рецепты.', '', 'Арканная пропитка для платы требует параллельного развития Ars. Сначала организуйте запас компонентов, затем собирайте турбину и электрические машины.']);
  fix('carry', ['Скрипты улучшения предусмотрены для переноса чар, аффиксов и имени. Результат зависит от станции и компонентов предмета; игровые проверки всех вариантов ещё не завершены.', '', 'Перед улучшением ценной вещи проверьте результат в тестовом мире. Для модульной станции сначала изготовьте модуль, затем объедините его с основой и материалами.']);
  const early = chapters.filter(c => ['start','steam','power'].includes(c.k));
  for (const ch of early) {
    for (const q of ch.quests) {
      // A small, fixed amount of XP cannot scale with the player's existing level.
      delete q.xp; delete q.box; delete q.r;
      q.xpPoints = q.task === 'check' ? 0 : q.main ? 12 : ch.k === 'start' ? 3 : 5;
      if (q.main && q.task !== 'check') q.r = [['minecraft:torch',8]];
      if (!q.d || !q.d.length) throw new Error('Missing description: ' + q.k);
      if (q.task !== 'check') {
        const tasks = Array.isArray(q.task[0]) ? q.task : [q.task];
        const items = tasks.flatMap(t => typeof t[0] === 'string' && !t[0].startsWith('#') ? [t[0]] : t[0].any || []);
        const item = items[0];
        if (item) {
          q.d.push('', C.description(item));
          // Detailed recipes are generated from the server dump, never guessed.
          const source = C.sources(item).find(r => r.type === 'minecraft:crafting_shaped' || r.type === 'minecraft:crafting_shapeless') || C.sources(item)[0];
          if (source && (q.k.startsWith('part_') || /^[ps]_/.test(q.k))) q.d.push('', ...C.recipeLines(source));
        }
        q.d.push('', '&7Предметы не изымаются. R в JEI — рецепт, U — применение. Прогресс общий для команды FTB Teams; награду каждый забирает отдельно.&r');
      }
    }
    // End-of-era rewards require actual products, not an unverified checkmark.
    const end = all[{start:'start_done',steam:'steam_done',power:'power_done'}[ch.k]];
    end.task = ch.k === 'start' ? [['modern_industrialization:tin_ingot',4],['minecraft:copper_ingot',12]] :
      ch.k === 'steam' ? [['modern_industrialization:steel_wiremill',1],['modern_industrialization:steel_ingot',8]] :
      [['modern_industrialization:assembler',1],['modern_industrialization:electric_blast_furnace',1]];
    end.xpPoints = 20; end.box = {start:'era0',steam:'era1',power:'era2'}[ch.k];
    end.d.push('', 'Для завершения предъявите предметы задания в инвентаре. После размещения машины её можно временно снять; предметы не забираются. Награда выдаётся один раз каждому участнику команды.');
  }
};
