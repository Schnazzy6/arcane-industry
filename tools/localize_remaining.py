"""Draft missing Russian item/block/enchantment labels into KubeJS language files.

Uses the installed English strings as source, never external resource packs.
The cache permits review and reruns without repeating network requests.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODS = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft/mods'
DEST = ROOT / 'overrides/client/kubejs/assets'
CACHE = ROOT / 'build/translation-draft-cache.json'
translated = json.loads(CACHE.read_text('utf-8')) if CACHE.exists() else {}
missing = {}
for jar in MODS.glob('*.jar'):
    try:
        with zipfile.ZipFile(jar) as archive:
            paths = set(archive.namelist())
            for name in paths:
                if not name.startswith('assets/') or not name.endswith('/lang/en_us.json'):
                    continue
                namespace = name.split('/')[1]
                en = json.loads(archive.read(name))
                ru_name = name.replace('/en_us.json', '/ru_ru.json')
                ru = json.loads(archive.read(ru_name)) if ru_name in paths else {}
                custom = DEST / namespace / 'lang/ru_ru.json'
                own = json.loads(custom.read_text('utf-8')) if custom.exists() else {}
                for key, value in en.items():
                    if (key.startswith(('item.', 'block.', 'enchantment.')) and key not in ru and key not in own
                            and isinstance(value, str) and value and '%' not in value and '\n' not in value
                            and re.search('[A-Za-z]', value)):
                        missing[(namespace, key)] = value
    except (zipfile.BadZipFile, ValueError, KeyError):
        continue

unique = sorted(set(missing.values()) - translated.keys())
print('draft labels', len(missing), 'unique new phrases', len(unique), flush=True)
for start in range(0, len(unique), 24):
    chunk = unique[start:start + 24]
    query = '\n'.join(chunk)
    url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode(
        {'client':'gtx','sl':'en','tl':'ru','dt':'t','q':query})
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.load(response)
            result = ''.join(part[0] for part in data[0]).splitlines()
            if len(result) != len(chunk):
                raise ValueError(f'line count {len(result)} != {len(chunk)}')
            for source, target in zip(chunk, result):
                if re.search('[А-Яа-яЁё]', target):
                    translated[source] = target.strip()
            break
        except Exception as error:
            if attempt == 3:
                print('skipped batch', start, repr(error), flush=True)
            else:
                time.sleep(2 ** attempt)
    if start % 480 == 0:
        CACHE.write_text(json.dumps(translated, ensure_ascii=False), 'utf-8')
        print('drafted', start + len(chunk), '/', len(unique), flush=True)
    time.sleep(0.12)
CACHE.write_text(json.dumps(translated, ensure_ascii=False), 'utf-8')

for namespace in sorted({namespace for namespace, _ in missing}):
    path = DEST / namespace / 'lang/ru_ru.json'
    current = json.loads(path.read_text('utf-8')) if path.exists() else {}
    for (ns, key), source in missing.items():
        if ns == namespace and source in translated:
            current.setdefault(key, translated[source])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('written', sum(source in translated for source in missing.values()), '/', len(missing), flush=True)
