"""Install a new separate Prism instance, leaving the currently open test client untouched."""
import os,pathlib,zipfile
from catalog import ROOT
target=pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustry-0.1.4'
target.mkdir(exist_ok=True)
with zipfile.ZipFile(ROOT/'dist/ArcaneIndustry-0.1.4-Prism.zip') as z:
    for entry in z.infolist():
        parts=pathlib.PurePosixPath(entry.filename).parts
        if len(parts)<2 or entry.is_dir():continue
        rel=pathlib.Path(*parts[1:]);out=target/rel
        assert out.resolve().is_relative_to(target.resolve())
        out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(z.read(entry))
java=next((ROOT/'runtime/java21').glob('*/bin/javaw.exe'))
cfg=(target/'instance.cfg').read_text('utf-8').replace('OverrideJavaLocation=false','OverrideJavaLocation=true').replace('AutomaticJava=true','AutomaticJava=false')
cfg+='\nJavaPath='+java.as_posix()+'\n'
(target/'instance.cfg').write_text(cfg,'utf-8')
print('Installed separate Prism instance: ArcaneIndustry-0.1.4')
