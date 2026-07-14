import { NavLink } from 'react-router-dom';
import { LayoutGrid, BarChart2, Sparkles } from 'lucide-react';
import './Sidebar.css';

const NAV = [
  { to: '/',          icon: LayoutGrid, label: 'Overview' },
  { to: '/analytics', icon: BarChart2,  label: 'Analytics' },
  { to: '/ai',        icon: Sparkles,   label: 'Ask AI'    },
];

const Sidebar = () => (
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

    <div className="sidebar-footer">
      <div className="repo-pill">
        <span className="repo-dot" />
        <span className="text-xs" style={{ color: 'var(--text-3)' }}>repo_id&nbsp;=&nbsp;</span>
        <span className="text-xs" style={{ color: 'var(--text-1)', fontWeight: 500 }}>1</span>
      </div>
    </div>
  </aside>
);

export default Sidebar;
