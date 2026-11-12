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
   const pass=data.offer_id==='reserve-pass';
   const automated=pass||data.offer_id==='selection-test';
   $('order-status').textContent=data.status==='DELIVERED'?(pass?'Your Reserve is ready':'Report delivered')
    :pass?'Paid; your private Reserve is being created (usually a few minutes). This page checks again every 15 seconds.'
    :automated?'Paid; your test is running (usually under 30 minutes). This page checks again every 30 seconds.':'Paid; awaiting human review';
   $('token').textContent=token;
   if(data.report){
    $('report-wrap').hidden=false;
    const r=data.report;
    if(pass){
     $('report-title').textContent=r.renewed?'Your Reserve was renewed':'Your Reserve keys';
     $('report').textContent=(r.renewed
      ?['Reserve ID:    '+r.reserve_id,'Now valid to:  '+r.expires_at,'','30 days were added. Your keys are unchanged.']
      :['Reserve ID:    '+r.reserve_id,'Reserve key:   '+r.reserve_key,'Reviewer key:  '+r.reviewer_key,'Valid to:      '+r.expires_at,'',
        'SAVE THESE NOW. Anyone holding the Reserve key can read and write this Reserve.','',
        '1. Add this MCP server to Claude, Claude Code, Cursor or another client (no sign-in):',
        '   '+r.mcp_endpoint,
        '2. Tell your agent:',
        '   "Use ICONIC Reserve. My reserve_key is '+r.reserve_key+'. Call reserve_pass_status, then remember what we decide and record what happens."',
        '3. Give the reviewer key only to whoever checks results.','',
        'Setup steps for each client: https://iconic.onl/agents/reserve/#quickstart',
        'To add 30 days later, buy again and enter the Reserve ID.']).join('\n');
    }else $('report').textContent=r.report_markdown||JSON.stringify(r,null,2);
   }
   else if(automated)setTimeout(check,pass?15000:30000);
  }catch{$('state').textContent='We could not verify this receipt right now. Keep your Stripe receipt and contact patrick@iconic.onl for assistance.'}
 }
 $('copy-token').addEventListener('click',async()=>{
  if(!token)return;
  try{await navigator.clipboard.writeText(token);$('copy-token').textContent='Copied'}catch{$('copy-token').textContent='Select and copy the token above'}
 });
 check();
})();
