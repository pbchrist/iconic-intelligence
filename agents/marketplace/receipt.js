(()=>{
 'use strict';
 const $=id=>document.getElementById(id);
 const parameters=new URLSearchParams(location.search);
 const session=parameters.get('session_id')||history.state?.checkoutSessionId;
 // Remove the bearer session ID from the URL, preserve it only in this tab's history state
 // so refreshing the receipt page works after Stripe's asynchronous confirmation.
 history.replaceState(session?{checkoutSessionId:session}:null,'',location.pathname);
 if(!/^cs_(?:test_)?[A-Za-z0-9_]{12,200}$/.test(session||'')){
  $('state').textContent='No Stripe payment session was provided. Check your Stripe receipt email or contact support.';
  return;
 }
 const url='https://patrick-beastmaster.tailf32530.ts.net/mpp-catalog/checkout/receipt/'+encodeURIComponent(session);
 let token='';
 async function check(){
  try{
   const response=await fetch(url,{cache:'no-store',referrerPolicy:'no-referrer'});
   const data=await response.json();
   if(response.status===202){
    $('state').textContent='Stripe has not confirmed this payment. If you just paid, wait briefly and refresh this page from your checkout link, or contact support.';
    return;
   }
   if(!response.ok||!data.order_access_token)throw Error('Payment or receipt could not be verified.');
   token=data.order_access_token;
   $('state').textContent='Payment confirmed. Your receipt is ready.';
   $('result').hidden=false;
   $('order-id').textContent=data.order_id;
   $('service').textContent=data.offer_id;
   $('price').textContent=new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(data.price_cents/100);
   $('order-status').textContent=data.status==='DELIVERED'?'Report delivered':'Paid; awaiting human review';
   $('token').textContent=token;
   if(data.report){$('report-wrap').hidden=false;$('report').textContent=JSON.stringify(data.report,null,2)}
  }catch{$('state').textContent='We could not verify this receipt right now. Keep your Stripe receipt and contact patrick@iconic.onl for assistance.'}
 }
 $('copy-token').addEventListener('click',async()=>{
  if(!token)return;
  try{await navigator.clipboard.writeText(token);$('copy-token').textContent='Copied'}catch{$('copy-token').textContent='Select and copy the token above'}
 });
 check();
})();
