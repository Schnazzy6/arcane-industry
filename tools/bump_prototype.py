from catalog import ROOT
p=ROOT/'tools/package.py'
p.write_text(p.read_text('utf-8').replace('0.1.0','0.1.1'),'utf-8')
