import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutGrid, BarChart2, Sparkles, Sun, Moon } from 'lucide-react';
import './Sidebar.css';

const NAV = [
  { to: '/',          icon: LayoutGrid, label: 'Overview' },
  { to: '/analytics', icon: BarChart2,  label: 'Analytics' },
  { to: '/ai',        icon: Sparkles,   label: 'Ask AI'    },
];

const Sidebar = () => {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-logo">E</span>
        <span className="sidebar-name">EMOS</span>
      </div>

      <nav className="sidebar-nav" aria-label="Main navigation">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            <Icon size={15} strokeWidth={1.75} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--s-2)' }}>
        <div className="repo-pill" style={{ margin: 0 }}>
          <span className="repo-dot" />
          <span className="text-xs" style={{ color: 'var(--text-3)' }}>repo_id&nbsp;=&nbsp;</span>
          <span className="text-xs" style={{ color: 'var(--text-1)', fontWeight: 500 }}>1</span>
        </div>
        <button 
          className="btn btn-ghost btn-icon"
          onClick={() => setDarkMode(!darkMode)}
          title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          aria-label="Toggle Theme"
          style={{ width: '28px', height: '28px', padding: 0 }}
        >
          {darkMode ? <Sun size={14} /> : <Moon size={14} />}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
