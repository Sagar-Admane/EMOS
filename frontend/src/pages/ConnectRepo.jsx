import { useState, useEffect, useRef } from 'react';
import { GitFork, Trash2, RefreshCw, AlertCircle, Database, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import confetti from 'canvas-confetti';
import { getApiUrl } from '../utils/api';
import RepoGraph3D from '../components/3d/RepoGraph3D';
import './ConnectRepo.css';

const PHASES = [
  'Fetching repository metadata from GitHub',
  'Ingesting commits, branches & contributors',
  'Ingesting files and pull requests',
  'Fetching code content and chunking',
  'Building Qdrant vector embeddings',
  'Building Neo4j knowledge graph',
];

function IndexingOverlay({ repoName, onDismiss }) {
  const [phaseIdx, setPhaseIdx] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setPhaseIdx(prev => (prev + 1) % PHASES.length);
    }, 4500);
    return () => clearInterval(id);
  }, []);

  return (
    <motion.div 
      className="indexing-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="indexing-logo">EMOS MONOCHROME</div>
      <div className="indexing-spinner" />
      <div className="indexing-title">Indexing {repoName}</div>
      <div className="indexing-subtitle">
        We're analysing your repository and building the 3D knowledge graph.
        This can take a minute or two depending on the repository size.
      </div>

      <div className="indexing-phases">
        {PHASES.map((phase, i) => (
          <div
            key={phase}
            className={`indexing-phase-item${i === phaseIdx ? ' active' : ''}`}
          >
            <span className="indexing-phase-dot" />
            {phase}
          </div>
        ))}
      </div>

      <button
        className="btn btn-ghost text-xs indexing-dismiss"
        onClick={onDismiss}
      >
        Continue in background →
      </button>
    </motion.div>
  );
}

function StatusBadge({ status }) {
  const labels = {
    ready: 'Ready',
    indexing: 'Indexing…',
    pending: 'Pending',
    failed: 'Failed',
  };
  return (
    <span className={`status-badge ${status}`}>
      <span className="status-dot" />
      {labels[status] ?? status}
    </span>
  );
}

function RepoCard({ repo, onDelete }) {
  return (
    <motion.div 
      className="repo-card"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -2 }}
    >
      <div className="repo-card-left">
        <span className="repo-card-name">{repo.full_name}</span>
        <div className="repo-card-meta">
          <span>{repo.owner}</span>
          {repo.qdrant_collection && (
            <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              <Database size={11} />
              {repo.qdrant_collection}
            </span>
          )}
          {repo.indexed_at && (
            <span>indexed {new Date(repo.indexed_at).toLocaleDateString()}</span>
          )}
        </div>
      </div>
      <div className="repo-card-right">
        <StatusBadge status={repo.status} />
        <button
          className="btn btn-ghost btn-icon"
          title="Disconnect repository"
          onClick={() => onDelete(repo.repo_id)}
          style={{ width: 28, height: 28, padding: 0, color: 'var(--text-4)' }}
        >
          <Trash2 size={13} />
        </button>
      </div>
    </motion.div>
  );
}

export default function ConnectRepo({ onRepoConnected, repos = [], setRepos }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [indexingRepo, setIndexingRepo] = useState(null);
  const [showOverlay, setShowOverlay] = useState(false);
  const pollingRef = useRef(null);

  useEffect(() => {
    if (!indexingRepo) {
      clearInterval(pollingRef.current);
      return;
    }

    pollingRef.current = setInterval(async () => {
      try {
        const res = await fetch(getApiUrl(`/api/github/repos/${indexingRepo.repo_id}/status`));
        if (!res.ok) return;
        const data = await res.json();

        setRepos(prev =>
          prev.map(r =>
            r.repo_id === data.repo_id
              ? { ...r, status: data.status, indexed_at: data.indexed_at, error_message: data.error_message }
              : r
          )
        );

        if (data.status === 'ready' || data.status === 'failed') {
          if (data.status === 'ready') {
            confetti({
              particleCount: 100,
              spread: 70,
              origin: { y: 0.6 },
              colors: ['#ffffff', '#a1a1aa', '#52525b', '#000000']
            });
          }
          clearInterval(pollingRef.current);
          setIndexingRepo(null);
          setShowOverlay(false);
        }
      } catch {
        // ignore polling errors
      }
    }, 3000);

    return () => clearInterval(pollingRef.current);
  }, [indexingRepo, setRepos]);

  async function handleConnect(e) {
    e.preventDefault();
    setError('');
    const slug = input.trim();
    if (!slug) return;

    setLoading(true);
    try {
      const res = await fetch(getApiUrl('/api/github/connect'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_full_name: slug }),
      });

      if (!res.ok) {
        const body = await res.json();
        throw new Error(body.detail ?? 'Failed to connect repository.');
      }

      const data = await res.json();
      setInput('');
      
      if (onRepoConnected) {
        onRepoConnected(data.repo_id);
      }

      setRepos(prev => {
        const exists = prev.find(r => r.repo_id === data.repo_id);
        if (exists) {
          return prev.map(r =>
            r.repo_id === data.repo_id ? { ...r, status: 'indexing', indexed_at: null } : r
          );
        }
        return [
          {
            repo_id: data.repo_id,
            full_name: data.full_name,
            owner: data.full_name.split('/')[0],
            status: 'indexing',
            qdrant_collection: data.qdrant_collection,
            connected_at: data.connected_at,
            indexed_at: null,
          },
          ...prev,
        ];
      });

      setIndexingRepo({ repo_id: data.repo_id, full_name: data.full_name });
      setShowOverlay(true);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(repoId) {
    try {
      await fetch(getApiUrl(`/api/github/repos/${repoId}`), { method: 'DELETE' });
      setRepos(prev => prev.filter(r => r.repo_id !== repoId));
    } catch {
      setError('Failed to disconnect repository.');
    }
  }

  return (
    <>
      <AnimatePresence>
        {showOverlay && indexingRepo && (
          <IndexingOverlay
            repoName={indexingRepo.full_name}
            onDismiss={() => setShowOverlay(false)}
          />
        )}
      </AnimatePresence>

      <motion.div 
        className="connect-page"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
      >
        <div className="connect-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <h1>Connect Repository</h1>
            <span className="badge badge-neutral" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
              <Sparkles size={11} /> Monochrome Graph Ingestion
            </span>
          </div>
          <p>
            Connect a GitHub repository. EMOS will index the codebase into Qdrant vectors and build a Neo4j 3D knowledge graph.
          </p>
        </div>

        {/* 3D Knowledge Graph Constellation */}
        <RepoGraph3D repos={repos} />

        {/* Error banner */}
        {error && (
          <div className="error-banner">
            <AlertCircle size={14} style={{ flexShrink: 0, marginTop: 1 }} />
            <span>{error}</span>
          </div>
        )}

        {/* Connect form */}
        <form className="connect-form" onSubmit={handleConnect}>
          <input
            id="repo-input"
            className="input"
            placeholder="owner/repo-name"
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={loading}
            autoComplete="off"
            spellCheck={false}
          />
          <button
            id="connect-btn"
            className="btn btn-primary"
            type="submit"
            disabled={loading || !input.trim()}
            style={{ display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap' }}
          >
            {loading ? (
              <RefreshCw size={13} style={{ animation: 'spin 0.9s linear infinite' }} />
            ) : (
              <GitFork size={13} />
            )}
            {loading ? 'Connecting…' : 'Connect'}
          </button>
        </form>

        {/* Connected repos list */}
        <div className="repo-list-section">
          <h2>Connected Repositories</h2>
          {repos.length === 0 ? (
            <div className="empty-state">
              <GitFork size={28} />
              <p>No repositories connected yet.</p>
            </div>
          ) : (
            <div className="repo-list">
              <AnimatePresence>
                {repos.map(repo => (
                  <RepoCard
                    key={repo.repo_id}
                    repo={repo}
                    onDelete={handleDelete}
                  />
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </motion.div>
    </>
  );
}
