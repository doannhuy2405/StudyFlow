<template>
  <canvas ref="canvas" class="neural-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';

const canvas = ref(null);
let animationId = null;

// Cấu hình mạng nơ-ron
const config = {
  nodeCount: 350,
  lineWidth: 1,
  lineColor: 'rgba(0, 255, 255, 1)',
  nodeColor: 'rgba(0, 255, 255, 1)',
  nodeRadius: 3,
  speed: 0.8,
};

class Node {
  constructor(width, height) {
    this.x = Math.random() * width;
    this.y = Math.random() * height;
    this.vx = (Math.random() - 0.5) * config.speed;
    this.vy = (Math.random() - 0.5) * config.speed;
  }

  update(width, height) {
    if (this.x <= 0 || this.x >= width) this.vx *= -1;
    if (this.y <= 0 || this.y >= height) this.vy *= -1;
    this.x += this.vx;
    this.y += this.vy;
  }
}

onMounted(async () => {
  // Đảm bảo canvas đã gán xong trong DOM
  await nextTick();

  if (!canvas.value) return;
  const ctx = canvas.value.getContext('2d');
  if (!ctx) return;

  canvas.value.width = window.innerWidth;
  canvas.value.height = window.innerHeight;

  const nodes = Array.from({ length: config.nodeCount }, () =>
    new Node(canvas.value.width, canvas.value.height)
  );

  function draw() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.value.width, canvas.value.height);

    // Vẽ đường kết nối giữa các node
    nodes.forEach((node1, i) => {
      nodes.slice(i + 1).forEach((node2) => {
        const distance = Math.hypot(node2.x - node1.x, node2.y - node1.y);
        if (distance < 150) {
          ctx.beginPath();
          ctx.strokeStyle = config.lineColor;
          ctx.lineWidth = config.lineWidth * (1 - distance / 150);
          ctx.moveTo(node1.x, node1.y);
          ctx.lineTo(node2.x, node2.y);
          ctx.stroke();
        }
      });
    });

    // Vẽ node
    nodes.forEach((node) => {
      node.update(canvas.value.width, canvas.value.height);
      ctx.beginPath();
      ctx.fillStyle = config.nodeColor;
      ctx.arc(node.x, node.y, config.nodeRadius, 0, Math.PI * 2);
      ctx.fill();
    });

    animationId = requestAnimationFrame(draw);
  }

  draw();

  window.addEventListener('resize', () => {
    if (!canvas.value) return;
    canvas.value.width = window.innerWidth;
    canvas.value.height = window.innerHeight;
  });
});

onUnmounted(() => {
  cancelAnimationFrame(animationId);
});
</script>

<style scoped>
.neural-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 0;
  opacity: 0.6;
  display: block;
}
</style>
