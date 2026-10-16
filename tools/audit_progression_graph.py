"""Check custom-component dependencies, with explicit industrial milestone aliases.

This is a critical-path cycle check, not a proof of every upstream mod mechanic.
"""
import json,collections
from catalog import ROOT
p=json.loads((ROOT/'build/progression-plan.json').read_text('utf-8'))
k='kubejs:';m='modern_industrialization:'
nodes={k+n for n in p['items']}
aliases={
 m+'analog_circuit':[k+'arcane_resin'],m+'digital_circuit':[k+'alchemical_catalyst'],
 m+'processing_unit':[k+'soul_stabilizer'],m+'quantum_circuit':[k+'soul_stabilizer',k+'seal_elements'],
 m+'advanced_machine_hull':[k+'alchemical_catalyst'],m+'quantum_machine_hull':[k+'seal_elements'],
 'techreborn:uu_matter':[k+'reborn_interface'],
 'techreborn:industrial_circuit':[k+'reborn_interface',k+'engineering_matrix'],
 'techreborn:data_storage_chip':[k+'reborn_interface',k+'engineering_matrix'],
 'techreborn:iridium_alloy_ingot':[k+'seal_elements'],
 'techreborn:superconductor':[k+'reborn_interface'],
 'goety:mystic_core':[k+'ritual_frame'],'forbidden_arcanus:deorum_ingot':[k+'ritual_frame'],
 'irons_spellbooks:rare_ink':[k+'industrial_focus'],
}
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,list):
  for v in x:yield from strings(v)
 elif isinstance(x,dict):
  for v in x.values():yield from strings(v)
edges={n:set() for n in nodes}
for row in p['recipes']:
 r=row['json'];out=r.get('result',r.get('output',{}))
 result=out.get('id') if isinstance(out,dict) else None
 if not result:
  outputs=r.get('item_outputs',[])
  if outputs:result=outputs[0]['item']
 if result not in nodes:continue
 # Occultism ritual_dummy is a viewer icon; Nature's Aura uses output.
 inputs={key:value for key,value in r.items() if key not in ['result','output','item_outputs','ritual_dummy']}
 for item in strings(inputs):
  if item in nodes:edges[result].add(item)
  edges[result].update(aliases.get(item,[]))
# The researcher tag is a native item ingredient, not a custom recipe dependency.
visiting=set();done=set();order=[]
def visit(n,trail):
 assert n not in visiting,'Progression cycle: '+' -> '.join(trail+[n])
 if n in done:return
 visiting.add(n)
 for dep in sorted(edges[n]):visit(dep,trail+[n])
 visiting.remove(n);done.add(n);order.append(n)
for n in sorted(nodes):visit(n,[])
report={'custom_components':len(nodes),'cycles':False,'topological_order':order,
        'dependencies':{n:sorted(v) for n,v in edges.items()},
        'limits':'Explicit milestone aliases; does not model every native recipe, drop, ritual or machine.'}
(ROOT/'build/progression-graph-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
assert 'create:' not in json.dumps(p),'Create reference in generated progression'
print('No custom-component cycles:',len(nodes),'components; no Create references.')
