import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import AIAssistant from './pages/AIAssistant';
import './App.css';

function App() {
  return (
    <Router>
      <div className="layout">
        <Sidebar />
        <div className="layout-content">
          <Routes>
            {/* Standard scrollable pages */}
            <Route path="/" element={
              <div className="page-scroll"><Dashboard /></div>
            } />
            <Route path="/analytics" element={
              <div className="page-scroll"><Analytics /></div>
            } />
            {/* AI page gets its own full-height container — no outer scroll */}
            <Route path="/ai" element={
              <div className="ai-layout"><AIAssistant /></div>
            } />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
