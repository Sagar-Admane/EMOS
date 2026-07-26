import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import AIAssistant from './pages/AIAssistant';
import ConnectRepo from './pages/ConnectRepo';
import Background3D from './components/3d/Background3D';
import StoryScroll from './components/story/StoryScroll';
import { getApiUrl } from './utils/api';
import './App.css';

function App() {
  const [activeRepoId, setActiveRepoId] = useState(() => {
    const saved = localStorage.getItem('active_repo_id');
    return saved ? Number(saved) : 1;
  });
  const [repos, setRepos] = useState([]);
  const [showStory, setShowStory] = useState(() => {
    return sessionStorage.getItem('emos_story_seen') !== 'true';
  });

  const fetchRepos = useCallback(async () => {
    try {
      const res = await fetch(getApiUrl('/api/github/repos'));
      if (res.ok) {
        const data = await res.json();
        setRepos(data);

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
    handleSelectRepo(repoId);
    await fetchRepos();
  };

  return (
    <Router>
      {showStory && (
        <StoryScroll onEnterApp={() => setShowStory(false)} />
      )}

      <div className="layout" style={{ position: 'relative', zIndex: 2 }}>
        <Background3D />
        <Sidebar 
          activeRepoId={activeRepoId} 
          onSelectRepo={handleSelectRepo} 
          repos={repos}
          onOpenStory={() => setShowStory(true)}
        />
        <div className="layout-content">
          <Routes>
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
