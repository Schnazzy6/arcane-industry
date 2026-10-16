"""Build an isolated server-only native world test; never part of the pack lock."""
import pathlib,json,subprocess,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
out=ROOT/'build/ritual-test'
java=next((ROOT/'runtime/java21').glob('*/bin/javac.exe'))
old=(ROOT/'custom/arcane-diet/javac.args').read_text('utf-8').splitlines()
cp=json.loads(old[old.index('"-classpath"')+1])
dfu=next((ROOT/'build/server/libraries/com/mojang/datafixerupper/8.0.16').glob('*.jar'))
cp=str(dfu.resolve()).replace('\\','/')+';'+cp
cp+=';'+ ';'.join(str(p.resolve()).replace('\\','/') for p in (ROOT/'build/server/mods').glob('*.jar'))
classes=out/'test-classes';classes.mkdir(exist_ok=True)
args=['-proc:none','-encoding','UTF-8','--release','21','-classpath',cp,'-d',str(classes),str(ROOT/'tools/RitualWorldTest.java')]
argfile=out/'javac.args';argfile.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in args),'utf-8')
subprocess.run([str(java),'@'+str(argfile)],check=True)
jar=ROOT/'build/server/mods/arcane-ritual-test.jar'
with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('META-INF/neoforge.mods.toml','modLoader="javafml"\nloaderVersion="[4,)"\nlicense="All Rights Reserved"\n[[mods]]\nmodId="arcane_ritual_test"\nversion="1.0"\ndisplayName="Temporary native ritual world test"\n')
 for p in classes.rglob('*.class'):z.write(p,p.relative_to(classes).as_posix())
print('Built test-only mod:',jar)
