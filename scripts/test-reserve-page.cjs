// Real-browser test of /agents/reserve/ against the LIVE public Reserve gateway.
// Run from an external network (GitHub-hosted runner). Fictional inputs only.
// Usage: node scripts/test-reserve-page.cjs http://localhost:3000/agents/reserve/
const { chromium } = require('playwright');
(async () => {

const url = process.argv[2] || 'http://localhost:3000/agents/reserve/';
const results = [];
const check = (name, ok, detail = '') => { results.push({ name, ok, detail }); console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${detail ? ' :: ' + detail : ''}`); };

const browser = await chromium.launch();
for (const [label, viewport] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844 }]]) {
  const page = await browser.newPage({ viewport });
  const pageErrors = [];
  page.on('pageerror', (e) => pageErrors.push(e.message));
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForFunction(() => document.querySelector('#statusPill')?.dataset.state !== 'wait', null, { timeout: 20000 }).catch(() => {});
  const state = await page.getAttribute('#statusPill', 'data-state');
  check(`${label}: live server status`, state === 'ok', `state=${state}`);
  const meta = await page.textContent('#toolMeta');
  check(`${label}: tool list loaded live`, /LIVE FROM SERVER/.test(meta) && /16 tools/.test(meta), meta.trim().slice(0, 90));
  const endpoint = (await page.textContent('#mcpUrl')).trim();
  check(`${label}: displayed endpoint`, endpoint === 'https://patrick-beastmaster.tailf32530.ts.net/reserve/mcp', endpoint);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  check(`${label}: no horizontal overflow`, overflow <= 0, `overflow=${overflow}`);

  await page.click('[data-example="dealer"]');
  await page.click('#assessBtn');
  await page.waitForSelector('#assessOut .rv-out, #assessOut .rv-error', { timeout: 20000 });
  const verdict = await page.textContent('#assessOut .rv-verdict, #assessOut .rv-error');
  const tx = await page.textContent('#assessOut .rv-meta').catch(() => '');
  check(`${label}: free assessment from live API`, /FULFILLED_FREE/.test(tx) && /free_/.test(tx), verdict.trim().slice(0, 90));

  await page.click('#tab-demo');
  await page.click('#demoBtn');
  await page.waitForSelector('#demoOut .rv-out, #demoOut .rv-error', { timeout: 20000 });
  const demo = await page.textContent('#demoOut');
  check(`${label}: synthetic demo from live API, labeled synthetic`, /SYNTHETIC · FICTIONAL DATA/.test(demo) && /EPHEMERAL_SYNTHETIC_NO_CUSTOMER_DATA/.test(demo), demo.trim().slice(0, 90));

  // Keyboard: tabs move with arrow keys.
  await page.focus('#tab-claude');
  await page.keyboard.press('ArrowRight');
  const sel = await page.getAttribute('#tab-code', 'aria-selected');
  check(`${label}: keyboard tab navigation`, sel === 'true');
  check(`${label}: no page errors`, pageErrors.length === 0, pageErrors.join(' | '));
  await page.screenshot({ path: `reserve-${label}.png`, fullPage: true });
  await page.close();
}
await browser.close();
const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
process.exit(failed.length ? 1 : 0);
})();
