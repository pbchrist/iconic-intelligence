const http = require('http');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const port = Number(process.env.PORT || 3000);
const root = path.resolve(__dirname);
const types = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.webp': 'image/webp', '.xml': 'application/xml; charset=utf-8', '.txt': 'text/plain; charset=utf-8'
};
const compressible = /^(text\/|application\/(javascript|xml))/;
const blocked = new Set(['/server.js','/package.json','/README.md','/.gitignore']);

function securityHeaders() {
  return {
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=()',
    'X-Frame-Options': 'SAMEORIGIN',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; frame-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self' mailto:; object-src 'none'"
  };
}

http.createServer((req, res) => {
  const rawPath = decodeURIComponent((req.url || '/').split('?')[0]);
  if (rawPath === '/healthz') {
    res.writeHead(200, { ...securityHeaders(), 'Content-Type':'application/json; charset=utf-8', 'Cache-Control':'no-store' });
    return res.end('{"ok":true}');
  }
  let urlPath = rawPath === '/' ? '/index.html' : rawPath;
  if (blocked.has(urlPath) || urlPath.includes('/.git') || /\.(patch|md)$/i.test(urlPath)) {
    res.writeHead(404, securityHeaders()); return res.end('not found');
  }
  const file = path.resolve(root, '.' + urlPath);
  if (!file.startsWith(root + path.sep)) {
    res.writeHead(403, securityHeaders()); return res.end('forbidden');
  }
  fs.stat(file, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { ...securityHeaders(), 'Content-Type':'text/plain; charset=utf-8', 'Cache-Control':'no-store' });
      return res.end('not found');
    }
    const ext = path.extname(file).toLowerCase();
    const type = types[ext] || 'application/octet-stream';
    const etag = `W/"${stats.size.toString(16)}-${Math.floor(stats.mtimeMs).toString(16)}"`;
    const headers = {
      ...securityHeaders(), 'Content-Type': type, 'Cache-Control': 'no-cache',
      'ETag': etag, 'Last-Modified': stats.mtime.toUTCString(), 'Vary': 'Accept-Encoding'
    };
    if (req.headers['if-none-match'] === etag) { res.writeHead(304, headers); return res.end(); }
    const canGzip = compressible.test(type) && /gzip/.test(req.headers['accept-encoding'] || '');
    if (canGzip) headers['Content-Encoding'] = 'gzip';
    res.writeHead(200, headers);
    if (req.method === 'HEAD') return res.end();
    const stream = fs.createReadStream(file);
    if (canGzip) stream.pipe(zlib.createGzip({ level: 6 })).pipe(res); else stream.pipe(res);
  });
}).listen(port, '0.0.0.0', () => console.log(`ICONIC listening on ${port}`));
