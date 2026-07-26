import { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { motion, AnimatePresence } from 'motion/react';
import confetti from 'canvas-confetti';
import { ArrowRight, ArrowLeft, AlertTriangle, Terminal, Search, CheckCircle2, UserX, Sparkles, X, ChevronRight } from 'lucide-react';
import './StoryPresentation.css';

const SLIDES = [
  {
    id: 1,
    tag: 'SLIDE 01 / 05',
    sceneTitle: 'MONDAY MORNING | A NEW ENGINEER JOINS',
    narrative: '"It\'s your first day. You clone the repository. Three million lines of code. Thousands of commits. Hundreds of pull requests."',
    query: 'Where is authentication implemented?',
    aiAnswer: 'Authentication is implemented in app/auth/service.py and handles JWT tokens.',
    type: 'ai-success'
  },
  {
    id: 2,
    tag: 'SLIDE 02 / 05',
    sceneTitle: 'A REAL ENGINEERING PROBLEM',
    alert: 'CRITICAL ALERT: Login failures spiking after latest deployment.',
    narrative: 'You ask the AI coding assistant for the root decision context...',
    query: 'Why was Redis introduced into authentication?',
    aiAnswer: 'Found 14 code references in app/auth/cache.py... [Silence: No decision context found]',
    type: 'ai-fail'
  },
  {
    id: 3,
    tag: 'SLIDE 03 / 05',
    sceneTitle: 'THE HUNT BEGINS',
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
    tag: 'SLIDE 04 / 05',
    sceneTitle: 'INTRODUCING EMOS',
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
    tag: 'SLIDE 05 / 05',
    sceneTitle: 'ENGINEERING MEMORY OPERATING SYSTEM',
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

export default function StoryPresentation({ onEnterApp }) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const mountRef = useRef(null);

  const nextSlide = useCallback(() => {
    setCurrentSlide(prev => Math.min(prev + 1, SLIDES.length - 1));
  }, []);

  const prevSlide = useCallback(() => {
    setCurrentSlide(prev => Math.max(prev - 1, 0));
  }, []);

  // Keyboard navigation listener (ArrowRight, ArrowLeft, Space, Enter)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowRight' || e.key === 'Space') {
        e.preventDefault();
        if (currentSlide === SLIDES.length - 1) {
          handleLaunch();
        } else {
          nextSlide();
        }
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevSlide();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentSlide, nextSlide, prevSlide]);

  // 3D WebGL Camera Shifting per Slide
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

    // Core Wireframe Sphere
    const coreGeo = new THREE.IcosahedronGeometry(8, 2);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      wireframe: true,
      transparent: true,
      opacity: 0.75
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    mainGroup.add(coreMesh);

    // Torus Ring
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

      // Dynamically shift camera & mesh rotation speed based on currentSlide
      const slideSpeed = 1 + currentSlide * 0.4;
      coreMesh.rotation.y = t * 0.25 * slideSpeed;
      coreMesh.rotation.x = t * 0.15 * slideSpeed;
      ringMesh.rotation.z = t * 0.2 * slideSpeed;
      particles.rotation.y = t * 0.04;

      if (currentSlide === 1) {
        // Slide 2 Alert pulse
        const pulse = 1 + Math.sin(t * 8) * 0.08;
        coreMesh.scale.set(pulse, pulse, pulse);
      } else if (currentSlide === 3) {
        // Slide 4 EMOS expansion
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
  }, [currentSlide]);

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

  const slide = SLIDES[currentSlide];
  const isLast = currentSlide === SLIDES.length - 1;

  return (
    <motion.div 
      className="presentation-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div ref={mountRef} className="presentation-webgl-canvas" />

      {/* Top Header */}
      <header className="presentation-header">
        <div className="presentation-brand">
          <span className="presentation-logo">E</span>
          <span className="presentation-title">THE FORGOTTEN ENGINEER</span>
        </div>
        <div className="presentation-progress-tracker">
          <span className="tracker-text">{slide.tag}</span>
          <div className="tracker-bar-bg">
            <div 
              className="tracker-bar-fill" 
              style={{ width: `${((currentSlide + 1) / SLIDES.length) * 100}%` }} 
            />
          </div>
        </div>
        <button className="btn btn-ghost btn-sm presentation-skip-btn" onClick={handleLaunch}>
          Skip to Workspace <X size={14} />
        </button>
      </header>

      {/* Slide Content Viewport */}
      <div className="presentation-viewport">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSlide}
            className="presentation-card card"
            initial={{ opacity: 0, x: 40, scale: 0.98 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: -40, scale: 0.98 }}
            transition={{ duration: 0.35, ease: 'easeOut' }}
          >
            {/* Slide 1 */}
            {currentSlide === 0 && (
              <>
                <div className="slide-tag">{slide.tag}</div>
                <h2 className="slide-heading">{slide.sceneTitle}</h2>
                <p className="slide-narrative">{slide.narrative}</p>
                <div className="terminal-window">
                  <div className="terminal-bar"><Terminal size={12} /><span>Engineer Query</span></div>
                  <div className="terminal-query">&gt; {slide.query}</div>
                  <div className="terminal-response success">
                    <CheckCircle2 size={13} style={{ flexShrink: 0 }} />
                    <span>{slide.aiAnswer}</span>
                  </div>
                </div>
              </>
            )}

            {/* Slide 2 */}
            {currentSlide === 1 && (
              <>
                <div className="slide-tag alert">{slide.tag}</div>
                <div className="slide-alert-banner">
                  <AlertTriangle size={15} />
                  <span>{slide.alert}</span>
                </div>
                <p className="slide-narrative">{slide.narrative}</p>
                <div className="terminal-window alert">
                  <div className="terminal-bar"><Terminal size={12} /><span>Engineer Query</span></div>
                  <div className="terminal-query">&gt; {slide.query}</div>
                  <div className="terminal-response fail">
                    <Search size={13} style={{ flexShrink: 0 }} />
                    <span>{slide.aiAnswer}</span>
                  </div>
                </div>
              </>
            )}

            {/* Slide 3 */}
            {currentSlide === 2 && (
              <>
                <div className="slide-tag">{slide.tag}</div>
                <h2 className="slide-heading">{slide.sceneTitle}</h2>
                <div className="slide-quick-cuts">
                  {slide.dialogues.map((d, i) => (
                    <div key={i} className="slide-cut-item">
                      <span className="slide-cut-bullet">•</span>
                      <span>{d.text}</span>
                      {d.author && <span className="slide-cut-author">— {d.author}</span>}
                    </div>
                  ))}
                </div>
                <div className="slide-punchline-box">
                  <UserX size={20} />
                  <h3>"{slide.punchline}"</h3>
                </div>
              </>
            )}

            {/* Slide 4 */}
            {currentSlide === 3 && (
              <>
                <div className="slide-tag emos">{slide.tag}</div>
                <h2 className="slide-heading">EMOS Decision Memory</h2>
                <div className="terminal-window emos">
                  <div className="terminal-bar"><Terminal size={12} /><span>Engineer Query</span></div>
                  <div className="terminal-query">&gt; {slide.query}</div>
                  <div className="terminal-response emos">
                    <p className="emos-summary">{slide.emosAnswer.summary}</p>
                    <div className="emos-meta-pills">
                      <span className="badge badge-neutral">{slide.meta.pr}</span>
                      <span className="badge badge-neutral">Author: {slide.meta.author}</span>
                      <span className="badge badge-neutral">Reviewer: {slide.meta.reviewer}</span>
                      <span className="badge badge-neutral">{slide.emosAnswer.risk}</span>
                    </div>
                    <p className="emos-impact">{slide.emosAnswer.impact}</p>
                  </div>
                </div>
              </>
            )}

            {/* Slide 5 */}
            {currentSlide === 4 && (
              <>
                <div className="slide-tag">{slide.tag}</div>
                <h1 className="slide-final-title">EMOS</h1>
                <p className="slide-final-subtitle">Engineering Memory Operating System</p>
                <div className="slide-final-points">
                  {slide.points.map((pt, i) => (
                    <p key={i} className={`slide-point${i === 0 ? ' dimmed' : ''}`}>{pt}</p>
                  ))}
                </div>
                <div className="slide-tagline-box">
                  <Sparkles size={16} />
                  <p>"{slide.tagline}"</p>
                </div>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Bottom Navigation Controls & Keyboard Hint */}
      <footer className="presentation-footer">
        <div className="nav-buttons-group">
          <button 
            className="btn btn-ghost presentation-nav-btn"
            onClick={prevSlide}
            disabled={currentSlide === 0}
          >
            <ArrowLeft size={15} />
            <span>Previous</span>
          </button>

          {isLast ? (
            <motion.button 
              className="btn btn-primary presentation-launch-btn"
              onClick={handleLaunch}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.96 }}
            >
              <span>Launch EMOS Workspace</span>
              <ArrowRight size={16} />
            </motion.button>
          ) : (
            <button 
              className="btn btn-primary presentation-nav-btn next"
              onClick={nextSlide}
            >
              <span>Next Scene</span>
              <ChevronRight size={16} />
            </button>
          )}
        </div>

        <div className="keyboard-hint">
          <span>Use <kbd>→</kbd> <kbd>←</kbd> <kbd>Space</kbd> to navigate</span>
        </div>
      </footer>
    </motion.div>
  );
}
