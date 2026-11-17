/* Outcome-first AI curriculum navigator. No network requests, accounts or analytics.
   The public inventory is rendered server-side in HTML so 439 skills remain browseable. */
(() => {
  'use strict';
  const storyView=document.getElementById('path-story-view');
  const inventoryView=document.getElementById('inventory');
  if(!storyView||!inventoryView)return;
  const stage=document.getElementById('path-stage');
  const trailEl=document.getElementById('path-trail');
  const countEl=document.getElementById('path-step-count');
  const back=document.getElementById('path-back');
  const restart=document.getElementById('path-restart');
  const buttons=[...document.querySelectorAll('[data-path-view]')];
  const inventorySearch=document.getElementById('inventory-search');
  const inventoryModule=document.getElementById('inventory-module');
  const inventoryLevel=document.getElementById('inventory-level');
  const skillSections=[...document.querySelectorAll('.inventory-module')];
  const names={"1":"AI literacy and mental models","2":"Prompting and context engineering","3":"Everyday AI work","4":"Research / sources / verification","5":"Model ecosystem / selection / routing","6":"Agent architecture and behavior","7":"Hermes agent operations","8":"Persistent memory across models and agents","9":"RAG / document intelligence / knowledge graphs","10":"Local model acquisition / inference","11":"GPUs / CUDA / Linux server administration","12":"Private networking / remote endpoints / operations","13":"APIs / MCP / tools / discovery","14":"Browser automation / computer use","15":"Cross-app workflows / scheduling","16":"AI-assisted coding / GitHub / CI-CD","17":"Evaluations / benchmarking / observability","18":"Security / privacy / data handling","19":"Building AI-facing web products","20":"AEO / crawler access / machine discovery","21":"Payments / agent-native transactions","22":"Spreadsheets / data reconciliation / analytics","23":"Dealership / pricing / CRM intelligence","24":"OSINT / research / lead sourcing","25":"Outreach / content / social systems","26":"Writing / editorial systems / narrative consistency","27":"AI discovery / evaluations / training delivery","28":"Voice / transcripts / content intake","29":"Experimental / complex system design"};
  const escapeHTML=str=>String(str).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const questions={
    start:{title:"What do you want AI to do?",detail:"Choose what you need. We'll figure out the next move together.",choices:[
      ["I don't know where to start","I know AI could help, but I need clarity.","clarity"],
      ["I want my own private AI","Something I run and control.","private"],
      ["I already use AI, but want better results","Smarter answers, better speed or useful memory.","improve"],
      ["I want AI to handle work for me","Documents, apps, agents or browser tasks.","delegate"],
      ["I want to build something","Connect tools or create a working system.","build"]
    ]},
    clarity:{title:"What's the biggest frustration?",detail:"Pick the problem that comes up most often.",choices:[
       ["I don't know which AI tasks are worth trying","Show me a practical starting point.","find-opportunity"],
      ["My staff already use AI","Set rules so nothing confidential leaks.","staff-rules"],
      ["I keep doing the same work by hand","I want to reclaim that time.","reduce-repetition"],
      ["I need better research or decisions","I want information I can trust.","better-research"]
    ]},
    private:{title:"Where would you like your AI to live?",detail:"You can start with something simple. A permanent business system comes later if you need it.",choices:[
      ["On my laptop or desktop","I want to try a private model myself.","local-quickstart"],
      ["On a computer serving my business","I want shared access and dependable uptime.","local-business"],
      ["I don't know what hardware I need","Help me choose before buying anything.","hardware-choice"]
    ]},
    improve:{title:"What's wrong with the AI you've tried?",detail:"Speed and intelligence aren't the same thing. Let's find the actual bottleneck.",choices:[
      ["It makes mistakes or can't reason through the job","I need to measure answer quality.","quality-benchmark"],
      ["It's too slow or costs too much","I need a useful speed–quality tradeoff.","speed-benchmark"],
      ["It forgets everything or misses my files","I want it to work with information it can retrieve.","knowledge-memory"]
    ]},
    delegate:{title:"What kind of work should it handle?",detail:"Choose the work, then we can choose the right level of automation.",choices:[
      ["Read, search and work with documents","Research, summaries and data from my files.","document-work"],
      ["Move work between my apps","Turn a recurring process into a workflow.","app-work"],
      ["Use websites or act as an agent","Bounded computer use, tools and oversight.","browser-work"]
    ]},
    build:{title:"What are you trying to make?",detail:"Start with the outcome. We can fill in the technology afterwards.",choices:[
      ["Connect AI to software I already use","APIs, tools, MCP and GitHub.","connected-tool"],
      ["Build a site, demo or something people can use","A real application with testing and deployment.","web-product"],
      ["Operate several models and agents together","Architecture, security, networking and reliability.","system-design"]
    ]}
  };
  const outcomes={
    "find-opportunity":{title:"Find your first useful AI job.",detail:"Begin with the business problem, privacy boundaries, and a small task you can test in a day.",lab:"Pick three tasks from your week, rank them by value and risk, and test the best one.",modules:[27,1,3]},
    "staff-rules":{title:"Set rules so nothing confidential leaks.",detail:"Find out which AI tools your people already use, what goes into them, and where client information could end up.",lab:"List the tools your staff use, sort your information into what may and may not go into them, and write a one-page policy your team can follow.",modules:[18,3,1]},
    "reduce-repetition":{title:"Make one repetitive task disappear.",detail:"Identify what repeats, what information it needs and which steps should stay under your control.",lab:"Map one weekly task and create a repeatable first version with a check at the end.",modules:[3,15,22]},
    "better-research":{title:"Get answers you can actually check.",detail:"Research with sources, reconcile conflicting information, and separate evidence from guesses.",lab:"Produce a short source-backed brief with a verification checklist.",modules:[4,22,27]},
    "local-quickstart":{title:"Run private AI on your own computer.",detail:"A basic local-model install can be introductory. You don't need to master Linux or CUDA just to get started.",lab:"Choose a compatible model, open a local chat interface, and test it on a real task.",modules:[10,18,1]},
    "local-business":{title:"Plan private AI for a real business.",detail:"Start with a working private model, then define who needs access, what stays private and how the system should recover.",lab:"Run a model locally and sketch its user access, data boundaries, and reliability requirements.",modules:[10,12,18]},
    "hardware-choice":{title:"Find the smallest machine that will do the job.",detail:"Don't start with a GPU shopping list. Work backward from your tasks, model requirements and budget.",lab:"Compare two hardware/model pairings for memory, speed and answer quality before purchasing.",modules:[5,10,11]},
    "quality-benchmark":{title:"Test how smart your AI needs to be.",detail:"Benchmark models on your real questions. Measure correctness, reasoning, consistency and errors instead of trusting a ranking.",lab:"Make a 10-task evaluation set and score two models against the same criteria.",modules:[5,17,10]},
    "speed-benchmark":{title:"Find the sweet spot between speed and intelligence.",detail:"Compare time to first answer, generated tokens per second, reasoning quality and the cost of fixing bad answers.",lab:"Run the same tasks on two configurations and compare usefulness per minute, not just token speed.",modules:[5,17,10]},
    "knowledge-memory":{title:"Give AI the context it keeps losing.",detail:"Connect documents, retrieval and persistent memory while controlling which information may leave your system.",lab:"Load a small document set, ask verifiable questions, then test what carries across sessions.",modules:[8,9,18]},
    "document-work":{title:"Let AI work with your documents.",detail:"Turn source files into reliable research, comparisons and summaries with citations or spot checks.",lab:"Ask a collection of files five questions and verify each answer against the source.",modules:[4,9,22]},
    "app-work":{title:"Connect a useful workflow.",detail:"Map inputs, actions, and approval points before making agents move information between systems.",lab:"Automate one recurring intake-to-output process with a human review checkpoint.",modules:[6,15,13]},
    "browser-work":{title:"Build an agent with boundaries.",detail:"Give an agent a specific task, defined tools, stopping rules and a way to verify what it did.",lab:"Run a bounded browser task, inspect its actions and verify the final result.",modules:[7,14,18]},
    "connected-tool":{title:"Connect AI to the tools you own.",detail:"Start with an API or MCP integration, define what it can do, and test how failures are handled.",lab:"Create one callable tool, verify its schema, and connect it to a model.",modules:[13,16,17]},
    "web-product":{title:"Build a working AI application.",detail:"Start with a single use case and an honest demo, then add testing, deployment and discoverability.",lab:"Ship one usable page or tool and verify it from a separate browser.",modules:[19,16,20]},
    "system-design":{title:"Architect a dependable AI system.",detail:"Coordinate agents, private and frontier models, networking, permissions, fallbacks and measurable outcomes.",lab:"Draw the system's trust boundaries, failure paths and recovery plan before building.",modules:[29,12,11]}
  };
  const entryPoints=['clarity','private','improve','delegate','build'];
  const params=new URLSearchParams(window.location.search);
  const seed=params.get('start');
  const stack=[{id:'start',answer:''}];
  if(entryPoints.includes(seed)){
    const option=questions.start.choices.find(item=>item[2]===seed);
    stack.push({id:seed,answer:option?option[0]:''});
  }else if(seed&&outcomes[seed]){
    const parent=Object.keys(questions).find(k=>k!=='start'&&questions[k].choices.some(c=>c[2]===seed));
    if(parent){const p=questions.start.choices.find(c=>c[2]===parent);stack.push({id:parent,answer:p?p[0]:''});}
    const option=parent&&questions[parent].choices.find(c=>c[2]===seed);
    stack.push({id:seed,answer:option?option[0]:''});
  }
  const render=()=>{
    const current=stack[stack.length-1];
    const question=questions[current.id];
    const crumbs=stack.map((s,i)=>i===0?'START':s.answer).join(' / ');
    trailEl.textContent=crumbs;
    countEl.textContent=question?'PICK YOUR NEXT MOVE':'YOUR STARTING POINT';
    back.disabled=stack.length<2;
    restart.disabled=stack.length<2;
    if(question){
      stage.innerHTML='<div class="path-story-inner"><p class="path-kicker">CHOOSE YOUR NEXT MOVE</p><h3 tabindex="-1">'+escapeHTML(question.title)+'</h3><p class="path-description">'+escapeHTML(question.detail)+'</p><div class="path-choices">'+question.choices.map((choice,i)=>'<button type="button" class="path-choice" data-path-next="'+escapeHTML(choice[2])+'"><span class="path-choice-number">'+String(i+1).padStart(2,'0')+'</span><span class="path-choice-text"><strong>'+escapeHTML(choice[0])+'</strong><small>'+escapeHTML(choice[1])+'</small></span><span class="path-choice-arrow" aria-hidden="true">→</span></button>').join('')+'</div></div>';
    }else{
      const result=outcomes[current.id];
      if(!result){stack.splice(1);render();return;}
      stage.innerHTML='<div class="path-story-inner path-result"><p class="path-kicker">YOUR NEXT MOVE</p><h3 tabindex="-1">'+escapeHTML(result.title)+'</h3><p class="path-description">'+escapeHTML(result.detail)+'</p><div class="path-mission"><small>IN YOUR SESSION: we build this with you, on your own work</small><p>'+escapeHTML(result.lab)+'</p></div><p class="path-minihead">SKILLS TO EXPLORE</p><div class="path-module-links">'+result.modules.map(id=>'<button type="button" data-inventory-module="'+id+'"><span>'+String(id).padStart(2,'0')+'</span> '+escapeHTML(names[id]||'Related skills')+'</button>').join('')+'</div><div class="path-result-actions"><a class="button button-primary" href="https://buy.stripe.com/00w14o8Bj1co89GbXD8IU0a" data-offer="training-private">Book this as a private session · $1,000</a><a class="path-quiet-action" href="https://buy.stripe.com/9B65kE7xf7AMblS1iZ8IU09" data-offer="training-workshop">or join a workshop · $249</a><button type="button" class="path-quiet-action" data-path-reset>TRY ANOTHER ROUTE</button></div></div>';
    }
  };
  const setView=(mode,focusSearch=false)=>{
    const inInventory=mode==='inventory';
    storyView.hidden=inInventory;
    inventoryView.hidden=!inInventory;
    buttons.forEach(b=>{const active=b.dataset.pathView===mode;b.classList.toggle('is-active',active);b.setAttribute('aria-pressed',active?'true':'false');});
    if(inInventory&&focusSearch)inventorySearch.focus();
  };
  const filterInventory=()=>{
    const query=inventorySearch.value.trim().toLowerCase();
    const selectedModule=inventoryModule.value;
    const selectedLevel=inventoryLevel.value;
    let total=0;
    for(const group of skillSections){
      const eligible=selectedModule==='all'||group.dataset.module===selectedModule;
      const moduleMatches=(group.dataset.name||'').includes(query);
      let count=0;
      for(const item of group.querySelectorAll('.inventory-skill')){
        const ok=eligible&&(selectedLevel==='all'||item.dataset.level===selectedLevel)&&(!query||moduleMatches||item.textContent.toLowerCase().includes(query));
        item.hidden=!ok;
        if(ok)count++;
      }
      group.hidden=count===0;
      group.querySelector('.inventory-count').textContent=count+' '+(count===1?'skill':'skills');
      if(count&& (query||selectedModule!=='all'||selectedLevel!=='all'))group.open=true;
      total+=count;
    }
    document.getElementById('inventory-results').textContent='Showing '+total+' of 439 skills';
    document.getElementById('inventory-empty').hidden=total>0;
  };
  const openModule=id=>{
    inventorySearch.value='';
    inventoryLevel.value='all';
    inventoryModule.value=String(id);
    setView('inventory');
    filterInventory();
    window.location.hash='inventory';
  };
  stage.addEventListener('click',event=>{
    const option=event.target.closest('[data-path-next]');
    if(option){
      const target=option.dataset.pathNext;
      const current=questions[stack[stack.length-1].id];
      const choice=current&&current.choices.find(item=>item[2]===target);
      if(!choice||(!questions[target]&&!outcomes[target]))return;
      stack.push({id:target,answer:choice[0]});
      render();
      stage.querySelector('h3')?.focus({preventScroll:true});
      return;
    }
    const skill=event.target.closest('[data-inventory-module]');
    if(skill){openModule(skill.dataset.inventoryModule);return;}
    if(event.target.closest('[data-path-reset]')){stack.splice(1);render();stage.querySelector('h3')?.focus({preventScroll:true});}
  });
  back.addEventListener('click',()=>{if(stack.length>1){stack.pop();render();stage.querySelector('h3')?.focus({preventScroll:true});}});
  restart.addEventListener('click',()=>{stack.splice(1);render();stage.querySelector('h3')?.focus({preventScroll:true});});
  for(const button of buttons)button.addEventListener('click',()=>{
    const mode=button.dataset.pathView;
    setView(mode,mode==='inventory');
    if(mode==='inventory')filterInventory();
    window.location.hash=mode==='inventory'?'inventory':'curriculum';
  });
  inventorySearch.addEventListener('input',filterInventory);
  inventoryModule.addEventListener('change',filterInventory);
  inventoryLevel.addEventListener('change',filterInventory);
  document.getElementById('inventory-expand').addEventListener('click',()=>skillSections.filter(x=>!x.hidden).forEach(x=>x.open=true));
  document.getElementById('inventory-collapse').addEventListener('click',()=>skillSections.forEach(x=>x.open=false));
  document.querySelectorAll('[data-open-inventory]').forEach(a=>a.addEventListener('click',()=>{setView('inventory');filterInventory();}));
  window.addEventListener('hashchange',()=>{if(window.location.hash==='#inventory')setView('inventory');});
  render();
  setView(window.location.hash==='#inventory'?'inventory':'story');
  filterInventory();
})();