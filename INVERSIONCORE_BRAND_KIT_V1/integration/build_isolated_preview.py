#!/usr/bin/env python3
"""G1 BRAND-ONLY isolated preview. Never edits an existing source tree or deploys."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'brand'
CSS = ROOT / 'integration' / 'brand-tokens.css'


def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def fail(msg: str) -> None:
    raise SystemExit('BLOCKED: ' + msg)


def git_ancestor(p: Path) -> bool:
    return any((a / '.git').exists() for a in [p, *p.parents])


def patch_html(html: str) -> str:
    old_brand = re.compile(r'<a\s+class="brand"\s+href="#top"\s+aria-label="InversionCore ana sayfa">.*?</a>', re.DOTALL)
    new_brand = ('<a class="brand ic-brand-lockup" href="#top" aria-label="InversionCore ana sayfa">'
        '<img class="ic-brand-lockup__mark" src="/assets/brand/inversioncore-mark.svg" alt="" '
        'width="48" height="48" decoding="async">'
        '<span class="ic-brand-lockup__label"><span class="ic-brand-lockup__name">Inversion<em>Core</em></span>'
        '<span class="ic-brand-lockup__tagline">TERSİNDEN DÜŞÜN · KANITLA KARAR VER</span></span></a>')
    html, n = old_brand.subn(new_brand, html)
    if n != 1: fail(f'Beklenen tek V5 marka bloğu bulunamadı (sayı={n}); şablonu tahmin ederek değiştirme.')
    old_icon = re.compile(r'<link\s+rel="icon"\s+href="/favicon.svg"\s+type="image/svg\+xml"\s*/?>')
    replacement = ('<link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml">\n'
        '<link rel="alternate icon" href="/assets/brand/favicon.ico" sizes="any">\n'
        '<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png" sizes="180x180">\n'
        '<link rel="manifest" href="/assets/brand/manifest.webmanifest">\n'
        '<meta property="og:image" content="https://inversioncore.com/assets/brand/og-cover-1200x630.png">\n'
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        '<link rel="stylesheet" href="/assets/brand/brand-tokens.css">')
    html, n = old_icon.subn(replacement, html)
    if n != 1: fail(f'Eski favicon bağlantısı tam bir adet değil (sayı={n})')
    old_footer = re.compile(r'<span class="footer-wordmark">InversionCore</span>')
    html, n = old_footer.subn('<span class="footer-wordmark ic-footer-wordmark"><img src="/assets/brand/inversioncore-mark-monochrome-white.svg" alt="" width="31" height="31" loading="lazy"> InversionCore</span>', html)
    if n != 1: fail('Footer marka alanı beklenen biçimde değil')
    if html.count('id="analysisWorkbench"') != 1: fail('Tek analiz alanı korunmamış')
    if html.count('<script') < 3: fail('V5 JS dosyaları beklenen sayıda değil')
    return html


def main() -> None:
    ap = argparse.ArgumentParser(description='Preview-only InversionCore logo application')
    ap.add_argument('--source-public', required=True, type=Path, help='V5 ZIP içindeki public dizini')
    ap.add_argument('--out', required=True, type=Path, help='Yeni oluşturulacak izole ön izleme dizini')
    ap.add_argument('--expected-sha256', required=True, help='Kaynak index.html beklenen SHA256; fail-closed')
    args = ap.parse_args()
    src = args.source_public.expanduser().resolve()
    out = args.out.expanduser().resolve()
    if not src.is_dir() or not (src / 'index.html').is_file(): fail('Kaynak public/index.html yok')
    if len(args.expected_sha256) != 64 or any(c not in '0123456789abcdefABCDEF' for c in args.expected_sha256): fail('Geçersiz SHA-256')
    before = digest(src / 'index.html')
    if before.lower() != args.expected_sha256.lower(): fail(f'Kaynak hash uyuşmazlığı: {before}')
    if out.exists(): fail('Çıkış dizini zaten var. Asla üstüne yazma.')
    if out == src or src in out.parents or out in src.parents: fail('Kaynak ve hedef birbirinin içinde olamaz')
    if git_ancestor(out.parent): fail('Çıktı bir Git çalışma ağacında olamaz. Harici izole dizin seç.')
    original = (src / 'index.html').read_text('utf-8')
    updated = patch_html(original)
    out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(src, out, dirs_exist_ok=True)
    (out / 'assets' / 'brand').mkdir(parents=True, exist_ok=True)
    for asset in ASSETS.iterdir():
        if asset.is_file(): shutil.copy2(asset, out / 'assets' / 'brand' / asset.name)
    shutil.copy2(CSS, out / 'assets' / 'brand' / 'brand-tokens.css')
    (out / 'index.html').write_text(updated, 'utf-8')
    base = {'source_public':str(src), 'source_index_sha256':before,'preview_index_sha256':digest(out/'index.html'),
       'scope':'BRAND_ONLY_PREVIEW', 'live_repo_edited':False, 'deploy_performed':False}
    (out / 'BRAND_PREVIEW_EVIDENCE.json').write_text(json.dumps(base, ensure_ascii=False, indent=2) + '\n')
    for p in src.rglob('*'):
        if p.is_file() and p.relative_to(src).as_posix() != 'index.html':
            if digest(p) != digest(out/p.relative_to(src)): fail(f'Kaynak dosya değişmiş: {p.relative_to(src)}')
    print(json.dumps({'status':'PREVIEW_CREATED','output':str(out),'source_sha256':before, 'preview_sha256':base['preview_index_sha256'], 'live_repo_edited':False},ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
