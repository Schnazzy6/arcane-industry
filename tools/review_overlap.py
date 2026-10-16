import json,sys
from catalog import ROOT,api
sys.stdout.reconfigure(encoding='utf-8')
slugs='ae-additions mega expanded-ae extended-ae advancedae appflux merequester ae2-automatic-requester ae2-pattern-encoding-access-terminal ae2-fluid-crafting-terminal ae2-import-export-card ae2-pattern-restocker ae2-favorites ae2-qol-client ae2-terminal-mouse-wheel-scrolling pattern-encoding-terminal-quick-math inventory-essentials inventory-profiles-next modern-dynamics'
for slug in slugs.split():
    p=api('project/'+slug)
    print('\n###',slug,'\n',p['description'],'\n',p.get('body','')[:9000])
