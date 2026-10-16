const fs=require('fs'),path=require('path');const dir='tools/quests';
const chs=require('./load')();
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const all={};chs.forEach(c=>c.quests.forEach(q=>{all[q.k]=q;q._c=c.k;}));
let html='<html><body style="background:#2b2b2b;color:#ddd;font:12px sans-serif">';
for(const c of chs){const xs=c.quests.map(q=>q.at[0]).concat((c.images||[]).flatMap(i=>[i.x-i.w/2,i.x+i.w/2])),ys=c.quests.map(q=>q.at[1]).concat((c.images||[]).flatMap(i=>[i.y-i.h/2,i.y+i.h/2]));
 const minx=Math.min(...xs)-1,miny=Math.min(...ys)-1,S=40;const W=(Math.max(...xs)-minx+1)*S,H=(Math.max(...ys)-miny+1)*S;
 const X=x=>(x-minx)*S,Y=y=>(y-miny)*S;let s=`<h3>${c.t}</h3><svg width="${W}" height="${H}" style="background:#3c3c3c">`;
 (c.images||[]).forEach(im=>{s+=`<rect x="${X(im.x-im.w/2)}" y="${Y(im.y-im.h/2)}" width="${im.w*S}" height="${im.h*S}" rx="8" fill="${im.color}"/>`;if(im.text)s+=`<text x="${X(im.x)}" y="${Y(im.y)+5}" text-anchor="middle" fill="#f4eee1" font-size="18" font-weight="bold">${esc(im.text)}</text>`;});
 const pos={};c.quests.forEach(q=>pos[q.k]=q.at);(c.links||[]).forEach(l=>pos[l.k]=l.at);
 c.quests.forEach(q=>{if(q.hideLines)return;(q.dep||[]).forEach(d=>{const p=pos[d];if(!p)return;s+=`<line x1="${X(p[0])}" y1="${Y(p[1])}" x2="${X(q.at[0])}" y2="${Y(q.at[1])}" stroke="#9ab" stroke-width="2"/>`;});});
 (c.links||[]).forEach(l=>s+=`<circle cx="${X(l.at[0])}" cy="${Y(l.at[1])}" r="${S*0.3}" fill="#555" stroke="#fc6" stroke-dasharray="3"/>`);
 c.quests.forEach(q=>{const r=S*(q.main?0.42:0.3);const col=q.main?'#d9a520':q.opt?'#6a8':q.task==='check'?'#88a':'#bbb';
  s+=q.opt?`<polygon points="${[0,1,2,3,4,5].map(i=>[X(q.at[0])+r*Math.cos(i*Math.PI/3),Y(q.at[1])+r*Math.sin(i*Math.PI/3)].join(',')).join(' ')}" fill="${col}"/>`:`<circle cx="${X(q.at[0])}" cy="${Y(q.at[1])}" r="${r}" fill="${col}"/>`;
  s+=`<title>${esc(q.t)}</title><text x="${X(q.at[0])}" y="${Y(q.at[1])+r+17}" fill="#eee" font-size="12" text-anchor="middle">${esc(q.t.slice(0,23))}</text>`;});
 html+=s+'</svg>';}
fs.writeFileSync(process.argv[2],html+'</body></html>');
fs.writeFileSync(require('path').join(require('path').dirname(process.argv[2]),'quest-scenes.json'),JSON.stringify(chs,null,2));
