import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.min.js';

const canvas = document.getElementById('intelligenceMap');
const stage = document.getElementById('mapStage');
const labelsRoot = document.getElementById('mapLabels');
const titleEl = document.getElementById('mapTitle');
const eyebrowEl = document.getElementById('mapEyebrow');
const descriptionEl = document.getElementById('mapDescription');
const actionEl = document.getElementById('mapAction');

if (!canvas || !stage || !labelsRoot) {
  throw new Error('ICONIC intelligence map mount not found');
}

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const coarsePointer = window.matchMedia('(pointer: coarse)').matches;

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: !coarsePointer,
  alpha: true,
  powerPreference: 'high-performance'
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, coarsePointer ? 1.35 : 1.8));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setClearColor(0x000000, 0);

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x11152d, 0.08);

const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
camera.position.set(0, 0.2, coarsePointer ? 9.5 : 8.6);

scene.add(new THREE.AmbientLight(0x9ea9ff, 0.8));
const key = new THREE.PointLight(0xf4f0e7, 8, 18, 2);
key.position.set(1.5, 3.2, 5.2);
scene.add(key);
const blue = new THREE.PointLight(0x6674ff, 10, 14, 2);
blue.position.set(-4, -2, 3);
scene.add(blue);

const group = new THREE.Group();
scene.add(group);

const nodeDefs = [
  {
    id: 'core', label: 'ICONIC', eyebrow: 'PERSISTENT INTELLIGENCE', title: 'THE BUSINESS CORE', tab: 'ask',
    pos: [0, 0.15, 0.35], radius: 0.72,
    description: 'One persistent layer connects what the company knows, what it watches, what it is doing, and where humans stay in control.'
  },
  {
    id: 'ask', label: 'ASK', eyebrow: 'DIRECT INTELLIGENCE', title: 'ASK THE BUSINESS', tab: 'ask',
    pos: [-2.45, 1.42, 0.15], radius: 0.42,
    description: 'Ask a business question. The system pulls approved context, live research and procedures into one answer.'
  },
  {
    id: 'intelligence', label: 'INTELLIGENCE', eyebrow: 'AUTONOMOUS DISCOVERY', title: 'WHAT CHANGED?', tab: 'intelligence',
    pos: [2.5, 1.38, -0.28], radius: 0.45,
    description: 'The layer keeps watch without waiting for a prompt and surfaces changes, threats, opportunities and anomalies.'
  },
  {
    id: 'work', label: 'WORK', eyebrow: 'PERSISTENT EXECUTION', title: 'WHAT IS RUNNING?', tab: 'work',
    pos: [2.62, -1.3, 0.2], radius: 0.43,
    description: 'Recurring reports, monitoring jobs and investigations stay visible from active through completed or blocked.'
  },
  {
    id: 'knowledge', label: 'KNOWLEDGE', eyebrow: 'BUSINESS MEMORY', title: 'WHAT DOES IT KNOW?', tab: 'knowledge',
    pos: [-2.55, -1.4, -0.18], radius: 0.44,
    description: 'Approved facts, documents, procedures, entities and source provenance accumulate instead of disappearing with the chat.'
  },
  {
    id: 'control', label: 'CONTROL', eyebrow: 'GOVERNANCE', title: 'WHERE DOES A HUMAN DECIDE?', tab: 'control',
    pos: [0.06, -2.18, 0.6], radius: 0.44,
    description: 'Policy gates make autonomy visible. Low-risk intelligence flows; consequential actions stop for explicit human judgment.'
  }
];

const nodeMeshes = [];
const labelEls = new Map();
const colorBase = new THREE.Color(0xaeb7ff);
const colorCore = new THREE.Color(0xf4f0e7);
const colorSelected = new THREE.Color(0xffffff);

const coreShell = new THREE.Mesh(
  new THREE.IcosahedronGeometry(0.95, 2),
  new THREE.MeshBasicMaterial({ color: 0xa8b2ff, wireframe: true, transparent: true, opacity: 0.22 })
);
coreShell.position.set(...nodeDefs[0].pos);
group.add(coreShell);

for (const def of nodeDefs) {
  const geometry = new THREE.SphereGeometry(def.radius, coarsePointer ? 20 : 32, coarsePointer ? 14 : 22);
  const material = new THREE.MeshStandardMaterial({
    color: def.id === 'core' ? colorCore : colorBase,
    emissive: def.id === 'core' ? 0x7c86e8 : 0x303765,
    emissiveIntensity: def.id === 'core' ? 1.4 : 0.7,
    metalness: 0.28,
    roughness: 0.24,
    transparent: true,
    opacity: 0.98
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(...def.pos);
  mesh.userData = { ...def, baseRadius: def.radius };
  group.add(mesh);
  nodeMeshes.push(mesh);

  const halo = new THREE.Mesh(
    new THREE.RingGeometry(def.radius * 1.35, def.radius * 1.39, 48),
    new THREE.MeshBasicMaterial({ color: 0xaab4ff, transparent: true, opacity: def.id === 'core' ? 0.2 : 0.09, side: THREE.DoubleSide })
  );
  halo.position.copy(mesh.position);
  halo.lookAt(camera.position);
  halo.userData.follow = mesh;
  group.add(halo);

  const label = document.createElement('button');
  label.type = 'button';
  label.className = `map-node-label ${def.id === 'core' ? 'core-label' : ''}`;
  label.textContent = def.label;
  label.dataset.node = def.id;
  label.addEventListener('click', (event) => {
    event.stopPropagation();
    selectNode(def.id, false);
  });
  labelsRoot.appendChild(label);
  labelEls.set(def.id, label);
}

const lineMaterial = new THREE.LineBasicMaterial({ color: 0x7f8cff, transparent: true, opacity: 0.22 });
const edgeLines = [];
const pulses = [];
const corePos = nodeMeshes[0].position;
for (let i = 1; i < nodeMeshes.length; i++) {
  const target = nodeMeshes[i].position;
  const geometry = new THREE.BufferGeometry().setFromPoints([corePos.clone(), target.clone()]);
  const line = new THREE.Line(geometry, lineMaterial.clone());
  line.userData.nodeId = nodeMeshes[i].userData.id;
  group.add(line);
  edgeLines.push(line);

  const pulse = new THREE.Mesh(
    new THREE.SphereGeometry(0.055, 12, 8),
    new THREE.MeshBasicMaterial({ color: 0xf2efff, transparent: true, opacity: 0.9 })
  );
  pulse.userData = { from: corePos.clone(), to: target.clone(), phase: i / nodeMeshes.length, speed: 0.07 + i * 0.008 };
  group.add(pulse);
  pulses.push(pulse);
}

// Small worker nodes make the routing idea visible without becoming visual noise.
for (const [x, y, z, c] of [[-1.25, 2.35, -1.1, 0x6674ff], [1.35, 2.2, -1.4, 0xd7dbff]]) {
  const worker = new THREE.Mesh(
    new THREE.OctahedronGeometry(0.17, 0),
    new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: 0.8, metalness: 0.4, roughness: 0.25 })
  );
  worker.position.set(x, y, z);
  group.add(worker);
}

const stars = (() => {
  const count = coarsePointer ? 70 : 130;
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 12;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 8;
    positions[i * 3 + 2] = -1.5 - Math.random() * 6;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({ color: 0x9fa9ff, size: coarsePointer ? 0.025 : 0.035, transparent: true, opacity: 0.32 });
  const pts = new THREE.Points(geometry, material);
  scene.add(pts);
  return pts;
})();

let selectedId = 'core';
let pointerDown = false;
let dragStartX = 0;
let dragRotationStart = 0;
let manualRotation = 0;
let targetTiltX = 0;
let targetTiltY = 0;
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function selectNode(id, fromCanvas = true) {
  const def = nodeDefs.find((item) => item.id === id) || nodeDefs[0];
  selectedId = def.id;
  eyebrowEl.textContent = def.eyebrow;
  titleEl.textContent = def.title;
  descriptionEl.textContent = def.description;
  actionEl.dataset.tab = def.tab;
  actionEl.textContent = def.id === 'core' ? 'OPEN IN DASHBOARD ↗' : `OPEN ${def.label} ↗`;

  for (const mesh of nodeMeshes) {
    const selected = mesh.userData.id === def.id;
    mesh.material.color.copy(selected ? colorSelected : (mesh.userData.id === 'core' ? colorCore : colorBase));
    mesh.material.emissiveIntensity = selected ? 1.8 : (mesh.userData.id === 'core' ? 1.3 : 0.7);
    labelEls.get(mesh.userData.id)?.classList.toggle('active', selected);
  }
  for (const line of edgeLines) {
    line.material.opacity = line.userData.nodeId === def.id || def.id === 'core' ? 0.48 : 0.12;
  }

  if (fromCanvas && navigator.vibrate && coarsePointer) navigator.vibrate(8);
}

function updatePointer(event) {
  const rect = canvas.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  if (!pointerDown) {
    targetTiltY = pointer.x * 0.16;
    targetTiltX = pointer.y * 0.08;
  }
}

canvas.addEventListener('pointerdown', (event) => {
  pointerDown = true;
  dragStartX = event.clientX;
  dragRotationStart = manualRotation;
  canvas.setPointerCapture?.(event.pointerId);
  updatePointer(event);
});
canvas.addEventListener('pointermove', (event) => {
  updatePointer(event);
  if (pointerDown) manualRotation = dragRotationStart + (event.clientX - dragStartX) * 0.006;
});
canvas.addEventListener('pointerup', (event) => {
  updatePointer(event);
  const moved = Math.abs(event.clientX - dragStartX);
  pointerDown = false;
  if (moved < 8) {
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(nodeMeshes, false)[0];
    if (hit) selectNode(hit.object.userData.id, true);
  }
});
canvas.addEventListener('pointerleave', () => { pointerDown = false; });

function resize() {
  const rect = stage.getBoundingClientRect();
  const width = Math.max(1, Math.round(rect.width));
  const height = Math.max(1, Math.round(rect.height));
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  // Pull back slightly on narrow screens so labels never fall off the card.
  camera.position.z = width < 520 ? 10.2 : width < 760 ? 9.4 : 8.6;
}
new ResizeObserver(resize).observe(stage);
resize();

function positionLabels() {
  const rect = stage.getBoundingClientRect();
  for (const mesh of nodeMeshes) {
    const world = new THREE.Vector3();
    mesh.getWorldPosition(world);
    world.project(camera);
    const x = (world.x * 0.5 + 0.5) * rect.width;
    const y = (-world.y * 0.5 + 0.5) * rect.height;
    const label = labelEls.get(mesh.userData.id);
    if (!label) continue;
    label.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
    label.style.opacity = world.z > 1 ? '0' : '1';
  }
}

const clock = new THREE.Clock();
function frame() {
  const t = clock.getElapsedTime();
  if (!pointerDown) manualRotation += reducedMotion ? 0 : 0.0006;
  group.rotation.y += ((manualRotation + targetTiltY) - group.rotation.y) * 0.04;
  group.rotation.x += (targetTiltX - group.rotation.x) * 0.04;
  coreShell.rotation.x = t * 0.12;
  coreShell.rotation.y = -t * 0.16;
  stars.rotation.y = reducedMotion ? 0 : -t * 0.004;

  nodeMeshes.forEach((mesh, index) => {
    const selected = mesh.userData.id === selectedId;
    const pulse = selected ? 1.09 + Math.sin(t * 3.1) * 0.035 : 1 + Math.sin(t * 1.2 + index) * 0.015;
    const target = reducedMotion ? (selected ? 1.08 : 1) : pulse;
    mesh.scale.lerp(new THREE.Vector3(target, target, target), 0.08);
  });

  pulses.forEach((pulse) => {
    const d = pulse.userData;
    const alpha = reducedMotion ? d.phase : (d.phase + t * d.speed) % 1;
    pulse.position.lerpVectors(d.from, d.to, alpha);
    pulse.material.opacity = 0.25 + Math.sin(alpha * Math.PI) * 0.7;
  });

  renderer.render(scene, camera);
  positionLabels();
  requestAnimationFrame(frame);
}

selectNode('core', false);
frame();

// COMPOUNDING INTELLIGENCE — a second, lightweight scene that visibly retains gains.
const compoundCanvas = document.getElementById('compoundCanvas');
const compoundStage = document.getElementById('compoundStage');
const compoundStory = document.getElementById('compoundStory');
const compoundCount = document.getElementById('compoundCount');
const compoundStepEls = [...document.querySelectorAll('[data-compound-step]')];

if (compoundCanvas && compoundStage && compoundStory) {
  const cRenderer = new THREE.WebGLRenderer({ canvas: compoundCanvas, antialias: !coarsePointer, alpha: true, powerPreference: 'high-performance' });
  cRenderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, coarsePointer ? 1.15 : 1.55));
  cRenderer.outputColorSpace = THREE.SRGBColorSpace;
  cRenderer.setClearColor(0x000000, 0);

  const cScene = new THREE.Scene();
  cScene.fog = new THREE.FogExp2(0x0b0d1a, 0.095);
  const cCamera = new THREE.PerspectiveCamera(44, 1, 0.1, 50);
  cCamera.position.set(0, 0.15, coarsePointer ? 8.7 : 7.8);
  cScene.add(new THREE.AmbientLight(0x8793ff, 1.05));
  const cLight = new THREE.PointLight(0xf4f0e7, 10, 18, 2);
  cLight.position.set(2.2, 3.4, 5.5);
  cScene.add(cLight);

  const cGroup = new THREE.Group();
  cScene.add(cGroup);
  const cCore = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.7, 2),
    new THREE.MeshStandardMaterial({ color: 0xf1eee6, emissive: 0x6a74d8, emissiveIntensity: 1.15, metalness: 0.22, roughness: 0.28 })
  );
  cGroup.add(cCore);
  const cShell = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.0, 2),
    new THREE.MeshBasicMaterial({ color: 0xaeb7ff, wireframe: true, transparent: true, opacity: 0.18 })
  );
  cGroup.add(cShell);

  const cPositions = [
    [-2.4,1.55,.2],[2.45,1.4,-.4],[-2.65,-1.0,-.2],[2.55,-1.15,.25],
    [-1.0,2.45,-.8],[1.05,2.35,-1.0],[-1.2,-2.3,-.55],[1.2,-2.25,-.65],
    [-3.15,.15,-1.15],[3.1,.15,-1.2],[-.1,3.0,-1.55],[.1,-2.95,-1.4]
  ];
  const cNodes = [];
  const cLines = [];
  const cPulseMaterial = new THREE.MeshBasicMaterial({ color: 0xf4f0e7, transparent: true, opacity: 0.8 });
  const cPulses = [];

  cPositions.forEach((pos, i) => {
    const node = new THREE.Mesh(
      new THREE.SphereGeometry(i < 4 ? 0.24 : 0.18, coarsePointer ? 12 : 18, coarsePointer ? 9 : 14),
      new THREE.MeshStandardMaterial({ color: i < 4 ? 0xbec5ff : 0x7e89e8, emissive: 0x3d477f, emissiveIntensity: .8, metalness: .2, roughness: .3, transparent: true, opacity: 0 })
    );
    node.position.set(...pos);
    node.scale.setScalar(0.001);
    node.userData.threshold = i / cPositions.length;
    cGroup.add(node);
    cNodes.push(node);

    const geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0), node.position.clone()]);
    const line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0x7f8cff, transparent: true, opacity: 0 }));
    line.userData.threshold = node.userData.threshold;
    cGroup.add(line);
    cLines.push(line);

    const pulse = new THREE.Mesh(new THREE.SphereGeometry(0.045, 8, 6), cPulseMaterial.clone());
    pulse.userData = { to: node.position.clone(), threshold: node.userData.threshold, phase: i / cPositions.length };
    pulse.visible = false;
    cGroup.add(pulse);
    cPulses.push(pulse);
  });

  let cProgress = 0;
  const resizeCompound = () => {
    const rect = compoundStage.getBoundingClientRect();
    const w = Math.max(1, Math.round(rect.width));
    const h = Math.max(1, Math.round(rect.height));
    cRenderer.setSize(w, h, false);
    cCamera.aspect = w / h;
    cCamera.position.z = w < 560 ? 9.2 : 7.8;
    cCamera.updateProjectionMatrix();
  };
  new ResizeObserver(resizeCompound).observe(compoundStage);
  resizeCompound();

  const updateCompoundProgress = () => {
    const rect = compoundStory.getBoundingClientRect();
    const start = window.innerHeight * 0.72;
    const distance = Math.max(1, rect.height - window.innerHeight * 0.2);
    cProgress = THREE.MathUtils.clamp((start - rect.top) / distance, 0, 1);
    const stepIndex = Math.min(3, Math.floor(cProgress * 4.001));
    compoundStepEls.forEach((el, i) => el.classList.toggle('active', i <= stepIndex));
    if (compoundCount) compoundCount.textContent = String(Math.max(1, Math.round(1 + cProgress * 11))).padStart(2, '0');
  };
  window.addEventListener('scroll', updateCompoundProgress, { passive: true });
  window.addEventListener('resize', updateCompoundProgress, { passive: true });
  updateCompoundProgress();

  const cClock = new THREE.Clock();
  const renderCompound = () => {
    const t = cClock.getElapsedTime();
    cGroup.rotation.y = reducedMotion ? -0.08 : Math.sin(t * .13) * .11;
    cGroup.rotation.x = reducedMotion ? 0 : Math.sin(t * .09) * .035;
    cCore.rotation.y = reducedMotion ? 0 : t * .11;
    cShell.rotation.x = reducedMotion ? 0 : t * .07;
    cShell.rotation.y = reducedMotion ? 0 : -t * .09;

    cNodes.forEach((node, i) => {
      const visible = cProgress + .08 >= node.userData.threshold;
      const target = visible ? 1 : .001;
      node.scale.lerp(new THREE.Vector3(target, target, target), .08);
      node.material.opacity += ((visible ? .96 : 0) - node.material.opacity) * .08;
      cLines[i].material.opacity += ((visible ? .22 + cProgress * .16 : 0) - cLines[i].material.opacity) * .07;
      cPulses[i].visible = visible && !reducedMotion;
      if (cPulses[i].visible) {
        const a = (cPulses[i].userData.phase + t * (.08 + i * .002)) % 1;
        cPulses[i].position.lerpVectors(cCore.position, cPulses[i].userData.to, a);
        cPulses[i].material.opacity = .18 + Math.sin(a * Math.PI) * .68;
      }
    });

    cCore.scale.setScalar(1 + cProgress * .16 + (reducedMotion ? 0 : Math.sin(t * 2.1) * .018));
    cRenderer.render(cScene, cCamera);
    requestAnimationFrame(renderCompound);
  };
  renderCompound();
}
