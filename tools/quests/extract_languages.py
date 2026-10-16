"""Extract installed mod translations deterministically; pack translations win."""
import json, pathlib, zipfile, os
root = pathlib.Path(__file__).resolve().parents[2]
out = root / 'build/quest-languages.json'
langs = {'en_us': {}, 'ru_ru': {}}
tags = {}
def merge_tag(name, data):
    parts = name.split('/')
    if len(parts) < 5 or parts[0] != 'data' or parts[2:4] != ['tags', 'item'] or not name.endswith('.json'):
        return
    key = parts[1] + ':' + '/'.join(parts[4:])[:-5]
    if data.get('replace'):
        tags[key] = []
    tags.setdefault(key, []).extend(data.get('values', []))
prism = pathlib.Path(os.environ['APPDATA']) / 'PrismLauncher'
vanilla = prism / 'libraries/com/mojang/minecraft/1.21.1/minecraft-1.21.1-client.jar'
for jar in ([vanilla] if vanilla.exists() else []) + sorted((root / 'build/server/mods').glob('*.jar')):
    with zipfile.ZipFile(jar) as z:
        for name in sorted(z.namelist()):
            if '/tags/item/' in name and name.endswith('.json'):
                try:
                    merge_tag(name, json.loads(z.read(name).decode('utf-8-sig')))
                except (ValueError, UnicodeError):
                    pass
            if name.startswith('assets/') and name.endswith(('/lang/ru_ru.json', '/lang/en_us.json')):
                try:
                    langs[pathlib.PurePosixPath(name).stem].update(json.loads(z.read(name).decode('utf-8-sig')))
                except (ValueError, UnicodeError):
                    pass
assets = prism / 'assets'
index = assets / 'indexes/17.json'
if index.exists():
    objects = json.loads(index.read_text())['objects']
    entry = objects.get('minecraft/lang/ru_ru.json')
    if entry:
        digest = entry['hash']
        translated = assets / 'objects' / digest[:2] / digest
        if translated.exists():
            langs['ru_ru'].update(json.loads(translated.read_text(encoding='utf-8')))
for base in ['overrides/common/kubejs/assets', 'overrides/client/kubejs/assets']:
    for f in sorted((root / base).glob('*/lang/*.json')):
        if f.stem in langs:
            langs[f.stem].update(json.loads(f.read_text(encoding='utf-8-sig')))
out.write_text(json.dumps(langs, ensure_ascii=False), encoding='utf-8')
for f in sorted((root / 'overrides/common/kubejs/data').glob('*/tags/item/**/*.json')):
    merge_tag('data/' + f.relative_to(root / 'overrides/common/kubejs/data').as_posix(), json.loads(f.read_text(encoding='utf-8-sig')))
(root / 'build/quest-tags.json').write_text(json.dumps(tags, ensure_ascii=False), encoding='utf-8')
print('Translations:', {k: len(v) for k, v in langs.items()})
