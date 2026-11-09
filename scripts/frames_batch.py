#!/usr/bin/env python3
"""Resumable Nano Banana Pro edit batch. shots.csv columns:
id,attempt,refs,aspect,seed,prompt_key,request_id,status   (refs = ';'-joined basenames from refs_urls.json)
prompts.json: {prompt_key: full prompt}.  Steps: submit <dir> [ids...] | collect <dir>
Images land in <dir>/gen/<id>_a<attempt>.png. Every submit is logged to <dir>/jobs.csv immediately."""
import csv, json, os, sys, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(HERE,'..','.env')):
    if '=' in l and not l.startswith('#'):
        k,v=l.strip().split('=',1); os.environ.setdefault(k,v.strip('"\''))
KEY=os.environ['FAL_KEY']; EP='fal-ai/nano-banana-pro/edit'
def req(url,data=None):
    r=urllib.request.Request(url,data=json.dumps(data).encode() if data is not None else None,
        headers={'Authorization':'Key '+KEY,'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(r,timeout=90))
def load(d): return list(csv.DictReader(open(os.path.join(d,'shots.csv'))))
def save(d,rows):
    with open(os.path.join(d,'shots.csv'),'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
def submit(d,only):
    rows=load(d); urls=json.load(open(os.path.join(d,'refs_urls.json'))); P=json.load(open(os.path.join(d,'prompts.json')))
    for r in rows:
        if r['request_id'] or (only and r['id'] not in only): continue
        inp={'prompt':P[r['prompt_key']],'image_urls':[urls[x] for x in r['refs'].split(';')],
             'resolution':'2K','aspect_ratio':r['aspect'],'seed':int(r['seed']),'output_format':'png'}
        j=req('https://queue.fal.run/'+EP,inp); r['request_id']=j['request_id']; r['status']='submitted'; save(d,rows)
        print('submitted',r['id'],r['attempt'])
def collect(d):
    rows=load(d); os.makedirs(os.path.join(d,'gen'),exist_ok=True)
    for r in rows:
        out=os.path.join(d,'gen',f"{r['id']}_a{r['attempt']}.png")
        if not r['request_id'] or os.path.exists(out): continue
        try:
            j=req(f"https://queue.fal.run/fal-ai/nano-banana-pro/requests/{r['request_id']}")
            urllib.request.urlretrieve(j['images'][0]['url'],out); r['status']='done'; print('got',out)
        except Exception as e: print('pending',r['id'],e)
    save(d,rows)
if __name__=='__main__':
    {'submit':lambda d:submit(d,sys.argv[3:]),'collect':collect}[sys.argv[1]](sys.argv[2])
