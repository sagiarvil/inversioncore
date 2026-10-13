#!/usr/bin/env python3
"""Independent offline integrity checks for isolated brand preview only."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
from PIL import Image
import json, re, tempfile, subprocess, shutil, sys
B = Path(__file__).resolve().parents[1]
brand=B/'assets'/'brand';src=B/'preview'/'v5-original-public'; dst=B/'preview'/'v5-branded-public'
assert (src/'index.html').exists() and (dst/'index.html').exists()
S=(src/'index.html').read_text(); D=(dst/'index.html').read_text()
for f in brand.glob('*.svg'):
    r=ET.parse(f).getroot();assert r.attrib.get('viewBox'),f
for n,sz in [('icon-192.png',(192,192)),('icon-512.png',(512,512)),('apple-touch-icon.png',(180,180)),('og-cover-1200x630.png',(1200,630)),('favicon-16.png',(16,16)),('favicon-32.png',(32,32))]:
    with Image.open(brand/n) as im: assert im.size==sz,(n,im.size)
assert S.count('id="analysisWorkbench"')==1==D.count('id="analysisWorkbench"')
assert D.count('class="brand ic-brand-lockup"')==1
assert '/assets/brand/favicon.svg' in D and '/assets/brand/brand-tokens.css' in D
for pat in ['id="decisionInput"','id="submitDecision"','id="dialogueStream"','/assets/js/interview.js','/assets/js/site.js']:
    assert pat in S and pat in D,pat
for f in src.rglob('*'):
    if f.is_file() and f.name!='index.html':
        assert sha256(f.read_bytes()).digest() == sha256((dst/f.relative_to(src)).read_bytes()).digest(),f
for f in brand.iterdir():
    if f.is_file(): assert (dst/'assets'/'brand'/f.name).read_bytes()==f.read_bytes(),f
assert '<script src="/api_worker.js"' not in D
# Exact source hash lock failures must refuse without creating destination
p=B/'integration'/'build_isolated_preview.py'
with tempfile.TemporaryDirectory() as td:
    result=subprocess.run([sys.executable,str(p),'--source-public',str(src),'--out',str(Path(td)/'must-not-exist'),'--expected-sha256','0'*64],capture_output=True,text=True)
    assert result.returncode!=0 and 'BLOCKED' in (result.stdout+result.stderr)
    assert not (Path(td)/'must-not-exist').exists()
print(json.dumps({'checks':['svg_xml_valid','icon_pixel_sizes','V5_ids_preserved','V5_script_references_preserved','original_assets_unchanged','brand_assets_copied','no_fake_engine_connected','wrong_hash_blocked'], 'status':'PASS','count':8},ensure_ascii=False,indent=2))
