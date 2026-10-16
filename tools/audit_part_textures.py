"""Validate every referenced vanilla texture against the actual Minecraft assets."""
import json,os,pathlib,zipfile
from catalog import ROOT
plan=json.loads((ROOT/'build/progression-plan.json').read_text('utf-8'))
library=pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/libraries/net/minecraft/client'
files=list(library.glob('1.21.1*/*-extra.jar'))
assert files,'Minecraft asset JAR not found'
entries=set()
for jar in files:
 with zipfile.ZipFile(jar) as z:entries.update(z.namelist())
for item,row in plan['items'].items():
 namespace,path=row['texture'].split(':',1)
 expected=f'assets/{namespace}/textures/{path}.png'
 if namespace=='kubejs':assert (ROOT/'overrides/client/kubejs'/expected).exists(),(item,expected)
 else:assert expected in entries,(item,expected)
print('Texture references valid:',len(plan['items']))
