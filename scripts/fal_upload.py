#!/usr/bin/env python3
"""Upload local files to fal CDN; prints JSON {basename: url}. Usage: fal_upload.py file... [--out urls.json]
Appends to --out if it exists (skips files already uploaded)."""
import json, mimetypes, os, sys, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(HERE,'..','.env')):
    if '=' in l and not l.startswith('#'):
        k,v=l.strip().split('=',1); os.environ.setdefault(k,v.strip('"\''))
KEY=os.environ['FAL_KEY']
args=sys.argv[1:]; out=None
if '--out' in args: i=args.index('--out'); out=args[i+1]; del args[i:i+2]
res=json.load(open(out)) if out and os.path.exists(out) else {}
for f in args:
    b=os.path.basename(f)
    if b in res: continue
    ct=mimetypes.guess_type(f)[0] or 'application/octet-stream'
    r=urllib.request.Request('https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3',
        data=json.dumps({'content_type':ct,'file_name':b}).encode(),
        headers={'Authorization':'Key '+KEY,'Content-Type':'application/json'})
    j=json.load(urllib.request.urlopen(r,timeout=60))
    p=urllib.request.Request(j['upload_url'],data=open(f,'rb').read(),method='PUT',headers={'Content-Type':ct})
    urllib.request.urlopen(p,timeout=120)
    res[b]=j['file_url']; print(b,j['file_url'])
    if out: json.dump(res,open(out,'w'),indent=1)
if not out: print(json.dumps(res,indent=1))
