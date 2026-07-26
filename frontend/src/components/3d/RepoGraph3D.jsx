import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function RepoGraph3D({ repos = [] }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 800;
    const height = 260;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
    camera.position.z = 18;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const graphGroup = new THREE.Group();
    scene.add(graphGroup);

    // Central Monochrome EMOS Knowledge Hub Node
    const hubGeo = new THREE.OctahedronGeometry(1.6, 2);
    const hubMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      wireframe: true,
      transparent: true,
      opacity: 0.9
    });
    const hubNode = new THREE.Mesh(hubGeo, hubMat);
    graphGroup.add(hubNode);

    const numRepos = Math.max(repos.length, 3);
    const radius = 7.5;

    for (let i = 0; i < numRepos; i++) {
      const angle = (i / numRepos) * Math.PI * 2;
      const repo = repos[i] || { full_name: `Repo ${i + 1}`, status: 'ready' };

      const nodeGeo = new THREE.IcosahedronGeometry(0.8, 1);
      const isReady = repo.status === 'ready';
      const nodeMat = new THREE.MeshBasicMaterial({
        color: isReady ? 0xffffff : 0x71717a,
        wireframe: true,
        transparent: true,
        opacity: isReady ? 0.85 : 0.5
      });
      const nodeMesh = new THREE.Mesh(nodeGeo, nodeMat);
      nodeMesh.position.set(Math.cos(angle) * radius, Math.sin(angle) * (radius * 0.4), Math.sin(angle) * (radius * 0.6));
      graphGroup.add(nodeMesh);

      const lineGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        nodeMesh.position
      ]);
      const lineMat = new THREE.LineDashedMaterial({
        color: isReady ? 0xffffff : 0x52525b,
        dashSize: 0.3,
        gapSize: 0.2,
        transparent: true,
        opacity: 0.35
      });
      const line = new THREE.Line(lineGeo, lineMat);
      line.computeLineDistances();
      graphGroup.add(line);
    }

    let animId;
    let clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();

      hubNode.rotation.y = t * 0.4;
      hubNode.rotation.x = t * 0.25;

      graphGroup.rotation.y = t * 0.12;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const newW = container.clientWidth || 800;
      camera.aspect = newW / height;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, height);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      scene.clear();
      renderer.dispose();
    };
  }, [repos]);

  return (
    <div className="card" style={{ padding: '16px 20px', marginBottom: 24, position: 'relative', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="text-xs font-mono" style={{ textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-3)' }}>
          Monochrome Constellation Graph
        </span>
        <span className="badge badge-neutral" style={{ fontSize: 10 }}>3D Orbiting Mesh</span>
      </div>
      <div ref={mountRef} style={{ width: '100%', height: 260 }} />
    </div>
  );
}
