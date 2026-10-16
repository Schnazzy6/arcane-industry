"""Remove the explicitly rejected Create stack from staging and the local test instance."""
import json, os, pathlib
from catalog import ROOT

rejected={'create','create-stock-bridge','storage-drawers-create-compat','iris-flw-compat'}
lockpath=ROOT/'pack.lock.json'
lock=json.loads(lockpath.read_text('utf-8'))
removed=[m for m in lock['mods'] if m['slug'] in rejected]
roots=[ROOT/'build/server',ROOT/'build/prism/Arcane Industry Prototype/minecraft',
       pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft']
for root in roots:
 for mod in removed:
  target=root/'mods'/mod['filename']
  assert target.resolve().is_relative_to(root.resolve())
  if target.exists():target.unlink()
lock['mods']=[m for m in lock['mods'] if m['slug'] not in rejected]
lockpath.write_text(json.dumps(lock,ensure_ascii=False,indent=2),'utf-8')
config=ROOT/'overrides/common/config/almostunified/unification/arcane_metals.json'
data=json.loads(config.read_text('utf-8'))
data['mod_priorities']=[m for m in data['mod_priorities'] if m!='create']
config.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')
print('Removed:',', '.join(m['slug'] for m in removed))
