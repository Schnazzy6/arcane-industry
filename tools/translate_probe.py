import json, urllib.parse, urllib.request
words = ['Crimson Planks Stairs','Diamond Sword','Amethyst Bricks']
url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode({'client':'gtx','sl':'en','tl':'ru','dt':'t','q':'\n'.join(words)})
data = json.load(urllib.request.urlopen(url, timeout=20))
translated = ''.join(part[0] for part in data[0]).splitlines()
print(len(translated), json.dumps(translated, ensure_ascii=False))
