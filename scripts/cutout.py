#!/usr/bin/env python3
"""BiRefNet v2 cut-outs via fal (sync). Usage: cutout.py <outdir> file... ; writes <outdir>/<stem>_cut.png, skips existing."""
import json, os, sys, urllib.request, subprocess
HERE=os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(HERE,'..','.env')):
    if '=' in l and not l.startswith('#'):
        k,v=l.strip().split('=',1); os.environ.setdefault(k,v.strip('"\''))
KEY=os.environ['FAL_KEY']; out=sys.argv[1]; os.makedirs(out,exist_ok=True)
for f in sys.argv[2:]:
    dst=os.path.join(out,os.path.splitext(os.path.basename(f))[0]+'_cut.png')
    if os.path.exists(dst): continue
    url=subprocess.check_output([sys.executable,os.path.join(HERE,'fal_upload.py'),f]).decode()
    url=json.loads(url[url.index("{"):])[os.path.basename(f)]
    r=urllib.request.Request('https://fal.run/fal-ai/birefnet/v2',data=json.dumps({'image_url':url,'output_format':'png'}).encode(),
        headers={'Authorization':'Key '+KEY,'Content-Type':'application/json'})
    j=json.load(urllib.request.urlopen(r,timeout=120)); urllib.request.urlretrieve(j['image']['url'],dst); print('cut',dst)
