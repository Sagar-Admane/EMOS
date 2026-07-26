import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function AnalyticsVisualizer3D({ data = [], type = 'contributors' }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 600;
    const height = 220;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 10, 18);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const chartGroup = new THREE.Group();
    scene.add(chartGroup);

    const items = data.slice(0, 10);
    const maxVal = Math.max(...items.map(d => type === 'contributors' ? (d.contributions || 1) : (d.count || 1)), 10);

    const barWidth = 0.8;
    const spacing = 1.4;
    const startX = -((items.length - 1) * spacing) / 2;

    items.forEach((item, idx) => {
      const val = type === 'contributors' ? (item.contributions || 1) : (item.count || 1);
      const normalizedHeight = Math.max((val / maxVal) * 7, 0.5);

      const geo = new THREE.BoxGeometry(barWidth, normalizedHeight, barWidth);

      // Pure monochrome wireframe colors: stark white for top 3, charcoal gray for others
      const isTop = idx < 3;
      const mat = new THREE.MeshBasicMaterial({
        color: isTop ? 0xffffff : 0x52525b,
        wireframe: true,
        transparent: true,
        opacity: isTop ? 0.9 : 0.6
      });

      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(startX + idx * spacing, normalizedHeight / 2 - 2, 0);
      chartGroup.add(mesh);
    });

    // Monochrome floor grid
    const gridHelper = new THREE.GridHelper(20, 20, 0x3f3f46, 0x18181b);
    gridHelper.position.y = -2.01;
    scene.add(gridHelper);

    let isDragging = false;
    let previousMouseX = 0;

    const handleMouseDown = (e) => {
      isDragging = true;
      previousMouseX = e.clientX;
    };

    const handleMouseMove = (e) => {
      if (!isDragging) return;
      const deltaX = e.clientX - previousMouseX;
      chartGroup.rotation.y += deltaX * 0.01;
      previousMouseX = e.clientX;
    };

    const handleMouseUp = () => {
      isDragging = false;
    };

    container.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    let animId;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      if (!isDragging) {
        chartGroup.rotation.y += 0.004;
      }
      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const newW = container.clientWidth || 600;
      camera.aspect = newW / height;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, height);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      container.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('resize', handleResize);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      scene.clear();
      renderer.dispose();
    };
  }, [data, type]);

  return (
    <div className="analytics-3d-card card" style={{ position: 'relative', overflow: 'hidden', padding: '16px 20px', marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span className="text-xs font-mono" style={{ textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-3)' }}>
          Monochrome 3D Distribution Mesh (Drag to Rotate)
        </span>
        <span className="badge badge-neutral" style={{ fontSize: 10 }}>Monochrome WebGL</span>
      </div>
      <div ref={mountRef} style={{ width: '100%', height: 220, cursor: 'grab' }} />
    </div>
  );
}
