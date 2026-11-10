/* One purchase screen for humans. Agent buyers use the existing MCP/SPT flow.
 * All prices and payment authorizations are revalidated on the server.
 * Stripe hosts the card form; no payment data touches this page.
 */
(()=>{
 'use strict';
 const API='https://patrick-beastmaster.tailf32530.ts.net/mpp-catalog';
 const $=id=>document.getElementById(id);
 const dialog=$('purchase-dialog'),form=$('purchase-form'),message=$('purchase-msg');
 const submit=$('purchase-submit');
 let chosen=null,waiting=false;
 const products=[...document.querySelectorAll('.product')];
 const buttons=[];
 const names=new Map(products.map(card=>[
  card.querySelector('code')?.textContent.trim(),
  {name:card.querySelector('h3')?.textContent.trim()||'ICONIC service',price:card.querySelector('strong')?.textContent.trim()||''}
 ]));
 for(const card of products){
  const id=card.querySelector('code')?.textContent.trim();
  if(!id)continue;
  const button=document.createElement('button');
  button.type='button';button.className='buy-action';button.disabled=true;
  button.textContent='Checking checkout…';
  button.addEventListener('click',()=>{
   if(waiting)return;chosen=id;form.reset();message.textContent='';
   $('purchase-product').textContent=names.get(id).name+' · '+names.get(id).price;
   $('dataset-inputs').hidden=id!=='dataset-diff-report';
   $('before-rows').required=id==='dataset-diff-report';
   $('after-rows').required=id==='dataset-diff-report';
   dialog.showModal();$('buyer-email').focus();
  });
  card.append(button);buttons.push(button);
 }
 $('purchase-cancel').addEventListener('click',()=>{if(!waiting)dialog.close()});
 dialog.addEventListener('cancel',e=>{if(waiting)e.preventDefault()});
 const moneyReady=async()=>{
  try{
   const response=await fetch(API+'/healthz',{cache:'no-store'});
   if(!response.ok)throw Error('checkout offline');
   const state=await response.json();
   const ready=state.hosted_checkout_ready===true;
   for(const button of buttons){button.disabled=!ready;button.textContent=ready?'Buy securely with Stripe':'Card checkout coming online'}
  }catch{
   for(const button of buttons){button.disabled=true;button.textContent='Card checkout temporarily unavailable'}
  }
 };
 // An offer deep link may open a *blank* checkout form, never submit payment.
 // Server validates the price and human spending authorization after submission.
 moneyReady().then(()=>{
  const id=new URLSearchParams(location.search).get('offer');
  if(!id)return;
  const card=products.find(c=>c.querySelector('code')?.textContent.trim()===id);
  const button=card?.querySelector('.buy-action');
  if(button&&!button.disabled)button.click();
 });
 if(new URLSearchParams(location.search).has('cancelled')){
  const note=document.createElement('p');note.className='note';
  note.textContent='Checkout was cancelled or left unfinished. No purchase is confirmed on this page.';
  document.querySelector('.hero .actions')?.after(note);
 }
 form.addEventListener('submit',async e=>{
  e.preventDefault();if(waiting||!chosen)return;
  const inputs={
   offer_id:chosen,offer_version:'0.1.0',buyer_authorized:true,
   nonconfidential_only:true,idempotency_key:'human-'+crypto.randomUUID(),
   contact_email:$('buyer-email').value.trim(),
   scope_summary:$('buyer-scope').value.trim()
  };
  if(chosen==='dataset-diff-report'){
   try{
    const before=JSON.parse($('before-rows').value),after=JSON.parse($('after-rows').value);
    if(!Array.isArray(before)||!Array.isArray(after))throw Error('Both datasets must be JSON arrays.');
    inputs.join_key=$('join-key').value.trim();
    inputs.datasets={before,after};
   }catch(err){message.textContent='Check the two JSON arrays: '+err.message;return}
  }
  waiting=true;submit.disabled=true;$('purchase-cancel').disabled=true;message.textContent='Opening secure Stripe checkout…';
  try{
   const res=await fetch(API+'/checkout',{
    method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(inputs)
   });
   const data=await res.json();
   if(!res.ok)throw Error(data.error==='STRIPE_CHECKOUT_UNAVAILABLE'
    ?'Stripe checkout is temporarily unavailable. No payment was made.'
    :data.error||'Checkout was not started. No payment was made.');
   if(typeof data.checkout_url!=='string'||!data.checkout_url.startsWith('https://checkout.stripe.com/'))
    throw Error('Invalid secure checkout destination.');
   location.assign(data.checkout_url);
  }catch(err){message.textContent=String(err.message||'Unable to open checkout.');waiting=false;submit.disabled=false;$('purchase-cancel').disabled=false}
 });
})();
