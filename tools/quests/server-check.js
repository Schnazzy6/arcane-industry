// Start the existing local test server; validate filters and stop after book loading.
const fs=require('fs'),path=require('path'),{spawn}=require('child_process');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'build/server');
const chapters=require('./load')(),G=require('./gear'),expr=require('./filters');
const expectedQuests=chapters.reduce((n,c)=>n+c.quests.length,0);
const crypto=require('crypto');
const visualExpected=Object.fromEntries(chapters.flatMap(c=>c.quests.map(q=>[
  (BigInt('0x'+crypto.createHash('sha1').update('quest:'+q.k).digest('hex').slice(0,16))&0x7fffffffffffffffn).toString(16).toUpperCase().padStart(16,'0'),q.hideLines])));
const rewardExpected=Object.fromEntries(chapters.flatMap(c=>c.quests.map(q=>[
  (BigInt('0x'+crypto.createHash('sha1').update('quest:'+q.k).digest('hex').slice(0,16))&0x7fffffffffffffffn).toString(16).toUpperCase().padStart(16,'0'),q.r||[]])));
const expectedImages=chapters.reduce((n,c)=>n+(c.images?.length||0),0);
const expectedColors=Object.fromEntries(chapters.flatMap(c=>(c.images||[]).map(im=>[
  (BigInt('0x'+crypto.createHash('sha1').update('image:'+c.k+':'+im.key).digest('hex').slice(0,16))&0x7fffffffffffffffn).toString(16).toUpperCase().padStart(16,'0'),parseInt(im.color.slice(1),16)])));
const gearQuests=chapters.flatMap(c=>c.quests).filter(q=>q.gear);
const cases=gearQuests.map(q=>{
  const wrongTier=Object.keys(G.data.tiers).find(id=>G.data.group[id]===q.gear.group&&G.data.tiers[id]!==q.gear.tier);
  const wrongType=Object.keys(G.data.tiers).find(id=>G.data.group[id]&&G.data.group[id]!==q.gear.group&&G.data.tiers[id]===q.gear.tier);
  return [q.k,expr(q.task[0]),q.task[0].any,[wrongTier,wrongType,'minecraft:stone'].filter(Boolean)];
});
const jdk=fs.readdirSync(path.join(root,'runtime/java21'))[0];
const log=fs.createWriteStream(path.join(root,'build/quests-server-check.log'));
const probe=path.join(dir,'kubejs/server_scripts/zzzz_quest_filter_probe.js');
if(fs.existsSync(probe)) throw Error('Probe already exists: '+probe);
fs.writeFileSync(probe, `let questProbeTicks = 0;
ServerEvents.tick(event => {
  if (++questProbeTicks !== 20) return;
  const Parser = Java.loadClass('dev.ftb.mods.ftbfiltersystem.util.FilterParser');
  var file = Java.loadClass('dev.ftb.mods.ftbquests.quest.ServerQuestFile').INSTANCE;
  var visualExpected = ${JSON.stringify(visualExpected)};
  var checkedVisual = 0, imageCount = 0;
  var rewardExpected = ${JSON.stringify(rewardExpected)};
  var rewardedQuests = 0;
  var expectedColors = ${JSON.stringify(expectedColors)};
  file.getAllChapters().forEach(function(ch) {
    if (!ch.getQuestLinks().isEmpty()) throw new Error('Duplicate quest aliases remain');
    ch.getImages().forEach(function(image) {
      if (image.getImage().isEmpty()) throw new Error('Empty chapter panel');
      if ((image.getColor().rgb() & 16777215) !== expectedColors[String(image.getCodeString()).toUpperCase()]) throw new Error('Panel tint missing');
      if (image.shouldDrawTextOnImage() && (image.getHeight()>1 || image.getTextInset()<8)) throw new Error('Header text lacks safe size/inset');
      imageCount++;
    });
    ch.getQuests().forEach(function(q) {
      var code = String(q.getCodeString()).toUpperCase();
      if (q.shouldHideDependencyLines() !== visualExpected[code]) throw new Error('Line visibility mismatch '+code);
      var items = [];
      q.getRewards().forEach(function(reward) {
        if (String(reward.getType().getTypeId()) === 'ftbquests:item') items.push([String(reward.getItem().id),Number(reward.getCount())]);
      });
      if (JSON.stringify(items) !== JSON.stringify(rewardExpected[code])) throw new Error('Physical reward differs '+code+' actual='+JSON.stringify(items)+' expected='+JSON.stringify(rewardExpected[code]));
      if (items.length) rewardedQuests++;
      checkedVisual++;
    });
  });
  if (checkedVisual !== ${expectedQuests} || imageCount !== ${expectedImages}) throw new Error('Visual book counts differ');
  console.info('[Quest Layout Probe] PASS: '+checkedVisual+' visibility flags, '+imageCount+' panels with verified tints and header bounds, zero quest aliases');
  console.info('[Quest Reward Probe] PASS: '+rewardedQuests+' quests with verified item rewards');
  const cases = [
    ['item_tag(minecraft:logs)', 'minecraft:oak_log', 'minecraft:stone'],
    ['item_tag(minecraft:beds)', 'minecraft:red_bed', 'minecraft:stone'],
    ['or(item(minecraft:cooked_beef)item(minecraft:baked_potato))', 'minecraft:baked_potato', 'minecraft:rotten_flesh']
  ];
  cases.forEach(function(c) {
    var f = Parser.parse(c[0], event.server.registryAccess());
    var positive = f.test(Item.of(c[1]));
    var negative = f.test(Item.of(c[2]));
    console.info('[Quest Filter Probe] '+c[0]+': positive='+positive+', negative='+negative);
    if (!positive || negative) throw new Error('Quest filter failed: '+c[0]);
  });
  const gearCases = ${JSON.stringify(cases)};
  let accepted = 0, rejected = 0, failures = 0;
  gearCases.forEach(function(c) {
    var f = Parser.parse(c[1], event.server.registryAccess());
    c[2].forEach(function(id) {
      if (!f.test(Item.of(id))) {
        failures++;
        console.info('[Quest Gear Probe] REJECTED '+id+' for '+c[0]+' actual='+Item.of(id).id+' count='+Item.of(id).count+' isolated='+Parser.parse('item('+id+')', event.server.registryAccess()).test(Item.of(id)));
      }
      accepted++;
    });
    c[3].forEach(function(id) {
      if (f.test(Item.of(id))) {failures++;console.info('[Quest Gear Probe] LEAKED '+id+' for '+c[0]);}
      rejected++;
    });
  });
  if (failures) throw new Error('Quest gear probe: '+failures+' failures');
  console.info('[Quest Gear Probe] PASS: '+gearCases.length+' filters, '+accepted+' accepted candidates, '+rejected+' rejected mismatches');
  console.info('[Quest Filter Probe] PASS: tag and any-of, positive and negative matches');
});\n`);
const p=spawn(path.join(root,'runtime/java21',jdk,'bin/java.exe'),['-Xms1G','-Xmx5G','@libraries/net/neoforged/neoforge/21.1.259/win_args.txt','nogui'],{cwd:dir,windowsHide:true,stdio:['pipe','pipe','pipe']});
let ready=false,tail='',stopping=false,probePassed=false,gearPassed=false,layoutPassed=false,rewardsPassed=false,bookLoaded=false;
function stop(){if(stopping)return;stopping=true;p.stdin.write('stop\n');}
const timer=setTimeout(()=>{console.error('Server check timed out');stop();},240000);
function onData(b){const s=b.toString();log.write(s);tail=(tail+s).slice(-12000);
  if(tail.includes('[Quest Filter Probe] PASS:')) probePassed=true;
  if(tail.includes('[Quest Gear Probe] PASS: '+gearQuests.length+' filters')) gearPassed=true;
  if(tail.includes('[Quest Layout Probe] PASS:')) layoutPassed=true;
  if(tail.includes('[Quest Reward Probe] PASS:')) rewardsPassed=true;
  if(new RegExp('Loaded \\d+ chapter groups, '+chapters.length+' chapters, '+expectedQuests+' quests, 9 reward tables').test(tail)) bookLoaded=true;
  if(!ready && /Done \([\d.]+s\)!/.test(tail)){ready=true;console.log('Server ready; quest definitions loaded');setTimeout(stop,7000);}
}
p.stdout.on('data',onData);p.stderr.on('data',onData);
p.on('error',e=>{console.error(e);clearTimeout(timer);process.exitCode=1;});
p.on('exit',code=>{clearTimeout(timer);log.end();fs.unlinkSync(probe);console.log('Server exit:',code,'ready:',ready,'filters:',probePassed,'gear:',gearPassed,'layout:',layoutPassed,'rewards:',rewardsPassed,'book:',bookLoaded);process.exitCode=ready&&code===0&&probePassed&&gearPassed&&layoutPassed&&rewardsPassed&&bookLoaded?0:1;});
