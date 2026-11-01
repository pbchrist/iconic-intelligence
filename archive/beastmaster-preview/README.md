# ICONIC. — Managed Intelligence Concept Site

Static HTML/CSS/JS concept for ICONIC.'s managed business intelligence offer.

## Run locally

From this folder:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Files

- `index.html` — page structure and copy
- `styles.css` — full responsive visual system
- `app.js` — dashboard demo, model matrix, experiment lab, 2D offline fallback
- `three-scene.js` — progressive Three.js scene loaded from a pinned CDN version
- `favicon.svg` — brand mark derived from the business-card geometry

## Notes

The dashboard is a front-end demo. It is intentionally not connected to client data or production systems yet.
The model matrix is explicitly illustrative, not benchmark data.
For production, wire the demo dashboard to authenticated APIs and replace synthetic data with approved client sources.
