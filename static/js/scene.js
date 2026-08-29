(() => {
  const canvas = document.getElementById("spectral-field");
  if (!canvas) return;

  const context = canvas.getContext("2d", { alpha: true });
  if (!context) {
    canvas.hidden = true;
    return;
  }
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const pointer = { x: 0.68, y: 0.44, tx: 0.68, ty: 0.44 };
  const nodes = Array.from({ length: 32 }, (_, index) => ({
    x: ((index * 47) % 97) / 97,
    y: ((index * 71) % 101) / 101,
    phase: index * 0.63,
    radius: 0.7 + (index % 4) * 0.35,
  }));

  let width = 0;
  let height = 0;
  let pixelRatio = 1;
  let frame = null;

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    pixelRatio = Math.min(window.devicePixelRatio || 1, 1.5);
    canvas.width = Math.floor(width * pixelRatio);
    canvas.height = Math.floor(height * pixelRatio);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    if (reduceMotion) draw(0);
  }

  function drawContour(time, row, color, direction) {
    const baseY = height * (0.14 + row * 0.052);
    const distance = Math.abs(baseY / height - pointer.y);
    const influence = Math.max(0, 1 - distance * 4.2);
    const amplitude = 6 + influence * 30;
    const frequency = 0.012 + row * 0.00018;
    context.beginPath();

    for (let x = -24; x <= width + 24; x += 16) {
      const normalizedX = x / Math.max(width, 1);
      const pointerWave = Math.exp(-Math.pow((normalizedX - pointer.x) * 4.4, 2));
      const wave = Math.sin(x * frequency + time * 0.00018 * direction + row * 0.73);
      const secondary = Math.sin(x * 0.004 - time * 0.00011 + row) * 4;
      const y = baseY + wave * amplitude * (0.35 + pointerWave * 0.65) + secondary;
      if (x === -24) context.moveTo(x, y);
      else context.lineTo(x, y);
    }

    context.strokeStyle = color;
    context.lineWidth = row % 5 === 0 ? 1.15 : 0.65;
    context.stroke();
  }

  function drawNodes(time) {
    nodes.forEach((node) => {
      const drift = reduceMotion ? 0 : Math.sin(time * 0.00025 + node.phase) * 8;
      const x = node.x * width + drift;
      const y = node.y * height + Math.cos(time * 0.00018 + node.phase) * 6;
      const dx = x / width - pointer.x;
      const dy = y / height - pointer.y;
      const proximity = Math.max(0, 1 - Math.sqrt(dx * dx + dy * dy) * 4.5);
      context.beginPath();
      context.arc(x, y, node.radius + proximity * 1.7, 0, Math.PI * 2);
      context.fillStyle = `rgba(137, 237, 255, ${0.08 + proximity * 0.35})`;
      context.fill();
    });
  }

  function draw(time) {
    context.clearRect(0, 0, width, height);
    pointer.x += (pointer.tx - pointer.x) * 0.055;
    pointer.y += (pointer.ty - pointer.y) * 0.055;

    const glow = context.createRadialGradient(
      pointer.x * width,
      pointer.y * height,
      0,
      pointer.x * width,
      pointer.y * height,
      Math.max(width, height) * 0.42
    );
    glow.addColorStop(0, "rgba(63, 227, 255, 0.12)");
    glow.addColorStop(0.45, "rgba(115, 82, 255, 0.055)");
    glow.addColorStop(1, "rgba(6, 12, 31, 0)");
    context.fillStyle = glow;
    context.fillRect(0, 0, width, height);

    context.save();
    context.globalCompositeOperation = "screen";
    for (let row = 0; row < 16; row += 1) {
      drawContour(time, row, row % 3 === 0 ? "rgba(120, 230, 255, .18)" : "rgba(139, 111, 255, .10)", row % 2 ? 1 : -1);
    }
    drawNodes(time);
    context.restore();

    if (!reduceMotion && !document.hidden) frame = requestAnimationFrame(draw);
  }

  window.addEventListener("pointermove", (event) => {
    pointer.tx = event.clientX / Math.max(window.innerWidth, 1);
    pointer.ty = event.clientY / Math.max(window.innerHeight, 1);
    document.documentElement.style.setProperty("--pointer-x", `${pointer.tx * 100}%`);
    document.documentElement.style.setProperty("--pointer-y", `${pointer.ty * 100}%`);
  }, { passive: true });

  window.addEventListener("resize", resize, { passive: true });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && frame) {
      cancelAnimationFrame(frame);
      frame = null;
    } else if (!document.hidden && !reduceMotion && !frame) {
      frame = requestAnimationFrame(draw);
    }
  });

  resize();
  if (!reduceMotion) frame = requestAnimationFrame(draw);
})();
