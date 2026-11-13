#!/usr/bin/env python3
"""Build evidence/index.html from docs/evidence/ai-subsidy.md. Run from the repo root."""
import html, re
from urllib.parse import urlparse

src = open('docs/evidence/ai-subsidy.md').read().replace(' Nothing here is used in site copy yet.', '')
RATING = {'STRONG': 'strong', 'LIST-PRICE': 'list', 'SECONDARY': 'secondary', 'Strong': 'counter', 'Medium': 'counter'}

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    def link(m):
        u = m.group(0).rstrip('.,')
        return '<a href="%s" target="_blank" rel="noopener">%s ↗</a>%s' % (u, urlparse(u).netloc.replace('www.', ''), m.group(0)[len(u):])
    return re.sub(r'https?://[^\s<]+', link, t)

def badge(cell):
    key = cell.split(',')[0].strip()
    cls = RATING.get(key)
    return '<span class="tag %s">%s</span>' % (cls, html.escape(cell)) if cls else inline(cell)

out, lines, i = [], src.split('\n'), 0
while i < len(lines):
    l = lines[i]
    if l.startswith('# '):
        i += 1; continue
    if l.startswith('## '):
        t = l[3:]; sid = 's' + t.split('.')[0]
        out.append('<h2 id="%s">%s</h2>' % (sid, inline(t)))
    elif l.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
        head, body = rows[0], rows[2:]
        out.append('<div class="cards">')
        for r in body:
            out.append('<article>%s<p>%s</p><small>%s · %s</small></article>' % (badge(r[0]), inline(r[1]), inline(r[2]), inline(r[3])))
        out.append('</div>'); continue
    elif re.match(r'(\d+\.|-) ', l):
        tag = 'ol' if l[0].isdigit() else 'ul'
        out.append('<%s>' % tag)
        while i < len(lines) and re.match(r'(\d+\.|-) ', lines[i]):
            out.append('<li>%s</li>' % inline(re.sub(r'^(\d+\.|-) ', '', lines[i]))); i += 1
        out.append('</%s>' % tag); continue
    elif l.strip():
        out.append('<p>%s</p>' % inline(l))
    i += 1

page = open('scripts/evidence-shell.html').read().replace('<!--BODY-->', '\n'.join(out))
open('evidence/index.html', 'w').write(page)
