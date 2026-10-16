import concurrent.futures, json, pathlib, urllib.request, urllib.parse, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / 'cache' / 'api'
CACHE.mkdir(parents=True, exist_ok=True)
BASE = 'https://api.modrinth.com/v2/'
def api(path):
    key = __import__('hashlib').sha256(path.encode()).hexdigest()
    dest = CACHE / (key + '.json')
    if dest.exists(): return json.loads(dest.read_text('utf-8'))
    for attempt in range(5):
        try:
            req = urllib.request.Request(BASE + path, headers={'User-Agent':'ArcaneIndustryPrototype/0.1 (personal modpack builder)'})
            with urllib.request.urlopen(req, timeout=90) as r: data = json.load(r)
            dest.write_text(json.dumps(data, ensure_ascii=False), 'utf-8')
            return data
        except Exception:
            if attempt == 4: raise
            time.sleep(2 * (attempt+1))

CANDIDATES = {
 'industry': 'modern-industrialization create ae2 modern-dynamics extended-industrialization',
 'magic': 'ars-nouveau occultism irons-spells-n-spellbooks malum natures-aura theurgy eidolon-repraised goety forbidden-arcanus hexerei evilcraft blood-magic botania',
 'magic-addons': 'ars-elemental ars-additions ars-ocultas ars-unification',
 'world': 'terralith tectonic regions-unexplored explorers-compass natures-compass waystones lootr yungs-better-dungeons yungs-better-mineshafts yungs-better-strongholds yungs-better-nether-fortresses dungeons-and-taverns twilight-forest cataclysm artifacts relics',
 'building': 'farmers-delight amendments supplementaries handcrafted chipped rechiseled macaws-bridges macaws-roofs macaws-windows construction-wand building-gadgets',
 'utility': 'emi jade appleskin mouse-tweaks controlling inventory-profiles-next polymorph sophisticated-backpacks sophisticated-storage ftb-library ftb-teams ftb-quests ftb-chunks ftb-ultimine kubejs spark chunky journeymap',
 'performance': 'sodium iris lithium ferrite-core modernfix immediatelyfast entityculling moreculling clumps',
 'atmosphere': 'ambientsounds sound-physics-remastered presence-footsteps falling-leaves not-enough-animations',
 'shader': 'complementary-reimagined',
}
CANDIDATES['ae2-addons'] = 'extended-ae advancedae mega appflux applied-energistics-2-wireless-terminals merequester ars-energistique ae-additions expanded-ae advanced-memory-card ae2-import-export-card ae2-toggleable-viewcell ae2-pattern-encoding-access-terminal ae2-auto-pattern-upload ae2-qol-client ae2-fluid-crafting-terminal ae2-terminal-mouse-wheel-scrolling ae2-automatic-requester ae2-pattern-restocker ae2-favorites ae2-crafting-priority pattern-encoding-terminal-quick-math rechiseled-ae2 create-stock-bridge'
CANDIDATES['qol-extra'] = 'storagedrawers storage-drawers-create-compat inventory-essentials inventory-profiles-next crafting-tweaks trashslot better-advancements enchantment-descriptions betterf3 jade-addons-forge crafting-on-a-stick carry-on better-third-person better-mount-hud betterf3 zoomify shulkerboxtooltip tooltipfix equipment-compare legendary-tooltips visual-workbench findme searchables configured default-options controlling just-enough-effect-descriptions-jeed justenoughbreeding just-enough-professions-jep jei'
# Explicit entries also cover projects whose published Modrinth dependency list is incomplete.
CANDIDATES['foundation'] = 'curios geckolib guideme patchouli modonomicon smartbrainlib lodestone moonlight valhelsia-core cyclops-core resourceful-lib athena irons-lib playeranimator'

def inspect(item):
    category, slug = item
    try:
        p = api('project/' + slug)
        query = {'game_versions':json.dumps(['1.21.1'])}
        if category != 'shader': query['loaders'] = json.dumps(['neoforge'])
        versions = api('project/' + p['id'] + '/version?' + urllib.parse.urlencode(query))
        releases = [v for v in versions if v['version_type']=='release']
        v = (releases or versions or [None])[0]
        return {'category':category,'requested':slug,'project':p,'version':v,'status':'available' if v else 'no-compatible-file'}
    except Exception as e:
        return {'category':category,'requested':slug,'status':'error','error':str(e)}

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(inspect, [(c,s) for c,ss in CANDIDATES.items() for s in ss.split()]))
    (ROOT/'catalog.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2),'utf-8')
    for row in rows:
        v = row.get('version')
        print(row['category'], row['requested'], v['version_number'] if v else row['status'], flush=True)
