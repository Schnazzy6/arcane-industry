// ONLY copied to the isolated test server. Test items/world are disposable.
let trTrialTick = 0;
ServerEvents.tick(event => {
  trTrialTick++;
  const s = event.server;
  if (trTrialTick === 1) {
    s.runCommandSilent('forceload add 0 0');
    s.runCommandSilent('fill 0 99 0 6 99 2 minecraft:stone');
    s.runCommandSilent('setblock 0 100 0 techreborn:grinder');
    s.runCommandSilent('setblock 1 100 0 techreborn:solid_fuel_generator');
    s.runCommandSilent('setblock 3 100 0 advanced_reborn:rotary_grinder');
  }
  if (trTrialTick === 20) {
    try {
      var l = s.overworld();
      var grinder = l.getBlock(0,100,0).entity;
      var gen = l.getBlock(1,100,0).entity;
      var rotary = l.getBlock(3,100,0).entity;
      grinder.getInventory().setItem(0, Item.of('minecraft:bone'));
      gen.getInventory().setItem(0, Item.of('minecraft:coal', 8));
      rotary.getInventory().setItem(0, Item.of('minecraft:bone'));
      rotary.setEnergy(rotary.getMaxStoredPower());
      rotary.setHeat(10000);
      console.info('[TR-TRIAL] Machines initialized; grinder powered by adjacent coal generator');
    } catch (e) { console.error('[TR-TRIAL] INIT '+e); }
  }
  if (trTrialTick === 620) {
    try {
      var l = s.overworld();
      for (const x of [0,1,3]) {
        const be = l.getBlock(x,100,0).entity;
        const inv = be.getInventory();
        let contents=[];
        for(let i=0;i<inv.getContainerSize();i++) if(!inv.getItem(i).isEmpty()) contents.push(i+':'+inv.getItem(i));
        console.info('[TR-TRIAL] RESULT x='+x+' energy='+be.getEnergy()+' inventory='+contents.join(';'));
      }
    } catch (e) { console.error('[TR-TRIAL] RESULT '+e); }
  }
});

