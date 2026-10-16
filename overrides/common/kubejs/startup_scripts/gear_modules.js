// Upgrade modules for the tier ladder (GEAR-TIERS.md). Stations that cannot carry an
// item's enchantments over (MI assembler, Goety, Occultism, Nature's Aura) make a module;
// the module, the tier N-1 item and the material are then combined on a crafting table,
// which keeps enchantments, affixes and name.
// Only modules some ladder step uses are registered: rework_ladder.js writes that list to
// kubejs/config/ladder-modules.json. Without the file every station tier is registered.
const AI_MODULE_ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI'];
const AI_MODULE_KINDS = {
  tech_module: ['Технический модуль', 4], dark_essence: ['Тёмная эссенция', 7],
  spirit_contract: ['Договор духа', 4], aura_seed: ['Семя ауры', 4]
};
let aiModuleList = null;
try { aiModuleList = JSON.parse(String(JsonIO.readString('kubejs/config/ladder-modules.json'))).modules; } catch (err) { }
if (!aiModuleList) {
  aiModuleList = [];
  Object.keys(AI_MODULE_KINDS).forEach(k => { for (let t = AI_MODULE_KINDS[k][1]; t <= 11; t++) aiModuleList.push(k + '_t' + t); });
}
StartupEvents.registry('item', event => {
  aiModuleList.forEach(name => {
    let kind = name.replace(/_t\d+$/, ''), tier = parseInt(name.substring(name.lastIndexOf('_t') + 2));
    event.create(name).displayName(AI_MODULE_KINDS[kind][0] + ' тира ' + AI_MODULE_ROMAN[tier])
      .texture('kubejs:item/modules/' + name);
  });
});
