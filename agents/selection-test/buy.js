/* Selection Test purchase: Stripe hosts the card form; the server revalidates price and inputs. */
(()=>{
 'use strict';
 const API='https://patrick-beastmaster.tailf32530.ts.net/mpp-catalog';
 const $=id=>document.getElementById(id);
 const go=$('go'),msg=$('msg');let busy=false;
 fetch(API+'/healthz',{cache:'no-store'}).then(r=>r.ok?r.json():Promise.reject()).then(s=>{
  const ok=s.hosted_checkout_ready===true;go.disabled=!ok;go.textContent=ok?'Pay $49 with Stripe':'Card checkout coming online';
 }).catch(()=>{go.disabled=true;go.textContent='Card checkout temporarily unavailable'});
 $('buy-form').addEventListener('submit',async e=>{
  e.preventDefault();if(busy)return;
  const url=$('server').value.trim();
  if(!/^https:\/\/[^\s/]+\.[^\s/]+/.test(url)){msg.textContent='Enter the public https address of your MCP server.';return}
  busy=true;go.disabled=true;msg.textContent='Opening secure Stripe checkout…';
  try{
   const res=await fetch(API+'/checkout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
    offer_id:'selection-test',offer_version:'0.1.0',buyer_authorized:true,nonconfidential_only:true,
    idempotency_key:'human-'+crypto.randomUUID(),server_url:url,contact_email:$('email').value.trim()})});
   const data=await res.json();
   if(!res.ok)throw Error(data.error==='PUBLIC_HTTPS_SERVER_URL_REQUIRED'?'That address must be a public https URL.':
     data.error==='STRIPE_CHECKOUT_UNAVAILABLE'?'Stripe checkout is temporarily unavailable. No payment was made.':
     (data.error||'Checkout was not started. No payment was made.'));
   if(typeof data.checkout_url!=='string'||!data.checkout_url.startsWith('https://checkout.stripe.com/'))throw Error('Invalid checkout destination.');
   location.assign(data.checkout_url);
  }catch(err){msg.textContent=String(err.message);busy=false;go.disabled=false}
 });
})();
