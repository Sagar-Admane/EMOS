import { useState, useRef, useEffect } from 'react';
import { ArrowUp, Sparkles, RotateCcw } from 'lucide-react';
import { getApiUrl } from '../utils/api';
import './AIAssistant.css';


const SUGGESTIONS = [
  'Who are the top contributors to this repository?',
  'Which files change the most frequently?',
  'Summarize the architecture of this codebase.',
  'Who owns the authentication module?',
];

/* Individual message bubble */
/* Individual message bubble */
const Message = ({ role, text, metadata, isNew }) => {
  if (role === 'user') {
    return (
      <div className={`msg msg-user${isNew ? ' animate-in' : ''}`}>
        <p className="msg-text">{text}</p>
      </div>
    );
  }

  // Simple inline Markdown formatter to avoid raw markdown tags in text output
  const renderFormattedText = (rawText) => {
    if (!rawText) return null;
    const lines = rawText.split('\n');
    return lines.map((line, idx) => {
      // 1. Headers: e.g. "### Heading" or "## Heading" or "# Heading"
      const headerMatch = line.match(/^(#{1,6})\s+(.*)$/);
      if (headerMatch) {
        const level = headerMatch[1].length;
        const content = parseInlineTokens(headerMatch[2]);
        const Tag = `h${level}`;
        return <Tag key={idx} className={`md-h${level}`} style={{ margin: '8px 0 4px 0', fontWeight: 'bold' }}>{content}</Tag>;
      }

      // 2. Unordered lists: e.g. "- item" or "* item"
      const listMatch = line.match(/^([*\-–])\s+(.*)$/);
      if (listMatch) {
        const content = parseInlineTokens(listMatch[2]);
        return <li key={idx} className="md-li" style={{ marginLeft: '16px', listStyleType: 'disc' }}>{content}</li>;
      }

      // 3. Spacing
      if (line.trim() === '') {
        return <div key={idx} style={{ height: '8px' }} />;
      }

      // 4. Default paragraph
      return <p key={idx} className="md-p" style={{ margin: '4px 0' }}>{parseInlineTokens(line)}</p>;
    });
  };

  const parseInlineTokens = (lineText) => {
    if (!lineText) return '';
    // Match bold (**text**) or inline code (`code`)
    const parts = lineText.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} style={{ background: 'var(--bg-muted)', padding: '2px 4px', borderRadius: '4px', fontFamily: 'monospace' }}>{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  return (
    <div className={`msg msg-assistant${isNew ? ' animate-in' : ''}`}>
      <div className="ai-avatar" aria-hidden="true">
        <Sparkles size={13} strokeWidth={1.75} />
      </div>
      <div className="msg-body">
        <div className="msg-text" style={{ whiteSpace: 'pre-wrap' }}>
          {renderFormattedText(text)}
        </div>
        {metadata && (
          <div className="msg-meta">
            <span className="badge badge-neutral">{metadata.intent?.replace(/_/g, ' ')}</span>
            <span className="badge badge-neutral">{metadata.skill} skill</span>
            <span className="text-xs" style={{ color: 'var(--text-4)', marginLeft: 'auto' }}>
              {Math.round(metadata.time)}ms
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

/* Thinking indicator */
const Thinking = () => (
  <div className="msg msg-assistant animate-in">
    <div className="ai-avatar">
      <Sparkles size={13} strokeWidth={1.75} />
    </div>
    <div className="thinking-dots">
      <span /><span /><span />
    </div>
  </div>
);

const INITIAL = [
  { id: 0, role: 'assistant', text: 'Ask me anything about this repository — architecture, reviewers, ownership, hotspots, or recent changes.', isNew: false },
];

export default function AIAssistant({ activeRepoId }) {
  const [messages, setMessages] = useState(INITIAL);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const busyRef = useRef(false);

  // Keep busyRef in sync so send() always sees the latest value without
  // needing to be recreated on every busy change.
  useEffect(() => { busyRef.current = busy; }, [busy]);

  // Scroll to bottom — wrapped in a plain function, never returns a value.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, busy]);

  const send = async (text) => {
    if (!text.trim() || busyRef.current) return;
    setInput('');
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', text, isNew: true }]);
    setBusy(true);
    busyRef.current = true;

    try {
      const res = await fetch(getApiUrl('/api/ai/ask'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text, repo_id: activeRepoId }),
      });

      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();

      setMessages(prev => [...prev, {
        id: Date.now(),
        role: 'assistant',
        text: data.answer,
        isNew: true,
        metadata: {
          intent: data.intent,
          skill: data.skill_used,
          time: data.execution_time_ms,
        },
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        role: 'error',
        text: `Something went wrong — ${err.message}`,
        isNew: true,
      }]);
    } finally {
      setBusy(false);
      busyRef.current = false;
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    send(input);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  const reset = () => {
    setMessages(INITIAL);
    setInput('');
    inputRef.current?.focus();
  };

  const isEmpty = messages.length <= 1 && !busy;

  return (
    <div className="ai-page animate-in">

      {/* Header */}
      <div className="ai-header">
        <div>
          <h1 className="text-display">Ask AI</h1>
          <p className="text-sm">Engineering intelligence for your repository</p>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={reset} title="New conversation">
          <RotateCcw size={13} />
          New chat
        </button>
      </div>

      {/* Chat window */}
      <div className="ai-window card">

        {/* Message list */}
        <div className="ai-messages" role="log" aria-live="polite">
          {messages.map(msg => (
            msg.role === 'error' ? (
              <div key={msg.id} className="msg msg-error animate-in">
                <p className="text-sm">{msg.text}</p>
              </div>
            ) : (
              <Message key={msg.id} {...msg} />
            )
          ))}
          {busy && <Thinking />}
          <div ref={bottomRef} />
        </div>

        {/* Suggestion chips — show only when idle and no prior messages */}
        {isEmpty && (
          <div className="ai-suggestions">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                className="suggestion-chip"
                onClick={() => send(s)}
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input bar */}
        <form className="ai-input-bar" onSubmit={handleSubmit}>
          <textarea
            ref={inputRef}
            className="ai-textarea"
            placeholder="Ask a question about your codebase…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={busy}
            aria-label="Ask a question"
          />
          <button
            type="submit"
            className={`ai-send-btn${input.trim() && !busy ? ' active' : ''}`}
            disabled={!input.trim() || busy}
            aria-label="Send"
          >
            <ArrowUp size={15} strokeWidth={2} />
          </button>
        </form>
      </div>

    </div>
  );
}
