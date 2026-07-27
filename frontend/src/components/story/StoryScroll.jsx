import { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { motion, AnimatePresence } from 'motion/react';
import confetti from 'canvas-confetti';
import {
  ArrowRight,
  AlertTriangle,
  Terminal,
  Search,
  CheckCircle2,
  UserX,
  Sparkles,
  X,
  ChevronDown,
  GitPullRequest,
  MessageSquare,
  Users,
  Activity,
  Zap,
  Brain,
  FileCode2,
  GitCommitHorizontal,
  Shield,
  Play,
  Volume2,
} from 'lucide-react';
import './StoryScroll.css';

/* ─── Scene Data ────────────────────────────────────────── */
const SCENES = [
  {
    id: 1,
    chapter: 'Chapter 1',
    title: 'Monday Morning',
    subtitle: 'A New Engineer Joins',
    image: '/story-assets/scene1.png',
    narrator:
      "It's your first day. You clone the repository. Three million lines of code. Thousands of commits. Hundreds of pull requests.",
    query: 'Where is authentication implemented?',
    aiResponse: {
      text: 'Authentication is implemented in app/auth/service.py — handles JWT tokens, OAuth2 flows, and session management.',
      success: true,
    },
    emotion: '😊',
    emotionText: 'The engineer smiles. AI found the code instantly.',
    mood: 'warm',
    moodColor: '#F5A623',
  },
  {
    id: 2,
    chapter: 'Chapter 2',
    title: 'Production Alert!',
    subtitle: 'A Real Engineering Problem',
    image: '/story-assets/scene2.png',
    alert: 'Login failures spiking 340% after latest deployment',
    narrator:
      'A production alert flashes red across every screen. Login failures after the latest deployment.',
    query: 'Why was Redis introduced into authentication?',
    aiResponse: {
      text: 'Found 14 code references in app/auth/cache.py... [No decision context available]',
      success: false,
    },
    silenceText: 'Silence. The AI finds code... but not the answer.',
    mood: 'alert',
    moodColor: '#FF6B6B',
  },
  {
    id: 3,
    chapter: 'Chapter 3',
    title: 'The Hunt Begins',
    subtitle: 'Searching for Lost Knowledge',
    image: '/story-assets/scene3.png',
    huntSteps: [
      { icon: 'git', text: 'Searching through old pull requests...' },
      { icon: 'commit', text: 'Reading vague commit messages ("fixed stuff")...' },
      { icon: 'slack', text: 'Digging through Slack threads and wikis...' },
      { icon: 'people', text: 'Asking senior engineers who might remember...' },
    ],
    dialogues: [
      { speaker: 'Senior Engineer', text: '"I think Alice knew."' },
      { speaker: 'Teammate', text: '"She left the company last year."' },
    ],
    punchline: 'The code survived. The knowledge didn\'t.',
    mood: 'somber',
    moodColor: '#9B59B6',
  },
  {
    id: 4,
    chapter: 'Chapter 4',
    title: 'Enter EMOS',
    subtitle: 'Engineering Memory Activated',
    image: '/story-assets/scene4.png',
    query: 'Why was Redis introduced into authentication?',
    emosResponse: {
      summary:
        'Redis was introduced in PR #128 to reduce authentication latency during peak traffic. The decision was made by Alice, reviewed by Bob, after database bottlenecks caused repeated login failures.',
      impact: 'This service now impacts Login, Sessions, and Payments.',
      risk: 'HIGH RISK (8.9/10)',
    },
    meta: {
      pr: '#128',
      author: 'Alice Chen',
      reviewer: 'Bob Martinez',
      services: ['Login', 'Sessions', 'Payments'],
    },
    mood: 'magic',
    moodColor: '#F5A623',
  },
  {
    id: 5,
    chapter: 'The End',
    title: 'EMOS',
    subtitle: 'Engineering Memory Operating System',
    image: '/story-assets/scene5.png',
    closingLines: [
      { text: 'AI can explain what your code does.', dim: true },
      { text: 'EMOS explains why your engineering decisions were made...', highlight: true },
      { text: '...who made them...', highlight: true },
      { text: '...how your systems evolved...', highlight: true },
      { text: '...and what will happen before you change them.', highlight: true },
    ],
    tagline:
      "Because great engineering isn't just written in code — it's written in decisions.",
    mood: 'epic',
    moodColor: '#F5A623',
  },
];

/* ─── Typewriter Hook ──────────────────────────────────── */
function useTypewriter(text, speed = 35, startDelay = 0, trigger = true) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!trigger) { setDisplayed(''); setDone(false); return; }
    setDisplayed(''); setDone(false);
    let i = 0;
    const timer = setTimeout(() => {
      const iv = setInterval(() => {
        i++;
        setDisplayed(text.slice(0, i));
        if (i >= text.length) { clearInterval(iv); setDone(true); }
      }, speed);
      return () => clearInterval(iv);
    }, startDelay);
    return () => clearTimeout(timer);
  }, [text, speed, startDelay, trigger]);

  return { displayed, done };
}

/* ─── Typing Text Sub-Component ─────────────────────────── */
function TypingText({ text, speed = 30, delay = 0, trigger = true }) {
  const { displayed, done } = useTypewriter(text, speed, delay, trigger);
  return (
    <span className="pixar-typing-text">
      {displayed}
      {!done && <span className="pixar-typing-cursor">▋</span>}
    </span>
  );
}

/* ─── Floating Particles Component ──────────────────────── */
function FloatingParticles({ count = 20, color = '#F5A623' }) {
  const particles = Array.from({ length: count }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: 2 + Math.random() * 4,
    duration: 3 + Math.random() * 5,
    delay: Math.random() * 3,
  }));

  return (
    <div className="pixar-floating-particles">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="pixar-particle"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
            background: color,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.8, 0.2],
            scale: [1, 1.5, 1],
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════
   MAIN COMPONENT
   ═══════════════════════════════════════════════════════════ */
export default function StoryScroll({ onEnterApp }) {
  const [activeScene, setActiveScene] = useState(0);
  const [scenePhase, setScenePhase] = useState(0);
  const mountRef = useRef(null);
  const scrollContainerRef = useRef(null);

  const scene = SCENES[activeScene];

  /* ─── 3D Background (subtle, Pixar-bokeh style) ──────── */
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const threeScene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      50, window.innerWidth / window.innerHeight, 0.1, 1000
    );
    camera.position.z = 30;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Soft bokeh-like spheres
    const spheres = [];
    const colors = [0xF5A623, 0xFF6B6B, 0x69F0AE, 0x4FC3F7, 0xFFD54F, 0xE040FB];
    for (let i = 0; i < 25; i++) {
      const geo = new THREE.SphereGeometry(0.3 + Math.random() * 1.2, 16, 16);
      const mat = new THREE.MeshBasicMaterial({
        color: colors[Math.floor(Math.random() * colors.length)],
        transparent: true,
        opacity: 0.06 + Math.random() * 0.08,
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(
        (Math.random() - 0.5) * 60,
        (Math.random() - 0.5) * 40,
        (Math.random() - 0.5) * 20 - 10
      );
      mesh.userData = {
        speedX: (Math.random() - 0.5) * 0.003,
        speedY: (Math.random() - 0.5) * 0.003,
        phase: Math.random() * Math.PI * 2,
      };
      threeScene.add(mesh);
      spheres.push(mesh);
    }

    let animId;
    const clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();

      spheres.forEach((s) => {
        s.position.x += s.userData.speedX;
        s.position.y += Math.sin(t * 0.5 + s.userData.phase) * 0.005;
        s.scale.setScalar(1 + Math.sin(t * 0.8 + s.userData.phase) * 0.15);
      });

      renderer.render(threeScene, camera);
    };
    animate();

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
      spheres.forEach((s) => { s.geometry.dispose(); s.material.dispose(); });
      renderer.dispose();
    };
  }, []);

  /* ─── Phase Timers ───────────────────────────────────── */
  useEffect(() => {
    setScenePhase(0);
    const t1 = setTimeout(() => setScenePhase(1), 500);
    const t2 = setTimeout(() => setScenePhase(2), 1400);
    const t3 = setTimeout(() => setScenePhase(3), 2400);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, [activeScene]);

  /* ─── Scroll Handler ─────────────────────────────────── */
  const handleScroll = useCallback(
    (e) => {
      const scrollTop = e.target.scrollTop;
      const height = e.target.clientHeight;
      const idx = Math.min(
        Math.floor((scrollTop + height * 0.4) / height),
        SCENES.length - 1
      );
      if (idx !== activeScene) setActiveScene(idx);
    },
    [activeScene]
  );

  /* ─── Launch Handler ─────────────────────────────────── */
  const handleLaunch = useCallback(() => {
    confetti({
      particleCount: 250,
      spread: 120,
      origin: { y: 0.45 },
      colors: ['#F5A623', '#FF6B6B', '#69F0AE', '#4FC3F7', '#FFD54F', '#E040FB'],
      shapes: ['star', 'circle'],
    });
    sessionStorage.setItem('emos_story_seen', 'true');
    if (onEnterApp) onEnterApp();
  }, [onEnterApp]);

  /* ─── Common spring configs ──────────────────────────── */
  const bouncy = { type: 'spring', stiffness: 200, damping: 20 };
  const gentleBounce = { type: 'spring', stiffness: 120, damping: 15 };

  /* ─── Icon Map ───────────────────────────────────────── */
  const huntIcons = {
    git: <GitPullRequest size={16} />,
    commit: <GitCommitHorizontal size={16} />,
    slack: <MessageSquare size={16} />,
    people: <Users size={16} />,
  };

  return (
    <motion.div
      className="pixar-story-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* 3D Bokeh Background */}
      <div ref={mountRef} className="pixar-webgl-bg" />

      {/* Warm gradient overlay */}
      <div className={`pixar-mood-overlay mood-${scene.mood}`} />

      {/* Header */}
      <header className="pixar-header">
        <div className="pixar-brand">
          <motion.div
            className="pixar-logo-icon"
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
          >
            🎬
          </motion.div>
          <div className="pixar-brand-text">
            <span className="pixar-brand-title">The Forgotten Engineer</span>
            <span className="pixar-brand-sub">An EMOS Animated Story</span>
          </div>
        </div>
        <div className="pixar-header-right">
          <div className="pixar-chapter-indicator">
            {SCENES.map((s, i) => (
              <motion.div
                key={s.id}
                className={`pixar-chapter-dot ${i === activeScene ? 'active' : ''} ${i < activeScene ? 'done' : ''}`}
                whileHover={{ scale: 1.3 }}
                onClick={() => {
                  scrollContainerRef.current?.scrollTo({
                    top: i * window.innerHeight,
                    behavior: 'smooth',
                  });
                }}
              />
            ))}
          </div>
          <button className="pixar-skip-btn" onClick={handleLaunch}>
            Skip <X size={13} />
          </button>
        </div>
      </header>

      {/* ── Scrollable Scenes ─────────────────────────────── */}
      <div
        ref={scrollContainerRef}
        className="pixar-scroll-container"
        onScroll={handleScroll}
      >

        {/* ═══ SCENE 1: Monday Morning ═══ */}
        <section className="pixar-scene" data-mood="warm">
          <div className="pixar-scene-inner">
            {/* Image Side */}
            <motion.div
              className="pixar-image-panel"
              initial={{ opacity: 0, scale: 1.05 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1.2, ease: 'easeOut' }}
              viewport={{ once: false, amount: 0.3 }}
            >
              <img src="/story-assets/scene1.png" alt="New engineer" className="pixar-scene-img" />
              <div className="pixar-img-glow warm" />
              <FloatingParticles count={15} color="#F5A623" />
            </motion.div>

            {/* Content Side */}
            <div className="pixar-content-panel">
              <motion.div
                className="pixar-chapter-badge"
                initial={{ opacity: 0, y: -10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={bouncy}
                viewport={{ once: false }}
              >
                <Play size={10} fill="currentColor" /> {SCENES[0].chapter}
              </motion.div>

              <motion.h2
                className="pixar-title"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ ...gentleBounce, delay: 0.15 }}
                viewport={{ once: false }}
              >
                {SCENES[0].title}
              </motion.h2>

              <motion.p
                className="pixar-subtitle"
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                viewport={{ once: false }}
              >
                {SCENES[0].subtitle}
              </motion.p>

              {/* Narrator */}
              <motion.div
                className="pixar-narrator"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                viewport={{ once: false }}
              >
                <div className="narrator-avatar">🎙️</div>
                <p>{SCENES[0].narrator}</p>
              </motion.div>

              {/* Stats */}
              <motion.div
                className="pixar-stats"
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.55 }}
                viewport={{ once: false }}
              >
                {[
                  { icon: <FileCode2 size={15} />, val: '3M+', label: 'Lines' },
                  { icon: <GitCommitHorizontal size={15} />, val: '2,847', label: 'Commits' },
                  { icon: <GitPullRequest size={15} />, val: '412', label: 'PRs' },
                ].map((s, i) => (
                  <motion.div
                    key={i}
                    className="pixar-stat-chip"
                    whileHover={{ scale: 1.06, y: -2 }}
                    transition={bouncy}
                  >
                    {s.icon}
                    <span className="stat-val">{s.val}</span>
                    <span className="stat-lbl">{s.label}</span>
                  </motion.div>
                ))}
              </motion.div>

              {/* Terminal */}
              <motion.div
                className="pixar-terminal"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                viewport={{ once: false }}
              >
                <div className="pixar-terminal-bar">
                  <span className="term-dot r" /><span className="term-dot y" /><span className="term-dot g" />
                  <span className="term-title"><Terminal size={11} /> AI Assistant</span>
                </div>
                <div className="pixar-terminal-body">
                  <div className="term-query">
                    <span className="term-prompt">❯</span>
                    {activeScene === 0 ? (
                      <TypingText text={SCENES[0].query} speed={28} delay={1200} trigger={activeScene === 0} />
                    ) : (
                      <span>{SCENES[0].query}</span>
                    )}
                  </div>
                  <motion.div
                    className="term-response success"
                    initial={{ opacity: 0, height: 0 }}
                    whileInView={scenePhase >= 3 ? { opacity: 1, height: 'auto' } : {}}
                    transition={{ delay: 0.2 }}
                    viewport={{ once: false }}
                  >
                    <CheckCircle2 size={14} className="resp-icon success" />
                    <span>{SCENES[0].aiResponse.text}</span>
                  </motion.div>
                </div>
              </motion.div>

              {/* Reaction */}
              <motion.div
                className="pixar-reaction"
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={scenePhase >= 3 ? { opacity: 1, scale: 1 } : {}}
                transition={bouncy}
                viewport={{ once: false }}
              >
                <span className="reaction-emoji">{SCENES[0].emotion}</span>
                <span>{SCENES[0].emotionText}</span>
              </motion.div>

              <div className="pixar-scroll-hint">
                <span>Scroll to continue the story</span>
                <ChevronDown size={14} className="pixar-bounce-icon" />
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SCENE 2: Production Alert ═══ */}
        <section className="pixar-scene" data-mood="alert">
          <div className="pixar-scene-inner">
            <motion.div
              className="pixar-image-panel"
              initial={{ opacity: 0, scale: 1.05 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1.2 }}
              viewport={{ once: false, amount: 0.3 }}
            >
              <img src="/story-assets/scene2.png" alt="Production alert" className="pixar-scene-img" />
              <div className="pixar-img-glow alert" />
              <FloatingParticles count={12} color="#FF6B6B" />
            </motion.div>

            <div className="pixar-content-panel">
              <motion.div className="pixar-chapter-badge alert" initial={{ opacity: 0, y: -10 }} whileInView={{ opacity: 1, y: 0 }} transition={bouncy} viewport={{ once: false }}>
                <AlertTriangle size={10} /> {SCENES[1].chapter}
              </motion.div>

              <motion.h2 className="pixar-title" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ ...gentleBounce, delay: 0.15 }} viewport={{ once: false }}>
                {SCENES[1].title}
              </motion.h2>

              <motion.p className="pixar-subtitle" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 0.3 }} viewport={{ once: false }}>
                {SCENES[1].subtitle}
              </motion.p>

              {/* Alert Banner */}
              <motion.div
                className="pixar-alert-banner"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                viewport={{ once: false }}
              >
                <motion.div
                  className="alert-icon-pulse"
                  animate={{ scale: [1, 1.3, 1], opacity: [0.7, 1, 0.7] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <AlertTriangle size={20} />
                </motion.div>
                <div className="alert-text">
                  <span className="alert-label">⚠ CRITICAL ALERT</span>
                  <span className="alert-desc">{SCENES[1].alert}</span>
                </div>
                <motion.div
                  animate={{ scaleY: [1, 1.3, 0.8, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Activity size={22} className="alert-chart" />
                </motion.div>
              </motion.div>

              {/* Narrator */}
              <motion.div className="pixar-narrator" initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} transition={{ delay: 0.55 }} viewport={{ once: false }}>
                <div className="narrator-avatar">🎙️</div>
                <p>{SCENES[1].narrator}</p>
              </motion.div>

              {/* Terminal */}
              <motion.div className="pixar-terminal alert" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }} viewport={{ once: false }}>
                <div className="pixar-terminal-bar">
                  <span className="term-dot r" /><span className="term-dot y" /><span className="term-dot g" />
                  <span className="term-title"><Terminal size={11} /> AI Assistant</span>
                </div>
                <div className="pixar-terminal-body">
                  <div className="term-query">
                    <span className="term-prompt">❯</span>
                    {activeScene === 1 ? (
                      <TypingText text={SCENES[1].query} speed={28} delay={1200} trigger={activeScene === 1} />
                    ) : (
                      <span>{SCENES[1].query}</span>
                    )}
                  </div>
                  <motion.div
                    className="term-response fail"
                    initial={{ opacity: 0, height: 0 }}
                    whileInView={scenePhase >= 3 ? { opacity: 1, height: 'auto' } : {}}
                    transition={{ delay: 0.2 }}
                    viewport={{ once: false }}
                  >
                    <Search size={14} className="resp-icon fail" />
                    <span>{SCENES[1].aiResponse.text}</span>
                  </motion.div>
                </div>
              </motion.div>

              {/* Silence */}
              <motion.div
                className="pixar-silence"
                initial={{ opacity: 0 }}
                whileInView={scenePhase >= 3 ? { opacity: 1 } : {}}
                transition={{ delay: 0.5 }}
                viewport={{ once: false }}
              >
                <span>😶</span> {SCENES[1].silenceText}
              </motion.div>

              <div className="pixar-scroll-hint">
                <span>Scroll to continue the story</span>
                <ChevronDown size={14} className="pixar-bounce-icon" />
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SCENE 3: The Hunt ═══ */}
        <section className="pixar-scene" data-mood="somber">
          <div className="pixar-scene-inner">
            <motion.div
              className="pixar-image-panel"
              initial={{ opacity: 0, scale: 1.05 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1.2 }}
              viewport={{ once: false, amount: 0.3 }}
            >
              <img src="/story-assets/scene3.png" alt="The hunt" className="pixar-scene-img" />
              <div className="pixar-img-glow somber" />
              <FloatingParticles count={10} color="#9B59B6" />
            </motion.div>

            <div className="pixar-content-panel">
              <motion.div className="pixar-chapter-badge somber" initial={{ opacity: 0, y: -10 }} whileInView={{ opacity: 1, y: 0 }} transition={bouncy} viewport={{ once: false }}>
                <Search size={10} /> {SCENES[2].chapter}
              </motion.div>

              <motion.h2 className="pixar-title" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ ...gentleBounce, delay: 0.15 }} viewport={{ once: false }}>
                {SCENES[2].title}
              </motion.h2>

              <motion.p className="pixar-subtitle" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 0.3 }} viewport={{ once: false }}>
                {SCENES[2].subtitle}
              </motion.p>

              {/* Animated hunt steps */}
              <div className="pixar-hunt-list">
                {SCENES[2].huntSteps.map((step, i) => (
                  <motion.div
                    key={i}
                    className="pixar-hunt-step"
                    initial={{ opacity: 0, x: -25 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ ...gentleBounce, delay: 0.35 + i * 0.2 }}
                    viewport={{ once: false }}
                    whileHover={{ x: 4, background: 'rgba(155, 89, 182, 0.12)' }}
                  >
                    <div className="hunt-icon">{huntIcons[step.icon]}</div>
                    <span>{step.text}</span>
                  </motion.div>
                ))}
              </div>

              {/* Dialogues */}
              <div className="pixar-dialogues">
                {SCENES[2].dialogues.map((d, i) => (
                  <motion.div
                    key={i}
                    className="pixar-dialogue"
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ ...gentleBounce, delay: 1.2 + i * 0.4 }}
                    viewport={{ once: false }}
                  >
                    <span className="dlg-speaker">{d.speaker}</span>
                    <span className="dlg-text">{d.text}</span>
                  </motion.div>
                ))}
              </div>

              {/* Punchline */}
              <motion.div
                className="pixar-punchline"
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ ...bouncy, delay: 2.0 }}
                viewport={{ once: false }}
              >
                <UserX size={22} />
                <h3>"{SCENES[2].punchline}"</h3>
              </motion.div>

              <div className="pixar-scroll-hint">
                <span>Scroll to continue the story</span>
                <ChevronDown size={14} className="pixar-bounce-icon" />
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SCENE 4: EMOS Reveal ═══ */}
        <section className="pixar-scene" data-mood="magic">
          <div className="pixar-scene-inner">
            <motion.div
              className="pixar-image-panel"
              initial={{ opacity: 0, scale: 1.05 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1.2 }}
              viewport={{ once: false, amount: 0.3 }}
            >
              <img src="/story-assets/scene4.png" alt="EMOS activated" className="pixar-scene-img" />
              <div className="pixar-img-glow magic" />
              <FloatingParticles count={25} color="#F5A623" />
            </motion.div>

            <div className="pixar-content-panel">
              <motion.div className="pixar-chapter-badge magic" initial={{ opacity: 0, y: -10 }} whileInView={{ opacity: 1, y: 0 }} transition={bouncy} viewport={{ once: false }}>
                <Sparkles size={10} /> {SCENES[3].chapter}
              </motion.div>

              <motion.h2 className="pixar-title magic" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ ...gentleBounce, delay: 0.15 }} viewport={{ once: false }}>
                ✨ {SCENES[3].title}
              </motion.h2>

              <motion.p className="pixar-subtitle" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 0.3 }} viewport={{ once: false }}>
                {SCENES[3].subtitle}
              </motion.p>

              {/* EMOS Terminal */}
              <motion.div
                className="pixar-terminal emos"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                viewport={{ once: false }}
              >
                <div className="pixar-terminal-bar emos-bar">
                  <span className="term-dot w" /><span className="term-dot w" /><span className="term-dot w" />
                  <span className="term-title emos-title"><Brain size={12} /> EMOS Decision Memory</span>
                </div>
                <div className="pixar-terminal-body">
                  <div className="term-query">
                    <span className="term-prompt emos-prompt">❯</span>
                    <span>{SCENES[3].query}</span>
                  </div>

                  <motion.div
                    className="emos-answer"
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    transition={{ delay: 0.9 }}
                    viewport={{ once: false }}
                  >
                    <p className="emos-summary">{SCENES[3].emosResponse.summary}</p>

                    <div className="emos-meta-grid">
                      <motion.div className="emos-meta-chip" whileHover={{ scale: 1.05 }} transition={bouncy}>
                        <GitPullRequest size={13} /> PR {SCENES[3].meta.pr}
                      </motion.div>
                      <motion.div className="emos-meta-chip" whileHover={{ scale: 1.05 }} transition={bouncy}>
                        <Users size={13} /> {SCENES[3].meta.author}
                      </motion.div>
                      <motion.div className="emos-meta-chip" whileHover={{ scale: 1.05 }} transition={bouncy}>
                        <Shield size={13} /> {SCENES[3].meta.reviewer}
                      </motion.div>
                      <motion.div className="emos-meta-chip danger" whileHover={{ scale: 1.05 }} transition={bouncy}>
                        <Zap size={13} /> {SCENES[3].emosResponse.risk}
                      </motion.div>
                    </div>

                    <div className="emos-services">
                      <span className="emos-svc-label">Impacted:</span>
                      {SCENES[3].meta.services.map((s, i) => (
                        <motion.span
                          key={s}
                          className="emos-svc-pill"
                          initial={{ opacity: 0, scale: 0.7 }}
                          whileInView={{ opacity: 1, scale: 1 }}
                          transition={{ ...bouncy, delay: 1.3 + i * 0.12 }}
                          viewport={{ once: false }}
                        >
                          {s}
                        </motion.span>
                      ))}
                    </div>
                  </motion.div>
                </div>
              </motion.div>

              <div className="pixar-scroll-hint">
                <span>Scroll to the finale</span>
                <ChevronDown size={14} className="pixar-bounce-icon" />
              </div>
            </div>
          </div>
        </section>

        {/* ═══ SCENE 5: Grand Finale ═══ */}
        <section className="pixar-scene finale" data-mood="epic">
          <div className="pixar-finale-inner">
            {/* Full-bleed background image */}
            <motion.div
              className="pixar-finale-bg"
              initial={{ opacity: 0, scale: 1.1 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 2.0 }}
              viewport={{ once: false, amount: 0.3 }}
            >
              <img src="/story-assets/scene5.png" alt="EMOS finale" className="pixar-scene-img finale-img" />
              <div className="pixar-finale-overlay" />
              <FloatingParticles count={30} color="#FFD54F" />
            </motion.div>

            <div className="pixar-finale-content">
              {/* Spinning logo ring */}
              <motion.div
                className="pixar-logo-ring"
                animate={{ rotate: 360 }}
                transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
              />

              <motion.h1
                className="pixar-finale-title"
                initial={{ opacity: 0, scale: 0.8, y: 30 }}
                whileInView={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ ...bouncy, delay: 0.3 }}
                viewport={{ once: false }}
              >
                EMOS
              </motion.h1>

              <motion.p
                className="pixar-finale-sub"
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
                viewport={{ once: false }}
              >
                Engineering Memory Operating System
              </motion.p>

              <div className="pixar-closing-lines">
                {SCENES[4].closingLines.map((line, i) => (
                  <motion.p
                    key={i}
                    className={`closing-line ${line.dim ? 'dim' : 'bright'}`}
                    initial={{ opacity: 0, x: -15 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.0 + i * 0.35 }}
                    viewport={{ once: false }}
                  >
                    {line.highlight && '→ '}{line.text}
                  </motion.p>
                ))}
              </div>

              <motion.div
                className="pixar-tagline-box"
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 3.0 }}
                viewport={{ once: false }}
              >
                <motion.div
                  animate={{ rotate: [0, 15, -15, 0], scale: [1, 1.2, 1] }}
                  transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                >
                  <Sparkles size={18} className="tagline-sparkle" />
                </motion.div>
                <p>"{SCENES[4].tagline}"</p>
              </motion.div>

              <motion.button
                className="pixar-cta-btn"
                onClick={handleLaunch}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ ...bouncy, delay: 3.4 }}
                viewport={{ once: false }}
                whileHover={{ scale: 1.06, boxShadow: '0 8px 40px rgba(245, 166, 35, 0.5)' }}
                whileTap={{ scale: 0.95 }}
              >
                <span>🚀 Launch EMOS Workspace</span>
                <ArrowRight size={18} />
              </motion.button>
            </div>
          </div>
        </section>

      </div>
    </motion.div>
  );
}
