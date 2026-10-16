"""Build a tiny HUD-only resource pack; no gameplay or GUI coordinate patches."""
from pathlib import Path
import json,zipfile,struct,zlib,shutil
ROOT=Path(__file__).resolve().parents[1]
def png(w,h,pixels):
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 raw=b''.join(b'\0'+b''.join(bytes(pixel) for pixel in row) for row in pixels)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
palette={' ':(0,0,0,0),'1':(0,0,0,255),'2':(0,148,255,255),'3':(209,235,255,255),'4':(86,184,255,255)}
air=['   111   ','  12221  ',' 12 3 41 ',' 12   41 ','  14441  ','   111   ','         ','         ','         ']
burst=['    2    ',' 2  1  2 ',' 12   21 ','  1   1  ','  2   2  ','         ','         ','         ','         ']
files={
 'pack.mcmeta':json.dumps({'pack':{'pack_format':34,'description':'Arcane Industry HUD: compact air bubbles and invisible empty food backgrounds'}}).encode(),
 'assets/sol_valheim_reforged/textures/screens/empty_slot.png':png(16,16,[[(0,0,0,0)]*16 for _ in range(16)]),
 'assets/minecraft/textures/gui/sprites/hud/air.png':png(9,9,[[palette[c] for c in row] for row in air]),
 'assets/minecraft/textures/gui/sprites/hud/air_bursting.png':png(9,9,[[palette[c] for c in row] for row in burst]),
}
folder=ROOT/'overrides/client/resourcepacks';folder.mkdir(parents=True,exist_ok=True)
p=folder/'ArcaneIndustry-HUD.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():z.writestr(name,data)
dest=ROOT/'build/prism/Arcane Industry Prototype/minecraft/resourcepacks';dest.mkdir(exist_ok=True);shutil.copy2(p,dest/p.name)
print('Built',p.name,'with',len(files),'files; no coordinate changes.')
