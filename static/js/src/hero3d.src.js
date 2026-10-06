/* Hero helix: a double strand of sample points that assembles on load, turns slowly, follows
   the pointer a little and reacts to scroll. Built with Three.js (MIT, bundled locally by
   `npm run build:3d` into static/js/hero3d.js). Colours come from the page's theme tokens.
   Respects reduced motion (one still frame), pauses when off screen or in a hidden tab,
   and leaves the page untouched when WebGL is unavailable. */
import { AdditiveBlending, BufferAttribute, BufferGeometry, CanvasTexture, Color, Group, LineBasicMaterial, LineSegments, NormalBlending, PerspectiveCamera, Points, PointsMaterial, Scene, WebGLRenderer } from 'three';

const host = document.querySelector('[data-hero3d]');
if (host) start(host);

function tokenColor(name, fallback) {
  // CSS colours here are OKLCH; a 2D canvas converts any CSS colour to RGB for us.
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
  const c = document.createElement('canvas'); c.width = c.height = 1;
  const g = c.getContext('2d'); g.fillStyle = fallback; g.fillStyle = value; g.fillRect(0, 0, 1, 1);
  const [r, gr, b] = g.getImageData(0, 0, 1, 1).data; return new Color(r / 255, gr / 255, b / 255);
}
function dotTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
  const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(255,255,255,1)'); grad.addColorStop(0.45, 'rgba(255,255,255,0.9)'); grad.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grad; g.fillRect(0, 0, 64, 64); return new CanvasTexture(c);
}
const ease = t => 1 - Math.pow(1 - t, 4);

function start(el) {
  let renderer;
  try { renderer = new WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'low-power' }); }
  catch { return; } // no WebGL: the hero stays as designed without the strand
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  el.append(renderer.domElement);
  renderer.domElement.setAttribute('aria-hidden', 'true');

  const scene = new Scene(), camera = new PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 0, 16);
  const group = new Group(); scene.add(group);

  // Two strands, 2 x N points, plus rungs between paired points and loose "dust".
  const N = 150, TURNS = 3.2, LEN = 22, R = 2.1;
  const strand = new Float32Array(N * 2 * 3), target = new Float32Array(N * 2 * 3), seed = new Float32Array(N * 2 * 3);
  for (let i = 0; i < N; i++) {
    const t = i / (N - 1), x = (t - 0.5) * LEN, a = t * TURNS * Math.PI * 2;
    for (let s = 0; s < 2; s++) {
      const k = (i * 2 + s) * 3, ph = a + s * Math.PI;
      target[k] = x; target[k + 1] = Math.cos(ph) * R; target[k + 2] = Math.sin(ph) * R;
      seed[k] = (Math.random() - 0.5) * 34; seed[k + 1] = (Math.random() - 0.5) * 18; seed[k + 2] = (Math.random() - 0.5) * 14;
    }
  }
  const RUNGS = Math.floor(N / 3), rung = new Float32Array(RUNGS * 2 * 3);
  const dustCount = 260, dust = new Float32Array(dustCount * 3);
  for (let i = 0; i < dustCount; i++) { dust[i * 3] = (Math.random() - 0.5) * 36; dust[i * 3 + 1] = (Math.random() - 0.5) * 16; dust[i * 3 + 2] = (Math.random() - 0.5) * 10 - 2; }

  const tex = dotTexture();
  const strandGeo = new BufferGeometry(); strandGeo.setAttribute('position', new BufferAttribute(strand, 3));
  const strandMat = new PointsMaterial({ size: 0.2, map: tex, transparent: true, depthWrite: false, sizeAttenuation: true });
  const rungGeo = new BufferGeometry(); rungGeo.setAttribute('position', new BufferAttribute(rung, 3));
  const rungMat = new LineBasicMaterial({ transparent: true, opacity: 0.35, depthWrite: false });
  const dustGeo = new BufferGeometry(); dustGeo.setAttribute('position', new BufferAttribute(dust, 3));
  const dustMat = new PointsMaterial({ size: 0.07, map: tex, transparent: true, opacity: 0.55, depthWrite: false, sizeAttenuation: true });
  group.add(new LineSegments(rungGeo, rungMat), new Points(strandGeo, strandMat)); scene.add(new Points(dustGeo, dustMat));

  function paint() {
    const dark = (document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')) === 'dark';
    strandMat.color = tokenColor('--color-accent', '#6539a9');
    rungMat.color = tokenColor('--color-fg-soft', '#75737b');
    dustMat.color = tokenColor('--color-fg-soft', '#75737b');
    const blend = dark ? AdditiveBlending : NormalBlending;
    strandMat.blending = dustMat.blending = blend; strandMat.needsUpdate = dustMat.needsUpdate = true;
    strandMat.opacity = dark ? 0.95 : 0.85;
  }
  paint();
  new MutationObserver(paint).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', paint);

  function resize() {
    const w = el.clientWidth || 1, h = el.clientHeight || 1;
    renderer.setSize(w, h, false); camera.aspect = w / h;
    camera.position.z = w < 700 ? 24 : 16; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(el); resize();

  let px = 0, py = 0, tx = 0, ty = 0, scroll = 0;
  addEventListener('pointermove', e => { tx = (e.clientX / innerWidth - 0.5) * 2; ty = (e.clientY / innerHeight - 0.5) * 2; }, { passive: true });
  addEventListener('scroll', () => { scroll = Math.min(1, scrollY / Math.max(1, el.clientHeight)); }, { passive: true });

  const t0 = performance.now(), ASSEMBLE = reduced ? 0 : 2400;
  function frame(now) {
    const t = now - t0, k = ASSEMBLE ? ease(Math.min(1, t / ASSEMBLE)) : 1;
    for (let i = 0; i < strand.length; i++) strand[i] = seed[i] + (target[i] - seed[i]) * k;
    for (let r = 0; r < RUNGS; r++) {
      const i = r * 3, a = i * 2 * 3, b = (i * 2 + 1) * 3, o = r * 6;
      rung[o] = strand[a]; rung[o + 1] = strand[a + 1]; rung[o + 2] = strand[a + 2];
      rung[o + 3] = strand[b]; rung[o + 4] = strand[b + 1]; rung[o + 5] = strand[b + 2];
    }
    strandGeo.attributes.position.needsUpdate = true; rungGeo.attributes.position.needsUpdate = true;
    rungMat.opacity = 0.35 * k;
    if (!reduced) {
      px += (tx - px) * 0.04; py += (ty - py) * 0.04;
      group.rotation.x = t * 0.00022 + scroll * 1.6;
      group.rotation.y = px * 0.18; group.rotation.z = -0.12 + py * 0.06;
      group.position.y = -scroll * 2.4;
    } else { group.rotation.set(0.6, 0, -0.12); }
    renderer.render(scene, camera);
  }
  if (reduced) { frame(performance.now()); return; }

  let visible = true, raf = 0;
  const loop = now => { frame(now); raf = requestAnimationFrame(loop); };
  const run = () => { cancelAnimationFrame(raf); if (visible && !document.hidden) raf = requestAnimationFrame(loop); };
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; run(); }).observe(el);
  document.addEventListener('visibilitychange', run);
  el.classList.add('is-live'); run();
}
