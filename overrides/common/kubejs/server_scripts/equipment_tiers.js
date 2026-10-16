// Equipment tier tooltips from kubejs/config/gear-tiers.json (tools/build_gear_tiers.js).
// Replaces the old generated T0-T8 epochs; see GEAR-TIERS.md.
const AI_TIP_TABLE = JSON.parse(String(JsonIO.readString('kubejs/config/gear-tiers.json')));

ItemEvents.modifyTooltips(event => {
  let byTier = {};
  Object.keys(AI_TIP_TABLE.tiers).forEach(id => {
    let t = AI_TIP_TABLE.tiers[id];
    (byTier[t] = byTier[t] || []).push(id);
  });
  Object.keys(byTier).forEach(t => {
    let tier = parseInt(t);
    let color = parseInt(AI_TIP_TABLE.colors[tier].substring(1), 16);
    let line = Text.of('Тир ' + AI_TIP_TABLE.roman[tier] + ' · ' + AI_TIP_TABLE.names[tier]).color(color);
    let source = tier <= 7
      ? Text.of('Встречается в сундуках').gray()
      : Text.of('Только крафт').darkGray();
    event.add(byTier[t], [line, source]);
  });
});
