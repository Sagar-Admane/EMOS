import { useState, useEffect, useRef } from 'react';
import { GitBranch, Users, GitPullRequest, GitCommit, ExternalLink, Sparkles } from 'lucide-react';
import { motion } from 'motion/react';
import { animate } from 'animejs';
import { getApiUrl } from '../utils/api';
import MetricSphere3D from '../components/3d/MetricSphere3D';
import './Dashboard.css';

/* Stat cell with Anime.js number counter */
const StatCell = ({ icon: Icon, value, label }) => {
  const numRef = useRef(null);

  useEffect(() => {
    if (value != null && typeof value === 'number' && numRef.current) {
      animate(numRef.current, {
        innerHTML: [0, value],
        round: 1,
        ease: 'outExpo',
        duration: 1200
      });
    }
  }, [value]);

  return (
    <motion.div 
      className="dash-stat"
      whileHover={{ scale: 1.02, y: -2 }}
      transition={{ type: 'spring', stiffness: 350 }}
    >
      <div className="dash-stat-icon">
        <Icon size={14} strokeWidth={1.75} />
      </div>
      <div className="stat">
        <span className="stat-value" ref={numRef}>
          {value ?? '—'}
        </span>
        <span className="stat-label">{label}</span>
      </div>
    </motion.div>
  );
};

const SkeletonRow = () => (
  <div className="table-row activity-row">
    <div className="skeleton" style={{ height: 13, width: '60%', borderRadius: 3 }} />
    <div className="skeleton" style={{ height: 11, width: '20%', borderRadius: 3, marginLeft: 'auto' }} />
  </div>
);

export default function Dashboard({ activeRepoId }) {
  const [summary, setSummary]   = useState(null);
  const [loading, setLoading]   = useState(true);
  const [error,   setError]     = useState(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const r = await fetch(getApiUrl(`/api/repositories/${activeRepoId}/summary`));
        if (!r.ok) throw new Error(`${r.status}`);
        setSummary(await r.json());
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [activeRepoId]);

  return (
    <motion.div 
      className="dash"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Page header */}
      <div className="page-header">
        <div className="page-header-left">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <h1 className="text-display">Overview</h1>
            <span className="badge badge-neutral" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
              <Sparkles size={11} /> Monochrome 3D
            </span>
          </div>
          <p className="text-sm">
            {loading
              ? 'Loading repository…'
              : error
              ? 'Could not reach backend'
              : summary?.owner && summary?.repository_name
              ? `${summary.owner}/${summary.repository_name}`
              : (summary?.repository_name ?? `Repository ${activeRepoId}`)}
          </p>
        </div>
        {summary?.html_url && (
          <a
            href={summary.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary btn-sm"
          >
            <ExternalLink size={13} />
            GitHub
          </a>
        )}
      </div>

      {/* Hero 3D Nucleus + Stat Summary Container */}
      <div className="dash-hero-container" style={{ display: 'grid', gridTemplateColumns: 'minmax(180px, 220px) 1fr', gap: 20, marginBottom: 24, alignItems: 'center' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '16px 12px' }}>
          <MetricSphere3D 
            commits={summary?.total_commits || 0}
            prs={summary?.total_prs || 0}
            contributors={summary?.total_contributors || 0}
          />
          <span className="text-xs font-mono" style={{ color: 'var(--text-4)', marginTop: 4 }}>Monochrome Core</span>
        </div>

        {/* Stats row */}
        <section className="dash-stats-row card">
          <StatCell icon={GitCommit}      value={loading ? null : summary?.total_commits}      label="Commits" />
          <div className="dash-stat-divider" />
          <StatCell icon={Users}          value={loading ? null : summary?.total_contributors}  label="Contributors" />
          <div className="dash-stat-divider" />
          <StatCell icon={GitPullRequest} value={loading ? null : summary?.total_prs}           label="Pull Requests" />
          <div className="dash-stat-divider" />
          <StatCell icon={GitBranch}      value={loading ? null : (summary?.total_branches ?? 1)} label="Branches" />
        </section>
      </div>

      {/* Lower grid */}
      <div className="dash-grid">
        {/* Recent activity */}
        <section className="card dash-section">
          <div className="dash-section-header">
            <span className="text-heading">Recent activity</span>
          </div>
          <div className="dash-section-body">
            {loading ? (
              [1,2,3,4,5].map(n => <SkeletonRow key={n} />)
            ) : error ? (
              <div className="empty-state">
                <p className="text-sm" style={{ color: 'var(--text-3)' }}>
                  Backend unavailable — {error}
                </p>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">
                  <GitCommit size={18} />
                </div>
                <p className="text-sm">Activity feed will appear here</p>
                <p className="text-xs">Ingest commits to populate this section</p>
              </div>
            )}
          </div>
        </section>

        {/* Repository details */}
        <section className="card dash-section">
          <div className="dash-section-header">
            <span className="text-heading">Repository details</span>
          </div>
          <div className="dash-section-body">
            {loading ? (
              [1,2,3].map(n => (
                <div key={n} className="detail-row">
                  <div className="skeleton" style={{ height: 11, width: '40%', borderRadius: 3 }} />
                  <div className="skeleton" style={{ height: 11, width: '50%', borderRadius: 3 }} />
                </div>
              ))
            ) : (
              <dl className="detail-list">
                <div className="detail-row">
                  <dt className="text-xs">Full name</dt>
                  <dd className="text-xs" style={{ color: 'var(--text-2)', fontWeight: 500 }}>
                    {summary?.owner && summary?.repository_name
                      ? `${summary.owner}/${summary.repository_name}`
                      : (summary?.repository_name ?? '—')}
                  </dd>
                </div>
                <div className="detail-row">
                  <dt className="text-xs">Default branch</dt>
                  <dd>
                    <span className="badge badge-neutral">{summary?.default_branch ?? 'main'}</span>
                  </dd>
                </div>
                <div className="detail-row">
                  <dt className="text-xs">Status</dt>
                  <dd>
                    <span className="badge badge-neutral">
                      {error ? 'Unreachable' : 'Connected'}
                    </span>
                  </dd>
                </div>
              </dl>
            )}
          </div>
        </section>
      </div>
    </motion.div>
  );
}
