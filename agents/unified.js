/* One-page Reserve free synthetic assessment and endpoint copy. No customer data is submitted. */
(() => {
  'use strict';
  const endpoint='https://patrick-beastmaster.tailf32530.ts.net/reserve';
  const demo=document.getElementById('unified-demo-btn');
  const status=document.getElementById('unified-demo-status');
  const result=document.getElementById('unified-demo-result');
  if (demo && status && result) demo.addEventListener('click', async () => {
    if (demo.disabled) return;
    demo.disabled=true;
    status.textContent='Running the free synthetic assessment on ICONIC Reserve…';
    result.hidden=true;
    result.textContent='';
    const controller=new AbortController();
    const timeout=setTimeout(()=>controller.abort(),15000);
    const fictional={
      business_type:'Fictional independent accounting firm, 14 employees',
      systems:['Fictional billing ledger','Example planning notes'],
      problem:'In this fictional example, associates repeat tax-planning research because past decisions and outcomes are not linked.',
      recurring_workflow:'Quarterly fictional planning review',
      measurable_outcome:'Estimated hours saved per fictional engagement',
      existing_memory:false,
      sensitive_data:false
    };
    try {
      const response=await fetch(endpoint+'/agents/evaluate',{
        method:'POST',mode:'cors',credentials:'omit',cache:'no-store',
        headers:{'Content-Type':'application/json'},body:JSON.stringify(fictional),signal:controller.signal
      });
      if(!response.ok) throw new Error('Reserve returned HTTP '+response.status);
      const data=await response.json();
      if(!data || !data.fit_status) throw new Error('Unexpected response from Reserve');
      const human=data.brief_for_human||{};
      const first=data.recommended_first_pilot||{};
      const lines=[
        'FIT ASSESSMENT: '+data.fit_status,
        human.headline||'',
        'NEXT STEP: '+(human.recommended_action||data.suggested_next_step||'See the full report'),
        first.workflow?'FIRST PILOT: '+first.workflow:'',
        first.outcome_metric?'MEASURE: '+first.outcome_metric:'',
        '',
        'This result is for fictional data only. No payment was initiated.'
      ];
      status.textContent='Live Reserve assessment completed.';
      result.textContent=lines.filter(Boolean).join('\n');
      result.hidden=false;
    } catch(error) {
      status.textContent='Reserve assessment unavailable: '+(error.name==='AbortError'?'request timed out':(error.message||'connection error'))+'. No payment was made.';
    } finally {clearTimeout(timeout);demo.disabled=false;}
  });
  document.querySelectorAll('.unified-copy[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const old=button.textContent;
      try {await navigator.clipboard.writeText(button.dataset.copy);button.textContent='COPIED';}
      catch {button.textContent='SELECT ENDPOINT ABOVE TO COPY';}
      setTimeout(()=>{button.textContent=old;},2000);
    });
  });
})();
