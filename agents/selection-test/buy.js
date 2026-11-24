/* Compatibility for cached older Selection Test HTML: submit a native form navigation,
   never fetch the private Tailscale address from browser JavaScript. */
(()=>{
 'use strict';
 const form=document.getElementById('buy-form');
 if(!form)return;
 const go=document.getElementById('go');
 form.method='post';
 form.action='https://patrick-beastmaster.tailf32530.ts.net/mpp-catalog/checkout/form';
 form.enctype='application/x-www-form-urlencoded';
 for(const id of ['server','email']){
  const input=document.getElementById(id);if(input)input.name=id;
 }
 const consent=document.getElementById('consent');
 if(consent){consent.name='consent';consent.value='yes';}
 if(go){go.disabled=false;go.textContent='Pay $49 with Stripe';}
})();
