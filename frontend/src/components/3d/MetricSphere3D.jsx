import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function MetricSphere3D({ commits = 0, prs = 0, contributors = 0 }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const size = 180;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(size, size);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    // Monochrome stark white wireframe sphere
    const geo = new THREE.IcosahedronGeometry(1.6, 2);
    const mat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      wireframe: true,
      transparent: true,
      opacity: 0.8
    });
    const sphere = new THREE.Mesh(geo, mat);
    group.add(sphere);

    // Torus Ring
    const ringGeo = new THREE.TorusGeometry(2.3, 0.015, 16, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xa1a1aa,
      transparent: true,
      opacity: 0.5
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 3;
    group.add(ring);

    let animId;
    let clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();
      sphere.rotation.y = t * 0.35;
      sphere.rotation.x = t * 0.2;
      ring.rotation.z = t * 0.25;
      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animId);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      geo.dispose();
      mat.dispose();
      ringGeo.dispose();
      ringMat.dispose();
      renderer.dispose();
    };
  }, [commits, prs, contributors]);

  return (
    <div
      ref={mountRef}
      style={{
        width: 180,
        height: 180,
        margin: '0 auto',
        filter: 'drop-shadow(0 0 10px rgba(255, 255, 255, 0.15))'
      }}
    />
  );
}
