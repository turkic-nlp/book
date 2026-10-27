#!/usr/bin/env python3
"""Local publication regression checks; does not deploy or certify factual claims.
Requires beautifulsoup4 and pymupdf. Run after scripts/render-all.sh.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter
import argparse, hashlib, json, posixpath, re, zipfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pymupdf as fitz

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
parser.add_argument('--report', type=Path)
a = parser.parse_args(); root = a.root.resolve(); build = root / '_book'
errors = []; cache = {}; links = images = 0

def soup(p):
    if p not in cache:
        cache[p] = BeautifulSoup(p.read_text(), 'html.parser')
    return cache[p]

pages = [p for p in build.rglob('*.html') if 'site_libs' not in p.parts]
if not pages: errors.append('Missing HTML build')
for p in pages:
    main = soup(p).select_one('main')
    if not main: continue
    ids = [n['id'] for n in main.select('[id]')]
    if len(ids) != len(set(ids)): errors.append(f'{p.name}: duplicate main IDs')
    for n in main.select('a[href], img[src]'):
        img = n.name == 'img'; u = urlsplit(n.get('src' if img else 'href'))
        if u.scheme or u.netloc: continue
        target = (p.parent / unquote(u.path)).resolve() if u.path else p
        if img: images += 1
        else: links += 1
        if not target.exists(): errors.append(f'{p.name}: missing {u.geturl()}')
        elif u.fragment and target.suffix == '.html' and not soup(target).find(id=unquote(u.fragment)):
            errors.append(f'{p.name}: missing anchor {u.geturl()}')
    for n in main.select('.quarto-xref'):
        if '??' in n.get_text(): errors.append(f'{p.name}: unresolved cross-reference')

notebooks = list((root / 'exercises').glob('*.ipynb'))
for p in notebooks:
    n = json.loads(p.read_text())
    if n.get('nbformat') != 4 or not n.get('cells'): errors.append(f'{p.name}: invalid notebook')
    for cell in n['cells']:
        source = ''.join(cell.get('source', []))
        if re.search(r'@(?:tbl-|fig-|Johanson_)', source): errors.append(f'{p.name}: unresolved book reference')
        if cell['cell_type'] == 'code' and (cell.get('outputs') or cell.get('execution_count') is not None):
            errors.append(f'{p.name}: saved execution state')

pdfs = list(build.glob('*.pdf')); pdf_info = {}
if len(pdfs) != 1: errors.append(f'Expected one PDF, found {len(pdfs)}')
else:
    doc = fitz.open(pdfs[0]); edge = []; glyphs = []
    publication = ' '.join(doc[1].get_text().split()) if len(doc) > 2 else ''
    for expected in ['Version 0.1.0, 2026', '10.5281/zenodo.23324599', 'Creative Commons']:
        if expected not in publication: errors.append(f'PDF publication page missing {expected}')
    if len(doc) < 3 or 'Preface' not in doc[2].get_text():
        errors.append('PDF preface must follow publication page')
    if not doc[0].get_images(): errors.append('PDF cover image missing')

    for i,p in enumerate(doc):
        for block in p.get_text('dict')['blocks']:
            if block['type'] != 0: continue
            for line in block['lines']:
                for span in line['spans']:
                    x0,y0,x1,y1 = span['bbox']
                    if x0 < 20 or x1 > p.rect.width-20 or y0 < 10 or y1 > p.rect.height-12:
                        edge.append({'page':i+1,'text':span['text']})
                    if '\ufffd' in span['text']: glyphs.append(i+1)
    if edge: errors.append('PDF text near/outside page edge; inspect report')
    if glyphs: errors.append('PDF replacement characters')
    pdf_info = {'pages':len(doc),'page_edge_spans':edge,'replacement_glyph_pages':glyphs,
                'sha256':hashlib.sha256(pdfs[0].read_bytes()).hexdigest()}

epubs = list(build.glob('*.epub')); epub_info = {}
if len(epubs) != 1: errors.append(f'Expected one EPUB, found {len(epubs)}')
else:
    with zipfile.ZipFile(epubs[0]) as z:
        names = set(z.namelist()); first = z.infolist()[0]
        if first.filename != 'mimetype' or first.compress_type != zipfile.ZIP_STORED or z.read('mimetype') != b'application/epub+zip':
            errors.append('Invalid EPUB mimetype packaging')
        container = ET.fromstring(z.read('META-INF/container.xml'))
        opf = container.find('.//{*}rootfile').attrib['full-path']; package = ET.fromstring(z.read(opf))
        base = posixpath.dirname(opf); manifest = {}
        for item in package.findall('.//{*}manifest/{*}item'):
            path = posixpath.normpath(posixpath.join(base,unquote(item.attrib['href'])))
            manifest[item.attrib['id']] = path
            if path not in names: errors.append(f'EPUB missing manifest item: {path}')
        spine = [manifest.get(x.attrib['idref']) for x in package.findall('.//{*}spine/{*}itemref')]
        if None in spine: errors.append('EPUB spine refers to unknown item')
        documents = {p:ET.fromstring(z.read(p)) for p in names if p.endswith('.xhtml')}
        checked = 0
        for p,doc in documents.items():
            for node in doc.iter():
                for attr in ('href','src','{http://www.w3.org/1999/xlink}href'):
                    if attr not in node.attrib: continue
                    u = urlsplit(node.attrib[attr])
                    if u.scheme or u.netloc: continue
                    dest = posixpath.normpath(posixpath.join(posixpath.dirname(p),unquote(u.path))) if u.path else p
                    checked += 1
                    if dest not in names: errors.append(f'EPUB {p}: missing {dest}')
                    elif u.fragment and dest in documents and not any(x.get('id') == unquote(u.fragment) for x in documents[dest].iter()):
                        errors.append(f'EPUB {p}: missing anchor {dest}#{u.fragment}')
        meta = package.find('{*}metadata')
        if [n.text for n in meta.findall('{*}language')] != ['en']:
            errors.append('EPUB language must be en')
        if not any('CC BY-SA 4.0' in (n.text or '') for n in meta.findall('{*}rights')):
            errors.append('EPUB rights metadata missing CC BY-SA 4.0')
        if len(spine) < 3 or not any(n.get('id') == 'publication-details' for n in documents[spine[1]].iter()):
            errors.append('EPUB publication details must immediately follow cover')
        if len(spine) < 3 or not any(n.get('id') == 'preface' for n in documents[spine[2]].iter()):
            errors.append('EPUB preface must follow publication details')

        epub_info = {'documents':len(documents),'local_references_checked':checked,'spine':spine,
                     'metadata':{k:[n.text for n in meta.findall('{*}'+k)] for k in ['title','creator','identifier','rights','language']},
                     'sha256':hashlib.sha256(epubs[0].read_bytes()).hexdigest()}
report = {'html_pages':len(pages),'internal_html_links_checked':links,'local_html_images_checked':images,
          'notebooks_checked':len(notebooks),'pdf':pdf_info,'epub':epub_info,'errors':errors,
          'limitations':['No external-link crawl','Does not run EPUBCheck or e-reader visual QA',
                         'PDF boundary scan does not replace visual inspection','Citation metadata and factual claims need source verification']}
if a.report: a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
