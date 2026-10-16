// Recipe rework (RECIPE-REWORK.md): magic<->tech components and armor tier templates.
StartupEvents.registry('item', event => {
  [
    ['sky_plate', 'Пластина небесного слитка'],
    ['iesnium_plate', 'Иесниевая пластина'],
    ['deorum_plate', 'Деорумная пластина'],
    ['mithril_mesh', 'Мифриловая сетка'],
    ['enchanted_titanium_plate', 'Зачарованная титановая пластина'],
    ['hallowed_circuit', 'Освящённая схема'],
    ['resonance_core', 'Резонансное ядро'],
    ['arcane_lens', 'Арканная линза'],
    // Creative item chain (rework_creative.js): one matrix per field.
    ['infinite_storage_matrix', 'Матрица бесконечного хранения'],
    ['infinite_energy_matrix', 'Матрица бесконечной энергии'],
    ['infinite_fluid_matrix', 'Матрица бесконечных жидкостей'],
    ['infinite_arcane_matrix', 'Матрица бесконечной магии']
  ].forEach(e => event.create(e[0]).displayName(e[1]).texture('kubejs:item/rework/' + e[0]));
});
