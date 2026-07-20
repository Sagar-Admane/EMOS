import { useState, useEffect } from 'react';
import { GitBranch, Users, GitPullRequest, GitCommit, ExternalLink } from 'lucide-react';
import { getApiUrl } from '../utils/api';
import './Dashboard.css';

/* Thin stat cell — number + label only */
const StatCell = ({ icon: Icon, value, label }) => (
  <div className="dash-stat">
    <div className="dash-stat-icon">
      <Icon size={14} strokeWidth={1.75} />
    </div>
    <div className="stat">
      <span className="stat-value">{value ?? '—'}</span>
      <span className="stat-label">{label}</span>
    </div>
  </div>
);

/* Skeleton row */
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
    <div className="dash animate-in">

      {/* Page header */}
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="text-display">Overview</h1>
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
                <p className="text-sm" style={{ color: 'var(--danger)' }}>
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
                    <span className={`badge ${error ? 'badge-danger' : 'badge-success'}`}>
                      {error ? 'Unreachable' : 'Connected'}
                    </span>
                  </dd>
                </div>
              </dl>
            )}
          </div>
        </section>

      </div>
    </div>
  );
}
