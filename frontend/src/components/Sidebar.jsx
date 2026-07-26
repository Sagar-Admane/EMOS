import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutGrid, BarChart2, Sparkles, Sun, Moon, GitBranch, Compass } from 'lucide-react';
import './Sidebar.css';

const NAV = [
  { to: '/',          icon: LayoutGrid, label: 'Overview' },
  { to: '/analytics', icon: BarChart2,  label: 'Analytics' },
  { to: '/connect',   icon: GitBranch,  label: 'Connect'   },
  { to: '/ai',        icon: Sparkles,   label: 'Ask AI'    },
];

const Sidebar = ({ activeRepoId, onSelectRepo, repos, onOpenStory }) => {
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
        {onOpenStory && (
          <button 
            className="nav-link" 
            onClick={onOpenStory} 
            style={{ background: 'transparent', width: '100%', cursor: 'pointer', textAlign: 'left' }}
            title="Replay 3D Intro Story"
          >
            <Compass size={15} strokeWidth={1.75} />
            <span>3D Story</span>
          </button>
        )}
      </nav>

      <div className="sidebar-footer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--s-2)' }}>
        <div className="repo-select-container">
          <span className="repo-dot" />
          <select 
            className="repo-select"
            value={activeRepoId || ''} 
            onChange={(e) => onSelectRepo(Number(e.target.value))}
            aria-label="Select Repository"
          >
            {repos.length === 0 ? (
              <option value="1">StockSync</option>
            ) : (
              repos.map(r => (
                <option key={r.repo_id} value={r.repo_id}>
                  {r.full_name.split('/').pop()}
                </option>
              ))
            )}
          </select>
        </div>
        <button 
          className="btn btn-ghost btn-icon"
          onClick={() => setDarkMode(!darkMode)}
          title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          aria-label="Toggle Theme"
          style={{ width: '28px', height: '28px', padding: 0, flexShrink: 0 }}
        >
          {darkMode ? <Sun size={14} /> : <Moon size={14} />}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
