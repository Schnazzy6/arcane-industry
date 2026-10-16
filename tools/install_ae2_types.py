"""Install the tested AE2 type-limit addon and a conservative 256-type cap."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile
from catalog import ROOT

FILENAME = 'no-more-63-ae2-1.21.1-neoforge-0.1.3.jar'
FILE_ID = 8662349
SLUG = 'no-more-63-ae2'


def install():
    source = ROOT / 'cache/files' / FILENAME
    data = source.read_bytes()
    with zipfile.ZipFile(source) as jar:
        assert jar.testzip() is None
        assert 'META-INF/neoforge.mods.toml' in jar.namelist()
    row = dict(slug=SLUG, title='No More 63 AE2',
               curseforge_project_id=1585209, curseforge_file_id=FILE_ID,
               version='0.1.3', filename=FILENAME,
               url=f'https://edge.forgecdn.net/files/{FILE_ID//1000}/{FILE_ID%1000:03d}/{FILENAME}',
               sha512=hashlib.sha512(data).hexdigest(), sha1=hashlib.sha1(data).hexdigest(),
               size=len(data), client=True, server=True, category='storage',
               source=f'https://www.curseforge.com/minecraft/mc-mods/{SLUG}/files/{FILE_ID}')
    config = ROOT / 'overrides/common/config/no_more_63_ae2.toml'
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text('# AE2 item types per standard ME cell; keeps the default byte capacity.\n'
                      'maxItemTypesPerCell = 256\n', 'utf-8')
    paths = [ROOT / 'build/server', ROOT / 'build/prism/Arcane Industry Prototype/minecraft',
             Path(os.environ['APPDATA']) / 'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft']
    for target in paths:
        assert (target / 'mods').is_dir(), target
        shutil.copy2(source, target / 'mods' / FILENAME)
        shutil.copy2(config, target / 'config' / config.name)
    pack_file = ROOT / 'pack.lock.json'
    pack = json.loads(pack_file.read_text('utf-8'))
    pack['mods'] = sorted([r for r in pack['mods'] if r['slug'] != SLUG] + [row], key=lambda r: r['slug'])
    pack_file.write_text(json.dumps(pack, ensure_ascii=False, indent=2), 'utf-8')
    qol_file = ROOT / 'qol.lock.json'
    qol = json.loads(qol_file.read_text('utf-8'))
    qol = sorted([r for r in qol if r['slug'] != SLUG] + [row], key=lambda r: r['slug'])
    qol_file.write_text(json.dumps(qol, ensure_ascii=False, indent=2), 'utf-8')
    print('AE2 standard item cell type cap: 256 (client and server staged).')


if __name__ == '__main__':
    install()
