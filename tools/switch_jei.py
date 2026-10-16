"""Switch the existing Prism/server pack to JEI without rebuilding user worlds."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile
from catalog import ROOT

OLD_SLUGS = {'emi', 'emi-loot', 'emi-ores', 'mi-multiblock-emi'}
NEW = [
    ('jei', 'Just Enough Items', 238222, 8857687,
     'jei-1.21.1-neoforge-19.54.0.429.jar', '19.54.0.429'),
    ('jei-stuff', 'JEI Stuff', 978621, 8938121,
     'jeistuff-1.21.1-1.2.1.jar', '1.2.1'),
]


def row(spec):
    slug, title, project, file_id, filename, version = spec
    source = ROOT / 'cache/files' / filename
    assert source.is_file(), f'Missing verified download: {source}'
    data = source.read_bytes()
    with zipfile.ZipFile(source) as jar:
        assert jar.testzip() is None, f'Corrupt jar: {source}'
    return dict(slug=slug, title=title, curseforge_project_id=project,
                curseforge_file_id=file_id, version=version, filename=filename,
                url=f'https://edge.forgecdn.net/files/{file_id//1000}/{file_id%1000:03d}/{filename}',
                sha512=hashlib.sha512(data).hexdigest(), sha1=hashlib.sha1(data).hexdigest(),
                size=len(data), client=True, server=True, category='recipe-viewer',
                source=f'https://www.curseforge.com/minecraft/mc-mods/{slug}/files/{file_id}')


def run():
    fresh = [row(spec) for spec in NEW]
    pack_path = ROOT / 'pack.lock.json'
    pack = json.loads(pack_path.read_text('utf-8'))
    old = [r for r in pack['mods'] if r['slug'] in OLD_SLUGS | {'jei'}]
    pack['mods'] = sorted([r for r in pack['mods'] if r['slug'] not in OLD_SLUGS | {'jei', 'jei-stuff'}]
                          + fresh, key=lambda r: r['slug'])
    qol_path = ROOT / 'qol.lock.json'
    qol = json.loads(qol_path.read_text('utf-8'))
    qol = [r for r in qol if r['slug'] not in {'jei', 'jei-stuff'}] + fresh
    curse_path = ROOT / 'curse.lock.json'
    curse = [r for r in json.loads(curse_path.read_text('utf-8'))
             if r['slug'] != 'mi-multiblock-emi']
    targets = [ROOT / 'build/server', ROOT / 'build/prism/Arcane Industry Prototype/minecraft',
               Path(os.environ['APPDATA']) / 'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft']
    old_names = {r['filename'] for r in old}
    old_names.add('mimbemi-1.0.2.jar')
    for target in targets:
        moddir = target / 'mods'
        assert moddir.is_dir() and target.resolve().parent != target.resolve(), target
        for filename in old_names:
            path = moddir / filename
            if path.exists():
                assert path.resolve().parent == moddir.resolve() and path.suffix == '.jar'
                path.unlink()
        for selected in fresh:
            shutil.copy2(ROOT / 'cache/files' / selected['filename'], moddir / selected['filename'])
        shutil.copytree(ROOT / 'overrides/common', target, dirs_exist_ok=True)
        if target.name == 'minecraft':
            shutil.copytree(ROOT / 'overrides/client', target, dirs_exist_ok=True)
    # EMI-only UI resources have no JEI counterpart and are no longer loaded.
    for target in [ROOT / 'overrides/client/kubejs',
                   targets[1] / 'kubejs', targets[2] / 'kubejs']:
        path = target / 'assets/emi/index/stacks/arcane_singularities.json'
        if path.exists():
            assert path.name == 'arcane_singularities.json'
            path.unlink()
    pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), 'utf-8')
    qol_path.write_text(json.dumps(qol, ensure_ascii=False, indent=2), 'utf-8')
    curse_path.write_text(json.dumps(curse, ensure_ascii=False, indent=2), 'utf-8')
    print('JEI and JEI Stuff installed; EMI-only jars removed from client and server.')


if __name__ == '__main__':
    run()
