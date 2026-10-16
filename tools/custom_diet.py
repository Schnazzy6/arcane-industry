"""Compile the pack's small, version-specific five-dish Valheim integration."""
import pathlib,os,subprocess,zipfile,json,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=ROOT/'custom/arcane-diet';out=base/'classes';out.mkdir(exist_ok=True)
for stale in out.rglob('*.class'):
 assert stale.resolve().is_relative_to(out.resolve());stale.unlink()
prism=pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/libraries'
priority=[prism/'net/minecraft/client/1.21.1-20240808.144430/client-1.21.1-20240808.144430-srg.jar',prism/'net/neoforged/neoforge/21.1.259/neoforge-21.1.259-universal.jar']
libs=priority+[p for p in prism.rglob('*.jar') if p not in priority and '1.20.1' not in p.parts]
libs+=list((ROOT/'build/prism/Arcane Industry Prototype/minecraft/mods').glob('*.jar'))
# Nested libraries (MixinExtras, GrandPower, etc.) are not needed by the custom source.
args=['-proc:none','-encoding','UTF-8','--release','21','-classpath',';'.join(map(str,libs)),'-d',str(out)]+[str(p) for p in (base/'src').rglob('*.java')]
argfile=base/'javac.args';argfile.write_text('\n'.join('"'+s.replace('\\','/')+'"' for s in args),'utf-8')
javac=next((ROOT/'runtime/java21').glob('*/bin/javac.exe'))
subprocess.run([str(javac),'@'+str(argfile)],check=True,cwd=ROOT)
meta='''modLoader="javafml"
loaderVersion="[4,)"
license="MIT"
[[mods]]
modId="arcane_diet"
version="0.1.0"
displayName="Arcane Industry: Five Dish Diet"
description="Five active Valheim Reforged dishes, compact HUD and a raised air bar."
[[dependencies.arcane_diet]]
modId="neoforge"
type="required"
versionRange="[21.1.259,21.2)"
side="BOTH"
[[dependencies.arcane_diet]]
modId="sol_valheim_reforged"
type="required"
versionRange="[1.1.7,1.1.8)"
side="BOTH"
[[mixins]]
config="arcane_diet.mixins.json"
'''
filename='arcane-industry-diet-0.1.0.jar';target=base/filename
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for p in out.rglob('*.class'):z.write(p,p.relative_to(out).as_posix())
 z.writestr('META-INF/neoforge.mods.toml',meta)
 z.writestr('arcane_diet.mixins.json',json.dumps({'required':True,'minVersion':'0.8','package':'ai.diet.mixin','compatibilityLevel':'JAVA_21','mixins':['FoodMixin'],'client':['OverlayMixin'],'injectors':{'defaultRequire':1}}))
 z.writestr('LICENSE','MIT License\nCopyright (c) 2026 Arcane Industry pack contributors\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies, subject to inclusion of this notice. THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND.\n')
for dest in [ROOT/'build/server/mods',ROOT/'build/prism/Arcane Industry Prototype/minecraft/mods']:
 shutil.copy2(target,dest/filename)
row={'slug':'arcane-industry-diet','version':'0.1.0','filename':filename,'client':True,'server':True,'sha512':hashlib.sha512(target.read_bytes()).hexdigest(),'sha1':hashlib.sha1(target.read_bytes()).hexdigest(),'category':'pack-integration','source':'custom/arcane-diet/src','license':'MIT'}
(ROOT/'custom.lock.json').write_text(json.dumps([row],indent=2),'utf-8')
print('Compiled and staged',filename)
