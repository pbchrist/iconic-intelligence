/* Reserve Pass purchase. Stripe hosts the card form; the server revalidates price and inputs.
 * The button only becomes a buy button when the live catalog says the pass is purchasable. */
(() => {
  'use strict';
  const API = 'https://patrick-beastmaster.tailf32530.ts.net/mpp-catalog';
  const $ = (id) => document.getElementById(id);
  const form = $('passForm'), go = $('passGo'), msg = $('passMsg');
  if (!form || !go) return;
  let busy = false;
  const json = (url) => fetch(url, { cache: 'no-store' }).then((r) => (r.ok ? r.json() : Promise.reject(new Error('offline'))));
  // The checkout server's health check is readable from this site; the offer itself is read from this site's own catalog copy.
  // The server checks the offer and the price again before any payment starts.
  Promise.all([json(API + '/healthz'), json('/agents/marketplace/offers.json')]).then(([health, catalog]) => {
    const offer = (catalog.offers || []).find((o) => o.offer_id === 'reserve-pass') || {};
    const ready = health.hosted_checkout_ready === true && offer.purchasable === true && offer.approved_price_cents === 1900;
    go.disabled = !ready;
    go.textContent = ready ? 'PAY $19 WITH STRIPE' : 'OPENING SOON';
    if (!ready) msg.textContent = 'Checkout for the Reserve Pass is not open yet. The free sandbox above works now.';
  }).catch(() => {
    go.disabled = true; go.textContent = 'OPENING SOON';
    msg.textContent = 'Checkout for the Reserve Pass is not reachable right now. Nothing was charged.';
  });
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (busy) return;
    const email = $('passEmail').value.trim(), renew = $('passRenew').value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { msg.textContent = 'Enter the email for your receipt.'; $('passEmail').focus(); return; }
    if (renew && !/^rp_[0-9a-f]{16}$/.test(renew)) { msg.textContent = 'A Reserve ID looks like rp_ followed by 16 characters. Leave it empty for a new Reserve.'; $('passRenew').focus(); return; }
    if (!$('passConsent').checked) { msg.textContent = 'Tick the box to authorize the $19 purchase.'; return; }
    busy = true; go.disabled = true; msg.textContent = 'Opening secure Stripe checkout…';
    try {
      const body = { offer_id: 'reserve-pass', offer_version: '0.1.0', buyer_authorized: true, nonconfidential_only: true,
        idempotency_key: 'human-' + crypto.randomUUID(), contact_email: email };
      if (renew) body.reserve_id = renew;
      const res = await fetch(API + '/checkout', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error === 'INVALID_RESERVE_ID' ? 'That Reserve ID is not valid.'
        : data.error === 'STRIPE_CHECKOUT_UNAVAILABLE' ? 'Stripe checkout is temporarily unavailable. No payment was made.'
        : 'Checkout was not started. No payment was made.');
      if (typeof data.checkout_url !== 'string' || !data.checkout_url.startsWith('https://checkout.stripe.com/')) throw new Error('Invalid checkout destination. No payment was made.');
      location.assign(data.checkout_url);
    } catch (err) { msg.textContent = String(err.message || 'Unable to open checkout.'); busy = false; go.disabled = false; }
  });
})();
