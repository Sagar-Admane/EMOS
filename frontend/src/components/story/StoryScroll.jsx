import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { motion } from 'motion/react';
import confetti from 'canvas-confetti';
import { ArrowRight, AlertTriangle, Terminal, Search, CheckCircle2, UserX, Sparkles, X, ChevronDown } from 'lucide-react';
import './StoryScroll.css';

const SCENES = [
  {
    id: 1,
    tag: 'SCENE 1: MONDAY MORNING',
    title: 'A New Engineer Joins',
    narrative: '"It\'s your first day. You clone the repository. Three million lines of code. Thousands of commits. Hundreds of pull requests."',
    query: 'Where is authentication implemented?',
    aiAnswer: 'Authentication is implemented in app/auth/service.py and handles JWT tokens.',
    type: 'ai-success'
  },
  {
    id: 2,
    tag: 'SCENE 2: PRODUCTION FAILURE',
    title: 'A Real Engineering Problem',
    alert: 'CRITICAL ALERT: Login failures spiking after latest deployment.',
    narrative: 'You ask the AI coding assistant for the root decision context...',
    query: 'Why was Redis introduced into authentication?',
    aiAnswer: 'Found 14 code references in app/auth/cache.py... [Silence: No decision context found]',
    type: 'ai-fail'
  },
  {
    id: 3,
    tag: 'SCENE 3: THE HUNT BEGINS',
    title: 'The Search for Lost Knowledge',
    dialogues: [
      { text: 'Searching through old pull requests...', type: 'search' },
      { text: 'Reading vague commit messages ("fixed stuff")...', type: 'commit' },
      { text: '"I think Alice knew."', author: 'Senior Engineer' },
      { text: '"She left the company last year."', author: 'Teammate' }
    ],
    punchline: 'The code survived. The knowledge didn\'t.'
  },
  {
    id: 4,
    tag: 'SCENE 4: INTRODUCING EMOS',
    title: 'Engineering Memory Activated',
    query: 'Why was Redis introduced into authentication?',
    emosAnswer: {
      summary: 'Redis was introduced in PR #128 to reduce authentication latency during peak traffic. The decision was made by Alice, reviewed by Bob, after database bottlenecks caused repeated login failures.',
      impact: 'Impacts Login, Sessions, and Payments.',
      risk: 'HIGH RISK SCORE (8.9/10)'
    },
    meta: {
      pr: 'PR #128',
      author: 'Alice',
      reviewer: 'Bob',
      reason: 'Database Bottleneck'
    }
  },
  {
    id: 5,
    tag: 'SCENE 5: CLOSING',
    title: 'Engineering Memory Operating System',
    points: [
      'AI can explain what your code does.',
      'EMOS explains why your engineering decisions were made...',
      '...who made them...',
      '...how your systems evolved...',
      '...and what will happen before you change them.'
    ],
    tagline: 'Because great engineering isn\'t just written in code — it\'s written in decisions.'
  }
];

export default function StoryScroll({ onEnterApp }) {
  const mountRef = useRef(null);
  const [activeScene, setActiveScene] = useState(0);
  const scrollContainerRef = useRef(null);

  // 3D WebGL Scene reacting dynamically to scroll position
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 24;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const mainGroup = new THREE.Group();
    scene.add(mainGroup);

    // Wireframe Core
    const coreGeo = new THREE.IcosahedronGeometry(8, 2);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      wireframe: true,
      transparent: true,
      opacity: 0.75
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    mainGroup.add(coreMesh);

    // Torus Rings
    const ringGeo = new THREE.TorusGeometry(12, 0.03, 16, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xa1a1aa,
      transparent: true,
      opacity: 0.4
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI / 3;
    mainGroup.add(ringMesh);

    // Particle Cloud
    const pCount = 280;
    const pGeo = new THREE.BufferGeometry();
    const pPos = new Float32Array(pCount * 3);

    for (let i = 0; i < pCount; i++) {
      pPos[i * 3]     = (Math.random() - 0.5) * 80;
      pPos[i * 3 + 1] = (Math.random() - 0.5) * 60;
      pPos[i * 3 + 2] = (Math.random() - 0.5) * 50;
    }
    pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
    const pMat = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.6,
      transparent: true,
      opacity: 0.5
    });
    const particles = new THREE.Points(pGeo, pMat);
    mainGroup.add(particles);

    let animId;
    let clock = new THREE.Clock();

    const animateLoop = () => {
      animId = requestAnimationFrame(animateLoop);
      const t = clock.getElapsedTime();

      // Camera distance and rotation speed shift per activeScene
      const sceneSpeed = 1 + activeScene * 0.4;
      coreMesh.rotation.y = t * 0.25 * sceneSpeed;
      coreMesh.rotation.x = t * 0.15 * sceneSpeed;
      ringMesh.rotation.z = t * 0.2 * sceneSpeed;
      particles.rotation.y = t * 0.04;

      if (activeScene === 1) {
        const pulse = 1 + Math.sin(t * 8) * 0.08;
        coreMesh.scale.set(pulse, pulse, pulse);
      } else if (activeScene === 3) {
        const expand = 1.25 + Math.sin(t * 2) * 0.04;
        coreMesh.scale.set(expand, expand, expand);
      } else {
        coreMesh.scale.lerp(new THREE.Vector3(1, 1, 1), 0.05);
      }

      renderer.render(scene, camera);
    };

    animateLoop();

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      coreGeo.dispose();
      coreMat.dispose();
      ringGeo.dispose();
      ringMat.dispose();
      pGeo.dispose();
      pMat.dispose();
      renderer.dispose();
    };
  }, [activeScene]);

  // Handle scroll events inside story overlay
  const handleScroll = (e) => {
    const scrollTop = e.target.scrollTop;
    const height = e.target.clientHeight;
    const idx = Math.min(Math.floor((scrollTop + height * 0.4) / height), SCENES.length - 1);
    if (idx !== activeScene) {
      setActiveScene(idx);
    }
  };

  const handleLaunch = () => {
    confetti({
      particleCount: 120,
      spread: 80,
      origin: { y: 0.6 },
      colors: ['#ffffff', '#a1a1aa', '#52525b', '#000000']
    });
    sessionStorage.setItem('emos_story_seen', 'true');
    if (onEnterApp) onEnterApp();
  };

  return (
    <motion.div 
      className="story-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Background 3D WebGL Canvas */}
      <div ref={mountRef} className="story-webgl-canvas" />

      {/* Header */}
      <header className="story-header">
        <div className="story-brand">
          <span className="story-logo-badge">E</span>
          <span className="story-brand-title">THE FORGOTTEN ENGINEER</span>
        </div>
        <button className="btn btn-ghost btn-sm story-skip-btn" onClick={handleLaunch}>
          Skip to Workspace <X size={14} />
        </button>
      </header>

      {/* Right Progress Dots */}
      <div className="story-progress-dots">
        {SCENES.map((sc, idx) => (
          <div 
            key={sc.id} 
            className={`story-dot${idx === activeScene ? ' active' : ''}`}
            onClick={() => {
              scrollContainerRef.current?.scrollTo({
                top: idx * window.innerHeight,
                behavior: 'smooth'
              });
            }}
          />
        ))}
      </div>

      {/* Scrollable Story Container */}
      <div 
        ref={scrollContainerRef} 
        className="story-scroll-container"
        onScroll={handleScroll}
      >
        {/* Scene 1 */}
        <section className="story-chapter-section">
          <motion.div className="story-card card" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="story-chapter-badge">{SCENES[0].tag}</div>
            <h2 className="story-heading">{SCENES[0].title}</h2>
            <p className="story-narrative-quote">{SCENES[0].narrative}</p>

            <div className="terminal-window">
              <div className="terminal-bar"><Terminal size={12} /><span>Engineer Query</span></div>
              <div className="terminal-query">&gt; {SCENES[0].query}</div>
              <div className="terminal-response success">
                <CheckCircle2 size={13} style={{ flexShrink: 0 }} />
                <span>{SCENES[0].aiAnswer}</span>
              </div>
            </div>
            <div className="story-scroll-hint">
              <span>Scroll to continue</span>
              <ChevronDown size={14} className="story-chevron-bounce" />
            </div>
          </motion.div>
        </section>

        {/* Scene 2 */}
        <section className="story-chapter-section">
          <motion.div className="story-card card alert-card" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="story-chapter-badge alert">{SCENES[1].tag}</div>
            <div className="story-alert-banner">
              <AlertTriangle size={15} />
              <span>{SCENES[1].alert}</span>
            </div>
            <p className="story-narrative-quote">{SCENES[1].narrative}</p>

            <div className="terminal-window alert">
              <div className="terminal-bar"><Terminal size={12} /><span>Engineer Query</span></div>
              <div className="terminal-query">&gt; {SCENES[1].query}</div>
              <div className="terminal-response fail">
                <Search size={13} style={{ flexShrink: 0 }} />
                <span>{SCENES[1].aiAnswer}</span>
              </div>
            </div>
            <div className="story-scroll-hint">
              <span>Scroll to continue</span>
              <ChevronDown size={14} className="story-chevron-bounce" />
            </div>
          </motion.div>
        </section>

        {/* Scene 3 */}
        <section className="story-chapter-section">
          <motion.div className="story-card card" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="story-chapter-badge">{SCENES[2].tag}</div>
            <h2 className="story-heading">{SCENES[2].title}</h2>

            <div className="story-quick-cuts">
              {SCENES[2].dialogues.map((d, i) => (
                <div key={i} className="story-cut-item">
                  <span className="story-cut-bullet">•</span>
                  <span>{d.text}</span>
                  {d.author && <span className="story-cut-author">— {d.author}</span>}
                </div>
              ))}
            </div>

            <div className="story-punchline-box">
              <UserX size={20} />
              <h3>"{SCENES[2].punchline}"</h3>
            </div>
            <div className="story-scroll-hint">
              <span>Scroll to continue</span>
              <ChevronDown size={14} className="story-chevron-bounce" />
            </div>
          </motion.div>
        </section>

        {/* Scene 4 */}
        <section className="story-chapter-section">
          <motion.div className="story-card card emos-hero-card" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="story-chapter-badge emos">{SCENES[3].tag}</div>
            <h2 className="story-heading">EMOS Decision Memory</h2>

            <div className="terminal-window emos">
              <div className="terminal-bar"><Terminal size={12} /><span>Engineer Query</span></div>
              <div className="terminal-query">&gt; {SCENES[3].query}</div>
              <div className="terminal-response emos">
                <p className="emos-summary">{SCENES[3].emosAnswer.summary}</p>
                <div className="emos-meta-pills">
                  <span className="badge badge-neutral">{SCENES[3].meta.pr}</span>
                  <span className="badge badge-neutral">Author: {SCENES[3].meta.author}</span>
                  <span className="badge badge-neutral">Reviewer: {SCENES[3].meta.reviewer}</span>
                  <span className="badge badge-neutral">{SCENES[3].emosAnswer.risk}</span>
                </div>
                <p className="emos-impact">{SCENES[3].emosAnswer.impact}</p>
              </div>
            </div>
            <div className="story-scroll-hint">
              <span>Scroll to conclusion</span>
              <ChevronDown size={14} className="story-chevron-bounce" />
            </div>
          </motion.div>
        </section>

        {/* Scene 5 */}
        <section className="story-chapter-section">
          <motion.div className="story-card card" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="story-chapter-badge">{SCENES[4].tag}</div>
            <h1 className="story-final-title">EMOS</h1>
            <p className="story-final-subtitle">Engineering Memory Operating System</p>

            <div className="story-final-points">
              {SCENES[4].points.map((pt, i) => (
                <p key={i} className={`story-point${i === 0 ? ' dimmed' : ''}`}>{pt}</p>
              ))}
            </div>

            <div className="story-tagline-box">
              <Sparkles size={16} />
              <p>"{SCENES[4].tagline}"</p>
            </div>

            <motion.button 
              className="btn btn-primary story-cta-btn"
              onClick={handleLaunch}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.96 }}
            >
              <span>Launch EMOS Workspace</span>
              <ArrowRight size={16} />
            </motion.button>
          </motion.div>
        </section>

      </div>
    </motion.div>
  );
}
