// Progressive Three.js enhancement. If the CDN is unavailable, app.js keeps a 2D animated fallback alive.
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.min.js';

const canvas = document.getElementById('field');
if (!canvas || window.matchMedia('(prefers-reduced-motion: reduce)').matches) throw new Error('Three scene skipped');

window.__ICONIC_STOP_FALLBACK__?.();

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.7));
renderer.setSize(window.innerWidth, window.innerHeight, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x070912, 0.038);
const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 120);
camera.position.set(0, 0.2, 11.8);

const group = new THREE.Group();
scene.add(group);

// Intelligence core
const coreGeo = new THREE.IcosahedronGeometry(1.42, 2);
const coreMat = new THREE.MeshBasicMaterial({ color: 0x707cf3, wireframe: true, transparent: true, opacity: 0.27 });
const core = new THREE.Mesh(coreGeo, coreMat);
core.position.set(3.9, .55, -1.2);
group.add(core);

const innerGeo = new THREE.IcosahedronGeometry(.86, 3);
const innerMat = new THREE.MeshBasicMaterial({ color: 0xcbd0ff, transparent: true, opacity: .12 });
const inner = new THREE.Mesh(innerGeo, innerMat);
inner.position.copy(core.position);
group.add(inner);

for (const [scale, rot, opacity] of [[1.9, .2, .13],[2.45, 1.05, .09],[3.05, 2.0, .055]]) {
  const ringGeo = new THREE.TorusGeometry(scale, .008, 6, 160);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x9fa9ff, transparent: true, opacity });
  const ring = new THREE.Mesh(ringGeo, ringMat);
  ring.position.copy(core.position);
  ring.rotation.set(rot * .45, rot, rot * .2);
  ring.userData.speed = .00035 + scale * .00009;
  group.add(ring);
}

// Node field
const nodeCount = 175;
const positions = new Float32Array(nodeCount * 3);
const nodes = [];
for (let i = 0; i < nodeCount; i++) {
  const x = (Math.random() - .5) * 24;
  const y = (Math.random() - .5) * 15;
  const z = (Math.random() - .5) * 18 - 2;
  positions[i*3] = x; positions[i*3+1] = y; positions[i*3+2] = z;
  nodes.push(new THREE.Vector3(x,y,z));
}
const pGeo = new THREE.BufferGeometry();
pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
const pMat = new THREE.PointsMaterial({ color: 0xb8c0ff, size: .035, transparent: true, opacity: .48, sizeAttenuation: true });
const points = new THREE.Points(pGeo, pMat);
scene.add(points);

// Sparse connections for a neural / constellation field
const linePositions = [];
for (let i = 0; i < nodes.length; i++) {
  for (let j = i + 1; j < nodes.length && j < i + 12; j++) {
    const a = nodes[i], b = nodes[j];
    if (a.distanceTo(b) < 2.3 && Math.random() > .52) {
      linePositions.push(a.x,a.y,a.z,b.x,b.y,b.z);
    }
  }
}
const lGeo = new THREE.BufferGeometry();
lGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
const lMat = new THREE.LineBasicMaterial({ color: 0x6f79df, transparent: true, opacity: .07 });
const lines = new THREE.LineSegments(lGeo, lMat);
scene.add(lines);

// Ambient depth particles
const dustCount = 500;
const dustPositions = new Float32Array(dustCount * 3);
for (let i=0;i<dustCount;i++) {
  dustPositions[i*3]=(Math.random()-.5)*34;
  dustPositions[i*3+1]=(Math.random()-.5)*20;
  dustPositions[i*3+2]=(Math.random()-.5)*30-8;
}
const dustGeo = new THREE.BufferGeometry();
dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPositions,3));
const dustMat = new THREE.PointsMaterial({color:0x8892ff,size:.014,transparent:true,opacity:.22});
const dust = new THREE.Points(dustGeo,dustMat);
scene.add(dust);

const mouse = { x: 0, y: 0 };
window.addEventListener('pointermove', (e) => {
  mouse.x = (e.clientX / window.innerWidth - .5) * 2;
  mouse.y = (e.clientY / window.innerHeight - .5) * 2;
}, { passive: true });

const clock = new THREE.Clock();
function animate() {
  const t = clock.getElapsedTime();
  const scroll = window.scrollY / Math.max(document.body.scrollHeight - window.innerHeight, 1);

  core.rotation.x = t * .10;
  core.rotation.y = t * .16;
  inner.rotation.x = -t * .075;
  inner.rotation.z = t * .12;
  inner.scale.setScalar(1 + Math.sin(t * 1.5) * .035);

  group.children.forEach((child) => {
    if (child.userData.speed) {
      child.rotation.x += child.userData.speed * 1.7;
      child.rotation.z += child.userData.speed;
    }
  });

  points.rotation.y = t * .006 + scroll * .12;
  lines.rotation.y = points.rotation.y;
  dust.rotation.y = -t * .003;

  camera.position.x += ((mouse.x * .34) - camera.position.x) * .025;
  camera.position.y += ((-mouse.y * .22 + scroll * .7) - camera.position.y) * .025;
  camera.lookAt(0, 0, -2.5);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.7));
  renderer.setSize(window.innerWidth, window.innerHeight, false);
});
