#!/usr/bin/env python3
"""Report which keys in .env are set (never prints values) and test each against its API."""
import os, sys, urllib.request, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
env = {}
for line in (root/".env").read_text().splitlines():
    line=line.strip()
    if line and not line.startswith("#") and "=" in line:
        k,v=line.split("=",1); env[k.strip()]=v.strip().strip('"')
def probe(url, headers):
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=10); return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception as e: return f"ERR {e.__class__.__name__}"
checks={
 "FAL_KEY": ("https://api.fal.ai/v1/models?limit=1", lambda k: {"Authorization": f"Key {k}"}),
 "ELEVENLABS_API_KEY": ("https://api.elevenlabs.io/v1/models", lambda k: {"xi-api-key": k}),
 "RUNWAYML_API_SECRET": ("https://api.dev.runwayml.com/v1/organization", lambda k: {"Authorization": f"Bearer {k}", "X-Runway-Version":"2024-11-06"}),
}
for name,(url,h) in checks.items():
    k=env.get(name,"")
    print(f"{name:22} {'set' if k else 'EMPTY':6} {probe(url,h(k)) if k else '-'}")
