import sys,json
sys.stdout.reconfigure(encoding='utf-8')
from catalog import api
from urllib.parse import urlencode
for q in sys.argv[1:]:
    data=api('search?'+urlencode({'query':q,'limit':40,'facets':json.dumps([['versions:1.21.1'],['categories:neoforge']])}))
    print(q,[(x['slug'],x['title']) for x in data['hits']])
