import * as THREE from './three.module.min.js';

const canvas = document.getElementById('intelligenceMap');
const stage = document.getElementById('mapStage');
const labelsRoot = document.getElementById('mapLabels');
const titleEl = document.getElementById('mapTitle');
const eyebrowEl = document.getElementById('mapEyebrow');
const descriptionEl = document.getElementById('mapDescription');
const actionEl = document.getElementById('mapAction');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const coarsePointer = matchMedia('(pointer: coarse)').matches;

if (canvas && stage && labelsRoot) {
  const nodeDefs = [
    { id:'core', label:'ICONIC', tab:'ask', eyebrow:'PERSISTENT INTELLIGENCE', title:'THE BUSINESS CORE', pos:[0,.1,.35], radius:.72, description:'One persistent layer connects what the company knows, what it watches, what it is doing, and where humans stay in control.' },
    { id:'ask', label:'ASK', tab:'ask', eyebrow:'DIRECT INTELLIGENCE', title:'ASK THE BUSINESS', pos:[-2.45,1.42,.15], radius:.42, description:'Ask a business question. The system pulls approved context, live research and procedures into one answer.' },
    { id:'intelligence', label:'INTELLIGENCE', tab:'intelligence', eyebrow:'AUTONOMOUS DISCOVERY', title:'WHAT CHANGED?', pos:[2.5,1.38,-.28], radius:.45, description:'The layer keeps watch without waiting for a prompt and surfaces changes, threats, opportunities and anomalies.' },
    { id:'work', label:'WORK', tab:'work', eyebrow:'PERSISTENT EXECUTION', title:'WHAT IS RUNNING?', pos:[2.62,-1.3,.2], radius:.43, description:'Recurring reports, monitoring jobs and investigations stay visible from active through completed or blocked.' },
    { id:'knowledge', label:'KNOWLEDGE', tab:'knowledge', eyebrow:'BUSINESS MEMORY', title:'WHAT DOES IT KNOW?', pos:[-2.55,-1.4,-.18], radius:.44, description:'Approved facts, documents, procedures, entities and provenance accumulate instead of disappearing with a chat.' },
    { id:'control', label:'CONTROL', tab:'control', eyebrow:'GOVERNANCE', title:'WHERE DOES A HUMAN DECIDE?', pos:[.06,-2.18,.6], radius:.44, description:'Policy gates make autonomy visible. Low-risk intelligence flows; consequential actions stop for explicit human judgment.' }
  ];

  let renderer = null;
  let scene = null;
  let camera = null;
  let group = null;
  let coreShell = null;
  let stars = null;
  let nodeMeshes = [];
  let edgeLines = [];
  let pulses = [];
  let labelEls = new Map();
  let selectedId = 'core';
  let pointerDown = false;
  let dragStartX = 0;
  let dragRotationStart = 0;
  let manualRotation = 0;
  let targetTiltX = 0;
  let targetTiltY = 0;
  let engaged = false;
  let inView = false;
  let contextLost = false;
  let raf = 0;
  let startTime = performance.now();
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  const colorBase = new THREE.Color(0xaeb7ff);
  const colorCore = new THREE.Color(0xf4f0e7);
  const colorSelected = new THREE.Color(0xffffff);

  function fallback(reason = '') {
    stage.classList.add('map-fallback-only');
    stage.classList.remove('three-ready');
    stage.dataset.fallbackReason = reason;
  }

  function build() {
    try {
      renderer = new THREE.WebGLRenderer({ canvas, antialias: !coarsePointer, alpha:true, powerPreference:'default' });
    } catch (error) {
      console.warn('ICONIC map WebGL unavailable; static fallback active.', error);
      fallback('renderer');
      return false;
    }
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, coarsePointer ? 1 : 1.25));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.setClearColor(0x000000,0);
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x11152d,.08);
    camera = new THREE.PerspectiveCamera(45,1,.1,100);
    camera.position.set(0,.2,coarsePointer?9.5:8.6);
    scene.add(new THREE.AmbientLight(0x9ea9ff,.8));
    const key = new THREE.PointLight(0xf4f0e7,8,18,2); key.position.set(1.5,3.2,5.2); scene.add(key);
    const blue = new THREE.PointLight(0x6674ff,10,14,2); blue.position.set(-4,-2,3); scene.add(blue);
    group = new THREE.Group(); scene.add(group);

    coreShell = new THREE.Mesh(new THREE.IcosahedronGeometry(.95,2), new THREE.MeshBasicMaterial({color:0xa8b2ff,wireframe:true,transparent:true,opacity:.22}));
    coreShell.position.set(...nodeDefs[0].pos); group.add(coreShell);

    for (const def of nodeDefs) {
      const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(def.radius, coarsePointer?18:26, coarsePointer?12:18),
        new THREE.MeshStandardMaterial({color:def.id==='core'?colorCore:colorBase,emissive:def.id==='core'?0x7c86e8:0x303765,emissiveIntensity:def.id==='core'?1.4:.7,metalness:.28,roughness:.24,transparent:true,opacity:.98})
      );
      mesh.position.set(...def.pos); mesh.userData={...def}; group.add(mesh); nodeMeshes.push(mesh);
      const label=document.createElement('button'); label.type='button'; label.className=`map-node-label ${def.id==='core'?'core-label':''}`; label.textContent=def.label; label.dataset.node=def.id;
      label.addEventListener('click',(event)=>{event.stopPropagation(); engaged=true; stage.classList.add('map-engaged'); selectNode(def.id,true);});
      labelsRoot.appendChild(label); labelEls.set(def.id,label);
    }

    const corePos=nodeMeshes[0].position;
    for(let i=1;i<nodeMeshes.length;i++){
      const target=nodeMeshes[i].position;
      const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([corePos.clone(),target.clone()]),new THREE.LineBasicMaterial({color:0x7f8cff,transparent:true,opacity:.22}));
      line.userData.nodeId=nodeMeshes[i].userData.id; group.add(line); edgeLines.push(line);
      const pulse=new THREE.Mesh(new THREE.SphereGeometry(.055,10,7),new THREE.MeshBasicMaterial({color:0xf2efff,transparent:true,opacity:.9}));
      pulse.userData={from:corePos.clone(),to:target.clone(),phase:i/nodeMeshes.length,speed:.07+i*.008}; group.add(pulse); pulses.push(pulse);
    }

    const count=coarsePointer?55:100, positions=new Float32Array(count*3);
    for(let i=0;i<count;i++){ positions[i*3]=(Math.random()-.5)*12; positions[i*3+1]=(Math.random()-.5)*8; positions[i*3+2]=-1.5-Math.random()*6; }
    const starGeo=new THREE.BufferGeometry(); starGeo.setAttribute('position',new THREE.BufferAttribute(positions,3));
    stars=new THREE.Points(starGeo,new THREE.PointsMaterial({color:0x9fa9ff,size:.03,transparent:true,opacity:.3})); scene.add(stars);

    canvas.addEventListener('webglcontextlost',(event)=>{ event.preventDefault(); contextLost=true; cancelAnimationFrame(raf); raf=0; fallback('context-lost'); });
    canvas.addEventListener('webglcontextrestored',()=>{ contextLost=false; stage.classList.remove('map-fallback-only'); stage.classList.add('three-ready'); resize(); renderOnce(); startLoop(); });
    canvas.addEventListener('pointerdown',onPointerDown);
    canvas.addEventListener('pointermove',onPointerMove);
    canvas.addEventListener('pointerup',onPointerUp);
    canvas.addEventListener('pointerleave',()=>{pointerDown=false;});

    new ResizeObserver(()=>{ resize(); renderOnce(); }).observe(stage);
    new IntersectionObserver(([entry])=>{ inView=entry.isIntersecting; if(inView) startLoop(); else stopLoop(); },{threshold:.08,rootMargin:'120px 0px'}).observe(stage);
    document.addEventListener('visibilitychange',()=>{ if(document.hidden) stopLoop(); else if(inView) startLoop(); });
    actionEl?.addEventListener('click',()=>window.__ICONIC_OPEN_DASHBOARD_TAB__?.(actionEl.dataset.tab||'ask'));

    resize(); selectNode('core',false); stage.classList.add('three-ready'); renderOnce();
    window.__ICONIC_MAP_RENDERER__=renderer;
    window.__ICONIC_FORCE_MAP_CONTEXT_LOSS__=()=>renderer.getContext().getExtension('WEBGL_lose_context')?.loseContext();
    window.__ICONIC_RESTORE_MAP_CONTEXT__=()=>renderer.getContext().getExtension('WEBGL_lose_context')?.restoreContext();
    return true;
  }

  function selectNode(id, switchDashboard=false){
    const def=nodeDefs.find(n=>n.id===id)||nodeDefs[0]; selectedId=def.id;
    if(eyebrowEl) eyebrowEl.textContent=def.eyebrow;
    if(titleEl) titleEl.textContent=def.title;
    if(descriptionEl) descriptionEl.textContent=def.description;
    if(actionEl){actionEl.dataset.tab=def.tab; actionEl.textContent=def.id==='core'?'OPEN IN DASHBOARD ↗':`OPEN ${def.label} ↗`;}
    nodeMeshes.forEach(mesh=>{const selected=mesh.userData.id===def.id; mesh.material.color.copy(selected?colorSelected:(mesh.userData.id==='core'?colorCore:colorBase)); mesh.material.emissiveIntensity=selected?1.8:(mesh.userData.id==='core'?1.3:.7); labelEls.get(mesh.userData.id)?.classList.toggle('active',selected);});
    edgeLines.forEach(line=>line.material.opacity=line.userData.nodeId===def.id||def.id==='core'?.48:.12);
    if(switchDashboard) window.__ICONIC_OPEN_DASHBOARD_TAB__?.(def.tab);
    renderOnce();
  }
  function updatePointer(event){const rect=canvas.getBoundingClientRect(); pointer.x=((event.clientX-rect.left)/rect.width)*2-1; pointer.y=-((event.clientY-rect.top)/rect.height)*2+1; if(!pointerDown){targetTiltY=pointer.x*.16;targetTiltX=pointer.y*.08;}}
  function onPointerDown(event){pointerDown=true;dragStartX=event.clientX;dragRotationStart=manualRotation;canvas.setPointerCapture?.(event.pointerId);updatePointer(event);}
  function onPointerMove(event){updatePointer(event);if(pointerDown)manualRotation=dragRotationStart+(event.clientX-dragStartX)*.006;}
  function onPointerUp(event){updatePointer(event);const moved=Math.abs(event.clientX-dragStartX);pointerDown=false;if(moved<8){raycaster.setFromCamera(pointer,camera);const hit=raycaster.intersectObjects(nodeMeshes,false)[0];if(hit){engaged=true;stage.classList.add('map-engaged');selectNode(hit.object.userData.id,true);}}}
  function resize(){if(!renderer||!camera)return;const rect=stage.getBoundingClientRect();const w=Math.max(1,Math.round(rect.width)),h=Math.max(1,Math.round(rect.height));renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();camera.position.z=w<520?10.2:w<760?9.4:8.6;}
  function positionLabels(){if(!camera)return;const rect=stage.getBoundingClientRect();for(const mesh of nodeMeshes){const world=new THREE.Vector3();mesh.getWorldPosition(world);world.project(camera);const x=(world.x*.5+.5)*rect.width,y=(-world.y*.5+.5)*rect.height,label=labelEls.get(mesh.userData.id);if(label){label.style.transform=`translate(-50%, -50%) translate(${x}px, ${y}px)`;label.style.opacity=world.z>1?'0':'1';}}}
  function animate(t){
    const sec=(t-startTime)/1000;
    if(!pointerDown&&!reducedMotion)manualRotation+=.0006;
    group.rotation.y+=((manualRotation+targetTiltY)-group.rotation.y)*.04;group.rotation.x+=(targetTiltX-group.rotation.x)*.04;
    coreShell.rotation.x=sec*.12;coreShell.rotation.y=-sec*.16;if(stars&&!reducedMotion)stars.rotation.y=-sec*.004;
    nodeMeshes.forEach((mesh,index)=>{let target=1;if(!reducedMotion){if(!engaged&&index>0){const focus=Math.floor(sec/1.15)%(nodeMeshes.length-1)+1;target=index===focus?1.11:1+Math.sin(sec*1.2+index)*.012;}else if(mesh.userData.id===selectedId)target=1.09+Math.sin(sec*3.1)*.035;}mesh.scale.lerp(new THREE.Vector3(target,target,target),.08);});
    pulses.forEach(pulse=>{const d=pulse.userData,alpha=reducedMotion?d.phase:(d.phase+sec*d.speed)%1;pulse.position.lerpVectors(d.from,d.to,alpha);pulse.material.opacity=.25+Math.sin(alpha*Math.PI)*.7;});
  }
  function renderOnce(){if(!renderer||contextLost)return;animate(performance.now());renderer.render(scene,camera);positionLabels();}
  function loop(t){raf=0;if(!inView||document.hidden||contextLost)return;animate(t);renderer.render(scene,camera);positionLabels();raf=requestAnimationFrame(loop);}
  function startLoop(){if(!renderer||raf||contextLost||document.hidden||!inView)return;if(reducedMotion){renderOnce();return;}raf=requestAnimationFrame(loop);}
  function stopLoop(){if(raf){cancelAnimationFrame(raf);raf=0;}}

  build();
}
