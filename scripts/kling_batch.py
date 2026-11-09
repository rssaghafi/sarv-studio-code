#!/usr/bin/env python3
"""Resumable Kling 3.0 Pro image-to-video batch (fal queue). clips.json: list of
{id, start_url, prompt, elements:[{frontal_image_url, reference_image_urls}], duration, request_id, status}
Steps: submit <dir> [ids...] | collect <dir>   Files land in <dir>/clips/<id>.mp4. generate_audio is always false."""
import json, os, sys, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__))
for l in open(os.path.join(HERE,'..','.env')):
    if '=' in l and not l.startswith('#'):
        k,v=l.strip().split('=',1); os.environ.setdefault(k,v.strip('"\''))
KEY=os.environ['FAL_KEY']; EP='fal-ai/kling-video/v3/pro/image-to-video'
NEG="camera movement, camera pan, zoom, push-in, wing beat, wings flapping, head turn toward camera, morphing, face change, glossy surface, shimmering texture, text, letters, blur, distort, low quality"
def req(url,data=None):
    r=urllib.request.Request(url,data=json.dumps(data).encode() if data is not None else None,headers={'Authorization':'Key '+KEY,'Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(r,timeout=90))
def load(d): return json.load(open(os.path.join(d,'clips.json')))
def save(d,c): json.dump(c,open(os.path.join(d,'clips.json'),'w'),indent=1)
def submit(d,only):
    cs=load(d)
    for c in cs:
        if c.get('request_id') or (only and c['id'] not in only): continue
        inp={'start_image_url':c['start_url'],'prompt':c['prompt'],'duration':str(c.get('duration',5)),'generate_audio':False,
             'elements':c['elements'],'negative_prompt':NEG,'cfg_scale':0.5}
        j=req('https://queue.fal.run/'+EP,inp); c['request_id']=j['request_id']; c['status']='submitted'; save(d,cs); print('submitted',c['id'],j['request_id'])
def collect(d):
    cs=load(d); os.makedirs(os.path.join(d,'clips'),exist_ok=True)
    for c in cs:
        out=os.path.join(d,'clips',c['id']+'.mp4')
        if not c.get('request_id') or os.path.exists(out): continue
        try:
            s=req(f"https://queue.fal.run/fal-ai/kling-video/requests/{c['request_id']}/status")
            if s.get('status')!='COMPLETED': print('pending',c['id'],s.get('status')); continue
            j=req(f"https://queue.fal.run/fal-ai/kling-video/requests/{c['request_id']}")
            urllib.request.urlretrieve(j['video']['url'],out); c['status']='done'; print('got',out)
        except Exception as e: print('pending/err',c['id'],e)
    save(d,cs)
if __name__=='__main__':
    {'submit':lambda d:submit(d,sys.argv[3:]),'collect':collect}[sys.argv[1]](sys.argv[2])
