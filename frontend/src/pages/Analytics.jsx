import { useState, useEffect } from 'react';
import { Users, Flame, Hash } from 'lucide-react';
import './Analytics.css';

const REPO_ID = 1;

const TABS = [
  { key: 'contributors', label: 'Contributors', icon: Users  },
  { key: 'hotspots',     label: 'Hotspots',     icon: Flame  },
];

/* Skeleton */
const SkeletonRows = ({ n = 6 }) => (
  <>
    {Array.from({ length: n }).map((_, i) => (
      <div key={i} className="table-row analytics-row">
        <div className="skeleton" style={{ height: 12, width: `${30 + Math.random() * 30}%`, borderRadius: 3 }} />
        <div className="skeleton" style={{ height: 12, width: '15%', borderRadius: 3 }} />
      </div>
    ))}
  </>
);

/* Contributor row */
const ContributorRow = ({ rank, username, contributions }) => (
  <div className="table-row analytics-row">
    <div className="analytics-rank text-xs">{rank}</div>
    <div className="analytics-name">
      <span className="avatar-circle">{username?.[0]?.toUpperCase() ?? '?'}</span>
      <span className="text-body" style={{ fontWeight: 500, color: 'var(--text-1)' }}>
        {username}
      </span>
    </div>
    <div className="analytics-meta">
      <span className="badge badge-neutral">
        {contributions ?? 0} commits
      </span>
    </div>
  </div>
);

/* Hotspot row */
const HotspotRow = ({ rank, path, count }) => {
  const filename = path?.split('/').pop() ?? path;
  const dir      = path?.includes('/') ? path.split('/').slice(0, -1).join('/') : '';
  return (
    <div className="table-row analytics-row">
      <div className="analytics-rank text-xs">{rank}</div>
      <div className="analytics-name" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 2 }}>
        <span style={{ fontWeight: 500, color: 'var(--text-1)', fontSize: 13 }}>{filename}</span>
        {dir && <span className="text-xs text-mono" style={{ color: 'var(--text-4)' }}>{dir}</span>}
      </div>
      <div className="analytics-meta">
        <span className="badge badge-neutral">{count ?? 0} changes</span>
      </div>
    </div>
  );
};

export default function Analytics() {
  const [tab,          setTab]          = useState('contributors');
  const [contributors, setContributors] = useState([]);
  const [hotspots,     setHotspots]     = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const [cRes, hRes] = await Promise.all([
          fetch(`/api/repositories/${REPO_ID}/contributors/top`),
          fetch(`/api/repositories/${REPO_ID}/files/hotspot`),
        ]);
        if (cRes.ok) setContributors(await cRes.json());
        if (hRes.ok) setHotspots(await hRes.json());
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const activeData = tab === 'contributors' ? contributors : hotspots;

  return (
    <div className="analytics-page animate-in">

      {/* Header */}
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="text-display">Analytics</h1>
          <p className="text-sm">Code ownership, activity, and file risk</p>
        </div>
      </div>

      {/* Tab strip */}
      <div className="tab-strip">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            className={`tab-btn${tab === key ? ' active' : ''}`}
            onClick={() => setTab(key)}
          >
            <Icon size={13} strokeWidth={1.75} />
            {label}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="card analytics-table">
        {/* Table header */}
        <div className="analytics-table-header">
          <div className="analytics-rank">
            <span className="text-xs" style={{ color: 'var(--text-4)' }}>
              <Hash size={11} />
            </span>
          </div>
          <div className="analytics-name text-xs" style={{ color: 'var(--text-4)' }}>
            {tab === 'contributors' ? 'Contributor' : 'File'}
          </div>
          <div className="analytics-meta text-xs" style={{ color: 'var(--text-4)' }}>
            {tab === 'contributors' ? 'Commits' : 'Changes'}
          </div>
        </div>

        {loading ? (
          <SkeletonRows />
        ) : error ? (
          <div className="empty-state">
            <p className="text-sm" style={{ color: 'var(--danger)' }}>Failed to load — {error}</p>
          </div>
        ) : activeData.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              {tab === 'contributors' ? <Users size={18} /> : <Flame size={18} />}
            </div>
            <p className="text-sm">No data available</p>
            <p className="text-xs">Run an ingestion to populate analytics</p>
          </div>
        ) : tab === 'contributors' ? (
          contributors.map((c, i) => (
            <ContributorRow
              key={c.username ?? i}
              rank={i + 1}
              username={c.username}
              contributions={c.contributions ?? c.commit_count}
            />
          ))
        ) : (
          hotspots.map((f, i) => (
            <HotspotRow
              key={f.path ?? i}
              rank={i + 1}
              path={f.path}
              count={f.modifications ?? f.commit_count}
            />
          ))
        )}
      </div>

    </div>
  );
}
