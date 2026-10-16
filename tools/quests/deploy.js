// Install only quest definitions. Back up definitions; never touch team/player progress.
const fs=require('fs'),path=require('path'),os=require('os');
const root=path.resolve(__dirname,'../..'), source=path.join(root,'overrides/common/config/ftbquests/quests');
const stamp=new Date().toISOString().replace(/[:.]/g,'-');
const backup=path.join(root,'build/quest-backups',stamp);
const targets=[path.join(root,'build/server/config/ftbquests/quests'),
  path.join(process.env.APPDATA || path.join(os.homedir(),'AppData/Roaming'),'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft/config/ftbquests/quests')];
for(const [i,target] of targets.entries()) {
  if(!fs.existsSync(path.dirname(target))) throw Error('Target missing: '+target);
  if(fs.existsSync(target)) fs.cpSync(target,path.join(backup,String(i)),{recursive:true});
  fs.mkdirSync(target,{recursive:true});
  fs.cpSync(source,target,{recursive:true});
  console.log('Installed:',target);
}
console.log('Definitions backed up:',backup);
