import json,pathlib,os,shutil
from catalog import ROOT
instance=ROOT/'build/prism/Arcane Industry Prototype'
game=instance/'minecraft'
java=next((ROOT/'runtime/java21').glob('*/bin/javaw.exe'))
pack={'formatVersion':1,'components':[{'uid':'org.lwjgl3','version':'3.3.3','dependencyOnly':True},{'uid':'net.minecraft','version':'1.21.1','important':True},{'uid':'net.neoforged','version':'21.1.259'}]}
(instance/'mmc-pack.json').write_text(json.dumps(pack,indent=2),'utf-8')
cfg='[General]\nInstanceType=OneSix\nname=Arcane Industry Prototype 0.1.0\niconKey=default\nOverrideMemory=true\nMinMemAlloc=2048\nMaxMemAlloc=10240\nOverrideJavaLocation=true\nJavaPath='+java.as_posix()+'\nAutomaticJava=false\nOverrideJavaArgs=true\nJvmArgs=-XX:+UseG1GC\nOverrideWindow=true\nLaunchMaximized=false\nMinecraftWinWidth=1280\nMinecraftWinHeight=720\n'
(instance/'instance.cfg').write_text(cfg,'utf-8')
options='lang:ru_ru\nrenderDistance:12\nsimulationDistance:6\nmaxFps:120\nenableVsync:false\nguiScale:3\ngraphicsMode:1\nentityDistanceScaling:0.75\nparticles:1\nshowTutorial:false\ntutorialStep:none\n'
if not (game/'options.txt').exists():(game/'options.txt').write_text(options,'utf-8')
(game/'config').mkdir(exist_ok=True)
if not (game/'config/iris.properties').exists():
    (game/'config/iris.properties').write_text('enableShaders=false\nshaderPack=ComplementaryReimagined_r5.9.3.zip\n','utf-8')
target=pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustryPrototype'
target.mkdir(exist_ok=True)
for p in (target/'minecraft/mods').glob('*.jar'):
    if not (game/'mods'/p.name).exists():
        assert p.resolve().is_relative_to(target.resolve())
        p.unlink()
shutil.copytree(instance,target,dirs_exist_ok=True)
print('Prism instance ready:',str(target).encode('ascii','backslashreplace').decode())
