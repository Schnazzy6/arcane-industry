import hashlib,json,pathlib,re,zipfile
from catalog import ROOT
dist=ROOT/'dist'
lock=json.loads((dist/'manifest.lock.json').read_text('utf-8'))
mods=lock['mods']
assert lock['neoforge']=='21.1.259'
banned={'raised','arcane-industry-diet','draconic-evolution','brandons-core','falling-leaves','modern-dynamics','ae-additions','expanded-ae','inventory-profiles-next','ae2-auto-pattern-upload','ae2-automatic-requester','ae2-pattern-restocker','appleskin','curios-continuation','epic-knights-shields-armor-and-weapons'}
assert not banned.intersection(x['slug'] for x in mods)
required={'almostunified','toast-control','disableinsecurechattoast','gravestone-mod','gravestone-carryables','baguettelib','no-recipe-book-system','mekanism-extras','applied-mekanistics','just-enough-mekanism-multiblocks','extra_enchantments','dis-enchanting-table','born-in-chaos','twilight-forest','eternal-starlight','more-relics','reliquified-artifacts','reliquified-ars-nouveau','reliquified-l-ender-s-cataclysm','reliquified-twilight-forest','apothic-compats','immersive-armors','blur-plus','mekanism','mekanism-generators','pipez','croptopia','epherolib','cooking-for-blockheads','effortless-building','emi-loot','emi-ores','chat-heads','leaves-be-gone','epic-samurais','ars-elemancy','fresh-animations','entity-model-features','entitytexturefeatures','not-enough-animations','modern-industrialization','extended-industrialization','re-avaritia','ae2','mega','storagedrawers','lootr','apotheosis','spice-of-life-valheim-reforged','industrialization-overdrive','yet-another-industrialization','mi-utilities','modern-industrialization-sound-addon','mi-multiblock-emi'}
assert required.issubset(x['slug'] for x in mods)
for side,filename,prefix in [('client','ArcaneIndustry-0.1.4-Prism.zip','Arcane Industry Prototype/minecraft/'),('server','ArcaneIndustry-0.1.4-Server-Windows.zip','server/')]:
    with zipfile.ZipFile(dist/filename) as z:
        names=z.namelist()
        assert not any(any(v in n.lower() for v in ['accounts.json','smoke-test-world','crash-reports/','/logs/','/ops.json']) or n.startswith('server/world/') for n in names)
        expected={x['filename'] for x in mods if x[side] and not x['filename'].endswith('.zip')}
        actual={pathlib.PurePosixPath(n).name for n in names if n.startswith(prefix+'mods/') and n.endswith('.jar')}
        assert expected==actual,(side,expected-actual,actual-expected)
        for m in mods:
            if not m[side]:continue
            folder='resourcepacks' if m['category']=='resourcepack' else 'shaderpacks' if m['filename'].endswith('.zip') else 'mods'
            data=z.read(prefix+folder+'/'+m['filename'])
            assert hashlib.sha512(data).hexdigest()==m['sha512'],m['filename']
        if side=='client':
            options=z.read(prefix+'options.txt').decode()
            keys=[s.split(':',1)[0] for s in options.splitlines() if ':' in s]
            assert len(keys)==len(set(keys))
            assert 'version:3955' in options
            assert 'file/ArcaneIndustry-HUD.zip' in options
            assert prefix+'resourcepacks/ArcaneIndustry-HUD.zip' in names
            assert b'"default"' in z.read(prefix+'config/sol_valheim_reforged-client.toml')
            assert b'hideVanillaCraftingGuide = true' in z.read(prefix+'config/craftingtweaks-common.toml')
            assert 'key_iris.keybind.toggleShaders:key.keyboard.f6' in options
            cfg=z.read('Arcane Industry Prototype/instance.cfg').decode()
            assert 'C:/Users/' not in cfg
        else:
            args=z.read('server/libraries/net/neoforged/neoforge/21.1.259/win_args.txt').decode()
            assert 'C:' not in args
            for rel in re.findall(r'libraries/[^;\s]+\.jar',args):assert 'server/'+rel in names,rel
            assert 'server/runtime/bin/java.exe' in names
            assert b'online-mode=true' in z.read('server/server.properties')
            assert b'eula=false' in z.read('server/eula.txt')
            assert b'bidirectionalEnergyCompat = true' in z.read(prefix+'config/modern_industrialization-startup.toml')
            assert prefix+'config/almostunified/unification/arcane_metals.json' in names
    print(side,'verified',len(actual),'jars')
print('Release file hashes, side separation, required content, removed duplicates, options and portable server paths: PASS')
