// Audit for the tier ladder. Copy into server_scripts, start the server once, delete.
// For every recipe whose result is tiered gear (II-XI) it reports recipes that are not
// ladder steps, and ladder/other recipes whose gear ingredient is 2+ tiers below the
// result or hits harder than the result.
const AI_AUD = JSON.parse(String(JsonIO.readString('kubejs/config/gear-tiers.json')));
const AI_AUD_REG = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
const AI_AUD_DC = Java.loadClass('net.minecraft.core.component.DataComponents');
const AI_AUD_ATTR = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes');
// Damage per second-ish, as in tools/build_gear_tiers.js (attack damage x speed).
function aiAudPower(stack) {
  var dmg = 0, spd = 0, mods = stack.get(AI_AUD_DC.ATTRIBUTE_MODIFIERS);
  if (mods != null) mods.modifiers().forEach(e => { if (e.attribute().is(AI_AUD_ATTR.ATTACK_DAMAGE)) dmg += e.modifier().amount(); else if (e.attribute().is(AI_AUD_ATTR.ATTACK_SPEED)) spd += e.modifier().amount(); });
  return (dmg + 1) * Math.sqrt(Math.max(0.25, 4 + spd) / 1.6);
}
function aiAudDamage(stack) {
  var dmg = 0, mods = stack.get(AI_AUD_DC.ATTRIBUTE_MODIFIERS);
  if (mods != null) mods.modifiers().forEach(e => { if (e.attribute().is(AI_AUD_ATTR.ATTACK_DAMAGE)) dmg += e.modifier().amount(); });
  return dmg;
}
ServerEvents.loaded(event => {
  var reg = event.server.registryAccess(), bad = [], notLadder = [], checked = 0, perOut = {}, ladderTypes = {};
  event.server.getRecipeManager().getRecipes().forEach(h => {
    var r = h.value(), id = String(h.id()), res;
    if (id.indexOf('kubejs:rework/ladder/') === 0) { var ty = String(AI_AUD_REG.RECIPE_TYPE.getKey(r.getType())); ladderTypes[ty] = (ladderTypes[ty] || 0) + 1; }
    try { res = r.getResultItem(reg); } catch (e) { return; }
    if (res == null || res.isEmpty()) return;
    var out = String(AI_AUD_REG.ITEM.getKey(res.getItem()));
    var tier = AI_AUD.tiers[out];
    if (tier === undefined || tier < 2 || tier > 11 || !AI_AUD.group[out]) return;
    checked++;
    perOut[out] = (perOut[out] || 0) + 1;
    if (/smithing_trim|_trim$/.test(id)) return; // armor trims re-skin the same item
    if (id.indexOf('kubejs:rework/ladder/') !== 0) notLadder.push(id + ' -> ' + out);
    var minTier = 99, harder = null, outPow = aiAudPower(res);
    r.getIngredients().forEach(ing => {
      var items = [];
      try { ing.itemIds.forEach(x => items.push(Item.of(String(x)))); } catch (e1) { try { ing.stackArray.forEach(x => items.push(x)); } catch (e2) { } }
      for (var i = 0; i < items.length; i++) {
        var iid = String(items[i].id);
        var t = AI_AUD.tiers[iid];
        if (t === undefined || !AI_AUD.group[iid]) continue;
        minTier = Math.min(minTier, t);
        if (String(AI_AUD.group[out]).indexOf('weapon') === 0 && aiAudPower(items[i]) > outPow + 0.01) harder = iid;
      }
    });
    if (minTier !== 99 && tier - minTier >= 2) {
      // A gap is fine only when the group has no items in the tiers in between.
      var gapFree = true;
      for (var g = minTier + 1; g < tier; g++) if (Object.keys(AI_AUD.group).some(x => AI_AUD.group[x] === AI_AUD.group[out] && AI_AUD.tiers[x] === g)) gapFree = false;
      if (!gapFree) bad.push(id + ': ' + out + ' (' + tier + ') from tier ' + minTier);
    }
    if (harder) bad.push(id + ': ' + out + ' made from harder-hitting ' + harder);
  });
  JsonIO.write('kubejs/config/ladder-leftovers.json', {entries: notLadder.map(x => ({id: x.split(' -> ')[0], out: x.split(' -> ')[1]}))});
  var multi = Object.keys(perOut).filter(o => perOut[o] > 1);
  console.info('[LadderAudit] gear recipes checked ' + checked + ', not ladder ' + notLadder.length + ', flagged ' + bad.length + ', outputs with 2+ recipes ' + multi.length);
  console.info('[LadderAudit] ladder recipe types ' + JSON.stringify(ladderTypes));
  notLadder.slice(0, 25).forEach(x => console.info('[LadderAudit] not ladder: ' + x));
  bad.slice(0, 40).forEach(x => console.info('[LadderAudit] flagged: ' + x));
  multi.slice(0, 15).forEach(x => console.info('[LadderAudit] multi: ' + x + ' x' + perOut[x]));
});
