import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import * as THREE from 'three';
import gsap from 'gsap';

export default function Background3D() {
  const containerRef = useRef(null);
  const location = useLocation();

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 30;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const mainGroup = new THREE.Group();
    scene.add(mainGroup);

    // 1. Pure Monochrome Particle Cloud
    const particleCount = 200;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const scales = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3]     = (Math.random() - 0.5) * 65;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 50;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 45;
      scales[i] = Math.random() * 1.5 + 0.5;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('scale', new THREE.BufferAttribute(scales, 1));

    const canvas = document.createElement('canvas');
    canvas.width = 16;
    canvas.height = 16;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
    grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
    grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(8, 8, 8, 0, Math.PI * 2);
    ctx.fill();

    const pTexture = new THREE.CanvasTexture(canvas);
    const pMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.7,
      map: pTexture,
      transparent: true,
      opacity: 0.35,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const particles = new THREE.Points(geometry, pMaterial);
    mainGroup.add(particles);

    // 2. Pure Wireframe Icosahedron Mesh (Monochrome Charcoal/Silver)
    const sphereGeo = new THREE.IcosahedronGeometry(13, 2);
    const sphereMat = new THREE.MeshBasicMaterial({
      color: 0x52525b,
      wireframe: true,
      transparent: true,
      opacity: 0.15
    });
    const wireSphere = new THREE.Mesh(sphereGeo, sphereMat);
    mainGroup.add(wireSphere);

    // 3. Crisp Monochrome Connecting Lines
    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.06
    });

    const linePositions = new Float32Array(particleCount * 6);
    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
    const linesMesh = new THREE.LineSegments(lineGeometry, lineMaterial);
    mainGroup.add(linesMesh);

    // Mouse tracking physics
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const handleMouseMove = (e) => {
      mouseX = (e.clientX - window.innerWidth / 2) * 0.0006;
      mouseY = (e.clientY - window.innerHeight / 2) * 0.0006;
    };

    window.addEventListener('mousemove', handleMouseMove);

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    let animId;
    let clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      targetX += (mouseX - targetX) * 0.04;
      targetY += (mouseY - targetY) * 0.04;

      mainGroup.rotation.y = elapsedTime * 0.025 + targetX * 1.5;
      mainGroup.rotation.x = Math.sin(elapsedTime * 0.015) * 0.08 + targetY * 1.5;
      wireSphere.rotation.z = elapsedTime * 0.04;

      const posArr = particles.geometry.attributes.position.array;
      for (let i = 0; i < particleCount; i++) {
        posArr[i * 3 + 1] += Math.sin(elapsedTime + posArr[i * 3]) * 0.004;
      }
      particles.geometry.attributes.position.needsUpdate = true;

      let lineIdx = 0;
      const lineArr = linesMesh.geometry.attributes.position.array;
      for (let i = 0; i < particleCount; i += 3) {
        for (let j = i + 1; j < particleCount; j += 6) {
          const dx = posArr[i * 3] - posArr[j * 3];
          const dy = posArr[i * 3 + 1] - posArr[j * 3 + 1];
          const dz = posArr[i * 3 + 2] - posArr[j * 3 + 2];
          const distSq = dx * dx + dy * dy + dz * dz;

          if (distSq < 140) {
            lineArr[lineIdx++] = posArr[i * 3];
            lineArr[lineIdx++] = posArr[i * 3 + 1];
            lineArr[lineIdx++] = posArr[i * 3 + 2];

            lineArr[lineIdx++] = posArr[j * 3];
            lineArr[lineIdx++] = posArr[j * 3 + 1];
            lineArr[lineIdx++] = posArr[j * 3 + 2];
          }
        }
      }
      linesMesh.geometry.setDrawRange(0, lineIdx / 3);
      linesMesh.geometry.attributes.position.needsUpdate = true;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animId);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      geometry.dispose();
      sphereGeo.dispose();
      pMaterial.dispose();
      sphereMat.dispose();
      lineMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    let opacity = 0.4;
    switch (location.pathname) {
      case '/': opacity = 0.35; break;
      case '/analytics': opacity = 0.45; break;
      case '/ai': opacity = 0.3; break;
      case '/connect': opacity = 0.4; break;
      default: break;
    }

    gsap.to(containerRef.current, {
      duration: 1.0,
      ease: 'power2.out',
      opacity: opacity
    });
  }, [location.pathname]);

  return (
    <div
      ref={containerRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        zIndex: 0,
        opacity: 0.35,
        transition: 'opacity 0.5s ease'
      }}
    />
  );
}
