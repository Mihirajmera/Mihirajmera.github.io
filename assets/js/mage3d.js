// 3D Mage: renders assets/models/mage.glb with three.js and turns it toward the cursor.
// Falls back to the 2D image (already on the page) if WebGL is missing, motion is reduced,
// or anything fails to load.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const hero = document.querySelector('.mage-hero');
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const canvasOk = (() => { try { return !!document.createElement('canvas').getContext('webgl2'); } catch (e) { return false; } })();

if (hero && !reduced && canvasOk) start().catch(() => hero.classList.remove('is-3d'));

async function start() {
  const url = hero.dataset.model;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'low-power' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const canvas = renderer.domElement;
  canvas.className = 'mage-canvas';
  canvas.setAttribute('aria-hidden', 'true');

  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0xb9b4aa, 2.1));
  const key = new THREE.DirectionalLight(0xffffff, 0.9);
  key.position.set(1.4, 1.8, 2.5);
  scene.add(key);

  const camera = new THREE.PerspectiveCamera(28, 1, 0.1, 20);
  const gltf = await new GLTFLoader().loadAsync(url);
  const model = gltf.scene;
  const box = new THREE.Box3().setFromObject(model);
  const size = box.getSize(new THREE.Vector3());
  const pivot = new THREE.Group();          // rotate around the chest, not the feet
  model.position.set(-(box.min.x + size.x / 2), -box.min.y - size.y * 0.55, 0);
  pivot.position.y = size.y * 0.55;
  pivot.add(model);
  scene.add(pivot);
  camera.position.set(0, size.y * 0.5, 2.1);
  camera.lookAt(0, size.y * 0.5, 0);

  const resize = () => {
    const r = hero.getBoundingClientRect();
    renderer.setSize(r.width, r.height, false);
    camera.aspect = r.width / r.height;
    camera.updateProjectionMatrix();
  };
  hero.append(canvas);
  resize();
  new ResizeObserver(resize).observe(hero);

  const target = { x: 0, y: 0 }, cur = { x: 0, y: 0 };
  window.addEventListener('pointermove', (e) => {
    const r = hero.getBoundingClientRect();
    const dx = (e.clientX - (r.left + r.width / 2)) / (window.innerWidth / 2);
    const dy = (e.clientY - (r.top + r.height / 2)) / (window.innerHeight / 2);
    target.y = Math.max(-1, Math.min(1, dx)) * 0.42;
    target.x = Math.max(-1, Math.min(1, dy)) * 0.18;
  }, { passive: true });
  hero.addEventListener('pointerleave', () => { target.x = 0; target.y = 0; });

  let visible = true, t0 = performance.now();
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(hero);
  renderer.setAnimationLoop(() => {
    if (!visible || document.hidden) return;
    const t = (performance.now() - t0) / 1000;
    cur.x += (target.x - cur.x) * 0.08;
    cur.y += (target.y - cur.y) * 0.08;
    pivot.rotation.set(cur.x, cur.y + Math.sin(t * 0.6) * 0.04, Math.sin(t * 0.8) * 0.015);
    pivot.position.y = size.y * 0.55 + Math.sin(t * 1.2) * 0.008;
    renderer.render(scene, camera);
  });
  hero.classList.add('is-3d');
}
