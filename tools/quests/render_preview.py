"""Render a review image from the same scene used by the SNBT builder (not a game screenshot)."""
import json, pathlib, textwrap, zipfile, os, io
from PIL import Image, ImageDraw, ImageFont
root=pathlib.Path(__file__).resolve().parents[2]
chapters=json.loads((root/'build/quest-scenes.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
heading=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',18)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',10)
scale=28
prism=pathlib.Path(os.environ['APPDATA'])/'PrismLauncher'
jars=[prism/'libraries/com/mojang/minecraft/1.21.1/minecraft-1.21.1-client.jar']+sorted((root/'build/server/mods').glob('*.jar'))
textures={}
for jar in jars:
    with zipfile.ZipFile(jar) as z:
        for p in z.namelist():
            if p.startswith('assets/') and '/textures/' in p and p.endswith('.png'):
                parts=p.split('/')
                ns=parts[1]
                name=pathlib.PurePosixPath(p).stem
                key=ns+':'+name
                if key not in textures or '/textures/item/' in p:
                    textures[key]=(jar,p)
def icon(id):
    if not id or id not in textures:return None
    jar,p=textures[id]
    try:
        with zipfile.ZipFile(jar) as z:
            im=Image.open(io.BytesIO(z.read(p))).convert('RGBA')
            if im.height>im.width:im=im.crop((0,0,im.width,im.width))
            return im.resize((28,28),Image.Resampling.NEAREST)
    except Exception:return None
for ch in chapters[:3]:
    imgs=ch['images']
    minx=min(i['x']-i['w']/2 for i in imgs)-1
    maxx=max(i['x']+i['w']/2 for i in imgs)+1
    miny=min(i['y']-i['h']/2 for i in imgs)-2.5
    maxy=max(i['y']+i['h']/2 for i in imgs)+1
    def xy(x,y):return (round((x-minx)*scale),round((y-miny)*scale))
    im=Image.new('RGB',(round((maxx-minx)*scale),round((maxy-miny)*scale)), '#0d1520')
    d=ImageDraw.Draw(im)
    d.text((28,12),ch['t']+' · предпросмотр раскладки',font=heading,fill='#eee6d5')
    for panel in imgs:
        box=(*xy(panel['x']-panel['w']/2,panel['y']-panel['h']/2),*xy(panel['x']+panel['w']/2,panel['y']+panel['h']/2))
        d.rounded_rectangle(box,8,fill=panel['color'])
        if panel.get('text'):
            d.text(xy(panel['x'],panel['y']),panel['text'],font=heading,fill='#f8f4e7',anchor='mm')
    quests={q['k']:q for q in ch['quests']}
    for q in ch['quests']:
        if q.get('hideLines'):continue
        for dep in q.get('dep',[]):
            p=quests.get(dep)
            if p:d.line([xy(*p['at']),xy(*q['at'])],fill='#95b7c8',width=2)
    for q in ch['quests']:
        x,y=xy(*q['at']);r=19 if q.get('main') else 17
        col='#bd974e' if q.get('main') else '#528570' if q.get('opt') else '#526e90'
        d.rounded_rectangle((x-r,y-r,x+r,y+r),8,fill='#17212d',outline=col,width=2)
        tex=icon(q.get('icon') or (q['task'][0] if isinstance(q['task'],list) and isinstance(q['task'][0],str) else None))
        if tex:im.paste(tex,(x-14,y-14),tex)
        else:d.text((x,y),'✓' if q['task']=='check' else '◆',font=font,fill=col,anchor='mm')
        lines=textwrap.wrap(q['t'],width=15)[:3]
        for n,line in enumerate(lines):d.text((x,y+r+5+n*12),line,font=small,fill='#d7e1e8',anchor='mt')
    target=root/'build'/('quest-layout-'+ch['k']+'.png')
    im.save(target)
    print(target)
