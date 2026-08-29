const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

async function createScene(canvas, mobileMode) {
  if (!canvas || reduceMotion || !window.WebGLRenderingContext) return;
  try {
    const THREE = await import("https://cdn.jsdelivr.net/npm/three@0.168.0/build/three.module.js");
    if (document.hidden) return;
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: !mobileMode });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, mobileMode ? 1.25 : 1.5));
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 20);
    camera.position.z = 5;
    const material = new THREE.MeshBasicMaterial({ color: 0x72d9db, transparent: true, opacity: mobileMode ? 0.22 : 0.11, wireframe: !mobileMode });
    const object = new THREE.Mesh(new THREE.IcosahedronGeometry(mobileMode ? 0.62 : 1.18, mobileMode ? 3 : 2), material);
    object.rotation.set(0.25, -0.35, 0);
    scene.add(object);
    const target = { x: 0, y: 0 };
    canvas.parentElement?.addEventListener("pointermove", (event) => {
      const rect = canvas.getBoundingClientRect();
      target.x = ((event.clientX - rect.left) / rect.width - 0.5) * 0.16;
      target.y = ((event.clientY - rect.top) / rect.height - 0.5) * -0.16;
    }, { passive: true });
    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      renderer.setSize(rect.width, rect.height, false);
      camera.aspect = rect.width / rect.height;
      camera.updateProjectionMatrix();
    };
    new ResizeObserver(resize).observe(canvas);
    resize();
    let frame;
    const render = (time) => {
      if (document.hidden) return;
      object.rotation.y += 0.002;
      object.rotation.x = 0.24 + Math.sin(time * 0.0005) * 0.06;
      object.position.x += (target.x - object.position.x) * 0.025;
      object.position.y += (target.y - object.position.y) * 0.025;
      renderer.render(scene, camera);
      frame = requestAnimationFrame(render);
    };
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden && !frame) frame = requestAnimationFrame(render);
      if (document.hidden && frame) { cancelAnimationFrame(frame); frame = null; }
    });
    frame = requestAnimationFrame(render);
  } catch {
    canvas.classList.add("scene-unavailable");
  }
}

createScene(document.getElementById("depth-scene"), false);
createScene(document.getElementById("analysis-depth-scene"), true);
