import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import AIAssistant from './pages/AIAssistant';
import ConnectRepo from './pages/ConnectRepo';
import './App.css';

function App() {
  const [activeRepoId, setActiveRepoId] = useState(() => {
    const saved = localStorage.getItem('active_repo_id');
    return saved ? Number(saved) : 1;
  });
  const [repos, setRepos] = useState([]);

  const fetchRepos = useCallback(async () => {
    try {
      const res = await fetch('/api/github/repos');
      if (res.ok) {
        const data = await res.json();
        setRepos(data);
        
        // If activeRepoId is default (1) and we have other repos connected,
        // or if activeRepoId is not in the list, auto-select the first one available
        if (data.length > 0) {
          const exists = data.some(r => r.repo_id === activeRepoId);
          if (!exists) {
            setActiveRepoId(data[0].repo_id);
            localStorage.setItem('active_repo_id', data[0].repo_id);
          }
        }
      }
    } catch (err) {
      console.error("Failed to fetch repos:", err);
    }
  }, [activeRepoId]);

  useEffect(() => {
    fetchRepos();
    const interval = setInterval(fetchRepos, 5000);
    return () => clearInterval(interval);
  }, [fetchRepos]);

  const handleSelectRepo = (repoId) => {
    setActiveRepoId(repoId);
    localStorage.setItem('active_repo_id', repoId);
  };

  const handleNewRepoConnected = async (repoId) => {
    // Update local state first so select option renders immediately
    handleSelectRepo(repoId);
    await fetchRepos();
  };

  return (
    <Router>
      <div className="layout">
        <Sidebar activeRepoId={activeRepoId} onSelectRepo={handleSelectRepo} repos={repos} />
        <div className="layout-content">
          <Routes>
            {/* Standard scrollable pages */}
            <Route path="/" element={
              <div className="page-scroll">
                <Dashboard activeRepoId={activeRepoId} />
              </div>
            } />
            <Route path="/analytics" element={
              <div className="page-scroll">
                <Analytics activeRepoId={activeRepoId} />
              </div>
            } />
            <Route path="/connect" element={
              <div className="page-scroll">
                <ConnectRepo onRepoConnected={handleNewRepoConnected} repos={repos} setRepos={setRepos} />
              </div>
            } />
            {/* AI page gets its own full-height container — no outer scroll */}
            <Route path="/ai" element={
              <div className="ai-layout">
                <AIAssistant activeRepoId={activeRepoId} />
              </div>
            } />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
