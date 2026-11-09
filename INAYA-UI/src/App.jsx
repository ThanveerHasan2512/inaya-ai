import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';

const INITIAL_MESSAGES = [{ id: 1, role: 'assistant', text: "Hello Thanveer, I am INAYA. How can I assist you today?", time: new Date() }];
const INITIAL_ACTIVITY = [{ id: 1, title: 'Interface initialized', detail: 'INAYA frontend is ready and connecting to backend', state: 'done', time: new Date() }];
const DEFAULT_SETTINGS = { intensity: 75, animations: true, sound: false, voice: false, speed: 1, appearance: 'midnight' };
const iconPaths = {
  grid: <><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></>,
  message: <><path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8z"/></>,
  activity: <><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></>,
  settings: <><circle cx="12" cy="12" r="3"/><path d="m19.4 15 .1.1 1.4 1.1-1.4 2.4-1.7-.7a8 8 0 0 1-1.7 1l-.3 1.8h-2.8l-.3-1.8a8 8 0 0 1-1.7-1l-1.7.7-1.4-2.4L7.3 15a8 8 0 0 1 0-2l-1.4-1.1 1.4-2.4 1.7.7a8 8 0 0 1 1.7-1l.3-1.8h2.8l.3 1.8a8 8 0 0 1 1.7 1l1.7-.7 1.4 2.4-1.4 1.1a8 8 0 0 1 0 2Z" transform="translate(-1 -1) scale(1.08)"/></>,
  mic: <><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0 0 14 0M12 17v5m-4 0h8"/></>,
  send: <><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></>,
  stop: <><rect x="5" y="5" width="14" height="14" rx="2"/></>,
  close: <><path d="m18 6-12 12M6 6l12 12"/></>,
  plus: <><path d="M12 5v14M5 12h14"/></>,
  chevron: <><path d="m9 18 6-6-6-6"/></>,
  check: <><path d="m5 12 4 4L19 6"/></>,
  clock: <><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></>,
  volume: <><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/></>,
  trash: <><path d="M3 6h18M8 6V4h8v2m-9 0 1 14h8l1-14M10 10v6m4-6v6"/></>,
  sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></>,
  shield: <><path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m9 12 2 2 4-4"/></>,
  spark: <><path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-2-5.8L4 11l6-2.2L12 3Z"/><path d="m19 14 1.1 2.9L23 18l-2.9 1.1L19 22l-1.1-2.9L15 18l2.9-1.1L19 14Z"/></>,
  terminal: <><path d="m4 17 6-6-6-6M12 19h8"/></>,
  cpu: <><rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 9h6v6H9zM9 1v4m6-4v4M9 19v4m6-4v4M1 9h4m-4 6h4m14-6h4m-4 6h4"/></>,
  moon: <><path d="M20.9 13A9 9 0 0 1 11 3.1 9 9 0 1 0 20.9 13Z"/></>,
  alert: <><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></>,
};

function Icon({ name, size = 18, className = '' }) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {iconPaths[name] || iconPaths.spark}
    </svg>
  );
}

function fmtTime(date) { return new Intl.DateTimeFormat([], { hour: '2-digit', minute: '2-digit' }).format(date); }
function fmtDate(date) { return new Intl.DateTimeFormat([], { weekday: 'short', month: 'short', day: 'numeric' }).format(date); }

function Orb({ status, animations, intensity, onClick }) {
  return (
    <button className={`orb-button ${animations ? '' : 'no-motion'}`} onClick={onClick} aria-label="Change assistant state" title="Click to cycle assistant state">
      <div className={`orb-scene state-${status.toLowerCase()}`} style={{ '--glow': `${intensity}%` }}>
        <div className="orb-grid"/><div className="orb-ring ring-one"/><div className="orb-ring ring-two"/><div className="orb-ring ring-three"/>
        <div className="orb-particles"><i/><i/><i/><i/><i/><i/><i/><i/></div>
        <div className="orb-core"><div className="orb-core-inner"><div className="core-glyph"><span/><span/><span/><span/><span/></div></div></div>
        <div className="orb-halo"/>
      </div>
    </button>
  );
}

function Waveform({ active }) {
  return (
    <div className={`waveform ${active ? 'wave-active' : ''}`} aria-label={active ? 'Audio activity' : 'Audio idle'}>
      {Array.from({ length: 31 }, (_, i) => <i key={i} style={{ '--i': i, '--h': `${8 + ((i * 17 + 11) % 25)}px` }}/>)}
    </div>
  );
}

function Toggle({ checked, onChange, label }) {
  return (
    <button type="button" className={`toggle ${checked ? 'on' : ''}`} role="switch" aria-checked={checked} aria-label={label} onClick={() => onChange(!checked)}>
      <span/>
    </button>
  );
}

function Modal({ title, onClose, children, wide = false }) {
  return (
    <div className="modal-backdrop" onMouseDown={e => e.target === e.currentTarget && onClose()}>
      <section className={`modal ${wide ? 'modal-wide' : ''}`} role="dialog" aria-modal="true" aria-label={title}>
        <header className="modal-head">
          <div>
            <div className="eyebrow">INAYA CONTROL</div>
            <h2>{title}</h2>
          </div>
          <button className="icon-btn" onClick={onClose} aria-label="Close modal"><Icon name="close"/></button>
        </header>
        {children}
      </section>
    </div>
  );
}

export default function App() {
  const [status, setStatus] = useState('IDLE');
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [activities, setActivities] = useState(INITIAL_ACTIVITY);
  const [draft, setDraft] = useState('');
  const [settings, setSettings] = useState(() => {
    try { return { ...DEFAULT_SETTINGS, ...JSON.parse(localStorage.getItem('inaya-settings') || '{}') }; }
    catch { return DEFAULT_SETTINGS; }
  });
  const [modal, setModal] = useState('');
  const [page, setPage] = useState('assistant');
  const [clock, setClock] = useState(new Date());
  const [listening, setListening] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [connection, setConnection] = useState(false);
  const [backendHealth, setBackendHealth] = useState(null);
  const [toast, setToast] = useState('');

  const inputRef = useRef(null);
  const recognitionRef = useRef(null);
  const activityId = useRef(2);
  const messageId = useRef(2);

  // Clock tick
  useEffect(() => {
    const id = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  // Save settings
  useEffect(() => {
    try { localStorage.setItem('inaya-settings', JSON.stringify(settings)); } catch {}
  }, [settings]);

  // Toast timeout
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(''), 2600);
    return () => clearTimeout(t);
  }, [toast]);

  const addActivity = useCallback((title, detail, state = 'done') => {
    setActivities(prev => [{ id: activityId.current++, title, detail, state, time: new Date() }, ...prev].slice(0, 25));
  }, []);

  // Health check polling
  const checkBackendHealth = useCallback(async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setConnection(true);
        setBackendHealth(data);
      } else {
        setConnection(false);
      }
    } catch {
      setConnection(false);
    }
  }, []);

  useEffect(() => {
    checkBackendHealth();
    const timer = setInterval(checkBackendHealth, 6000);
    return () => clearInterval(timer);
  }, [checkBackendHealth]);

  const speak = useCallback((text) => {
    if (!settings.voice) return;
    if (!('speechSynthesis' in window)) {
      setError('Speech synthesis is not supported in this browser.');
      setStatus('ERROR');
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = Number(settings.speed) || 1;
    utterance.onstart = () => setStatus('SPEAKING');
    utterance.onend = () => setStatus(s => s === 'SPEAKING' ? 'IDLE' : s);
    utterance.onerror = () => setStatus(s => s === 'SPEAKING' ? 'IDLE' : s);
    window.speechSynthesis.speak(utterance);
  }, [settings.voice, settings.speed]);

  const sendMessage = async (raw = draft) => {
    const text = raw.trim();
    if (!text) { setError('Type a message before sending.'); return; }
    setError('');
    setDraft('');
    setPage('assistant');

    const userMessage = { id: messageId.current++, role: 'user', text, time: new Date() };
    setMessages(prev => [...prev, userMessage]);
    addActivity('Command received', text, 'running');
    setStatus('THINKING');
    setProgress(35);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      if (res.ok) {
        const data = await res.json();
        const replyText = data.reply;
        setMessages(prev => [...prev, {
          id: messageId.current++,
          role: 'assistant',
          text: replyText,
          time: new Date(),
          provider: data.provider,
          tools_executed: data.tools_executed,
        }]);

        if (data.tools_executed && data.tools_executed.length > 0) {
          data.tools_executed.forEach(t => {
            const isSuccess = t.result?.success !== false;
            const detailMsg = t.result?.details || t.result?.message || t.result?.error || JSON.stringify(t.result || {});
            addActivity(
              `${isSuccess ? 'Executed' : 'Failed'}: ${t.result?.app_name || t.tool || t.name}`,
              detailMsg,
              isSuccess ? 'done' : 'error'
            );
          });
        }

        addActivity('Task completed', `Handled by ${data.provider} provider`, 'done');
        setStatus('IDLE');
        setProgress(100);
        setTimeout(() => setProgress(0), 700);

        if (settings.voice) speak(replyText);
      } else {
        let errorDetail = `HTTP ${res.status}`;
        try {
          const errData = await res.json();
          errorDetail = errData.detail || errData.error || errorDetail;
        } catch {}
        const errorReply = `Error from INAYA backend: ${errorDetail}`;
        setMessages(prev => [...prev, {
          id: messageId.current++,
          role: 'assistant',
          text: errorReply,
          time: new Date(),
          provider: 'system',
          error: true,
        }]);
        addActivity('Request failed', errorDetail, 'error');
        setError(errorDetail);
        setStatus('ERROR');
        setProgress(0);
      }
    } catch (err) {
      const errorMsg = `Could not reach INAYA backend at /api/chat. Please ensure the server is running (python run.py).`;
      setMessages(prev => [...prev, {
        id: messageId.current++,
        role: 'assistant',
        text: errorMsg,
        time: new Date(),
        provider: 'system',
        error: true,
      }]);
      addActivity('Connection Error', 'Backend server unreachable at /api/chat', 'error');
      setError('Backend offline. Run: python run.py from D:\\INAYA');
      setStatus('ERROR');
      setProgress(0);
    }
  };

  const clearChat = () => {
    setMessages([{ id: messageId.current++, role: 'assistant', text: 'Conversation cleared. Hello Thanveer — how can I help?', time: new Date() }]);
    setError('');
    addActivity('Conversation cleared', 'Local chat history reset', 'done');
    setToast('Conversation cleared');
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    setListening(false);
    recognitionRef.current?.stop?.();
    setStatus('IDLE');
    setProgress(0);
    addActivity('Interaction stopped', 'Speech synthesis and processing stopped', 'done');
    setToast('Stopped');
  };

  const startVoiceTest = () => {
    if (!('speechSynthesis' in window)) {
      setError('Speech synthesis is not supported by this browser.');
      setStatus('ERROR');
      return;
    }
    setError('');
    setSettings(s => ({ ...s, voice: true }));
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance("Hello Thanveer. I am INAYA. Voice output is functioning properly.");
    u.rate = settings.speed;
    u.onstart = () => setStatus('SPEAKING');
    u.onend = () => setStatus('IDLE');
    u.onerror = () => { setStatus('ERROR'); setError('The browser could not play speech. Check audio settings.'); };
    window.speechSynthesis.speak(u);
    addActivity('Voice test started', 'Browser speech synthesis', 'done');
  };

  const toggleMic = () => {
    if (listening) {
      recognitionRef.current?.stop?.();
      setListening(false);
      setStatus('IDLE');
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Microphone dictation is unavailable in this browser. Try Chrome or Edge.');
      setStatus('ERROR');
      addActivity('Microphone unavailable', 'SpeechRecognition not supported in browser', 'error');
      return;
    }
    try {
      const recognition = new SpeechRecognition();
      recognition.lang = navigator.language || 'en-US';
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.onstart = () => {
        setListening(true);
        setStatus('LISTENING');
        setError('');
        addActivity('Microphone enabled', 'Dictation active', 'done');
      };
      recognition.onresult = event => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setDraft(transcript);
      };
      recognition.onerror = event => {
        setError(event.error === 'not-allowed' ? 'Microphone permission denied.' : `Microphone error: ${event.error}`);
        setListening(false);
        setStatus('ERROR');
        addActivity('Microphone error', event.error, 'error');
      };
      recognition.onend = () => {
        setListening(false);
        setStatus(s => s === 'LISTENING' ? 'IDLE' : s);
      };
      recognitionRef.current = recognition;
      recognition.start();
    } catch {
      setError('Could not start microphone dictation. Check permissions.');
      setStatus('ERROR');
    }
  };

  const runQuickAction = (action) => {
    if (action === 'ask') { setPage('assistant'); inputRef.current?.focus(); setToast('Chat is ready'); }
    if (action === 'notepad') sendMessage('Open Notepad');
    if (action === 'calc') sendMessage('Open Calculator');
    if (action === 'explorer') sendMessage('Open File Explorer');
    if (action === 'vscode') sendMessage('Open VS Code');
    if (action === 'chrome') sendMessage('Open Chrome');
    if (action === 'edge') sendMessage('Open Edge');
    if (action === 'cmd') sendMessage('Open Command Prompt');
    if (action === 'status') { setModal('status'); }
    if (action === 'settings') { setModal('settings'); }
    if (action === 'voice') startVoiceTest();
    if (action === 'clear') clearChat();
  };

  const changePage = (next) => {
    setPage(next);
    if (next === 'assistant') setTimeout(() => inputRef.current?.focus(), 40);
  };

  const statusLabel = useMemo(() => ({
    IDLE: 'Ready when you are',
    LISTENING: 'Listening to your voice',
    THINKING: 'Processing request with INAYA Brain',
    SPEAKING: 'Speaking response',
    EXECUTING: 'Executing Windows action',
    ERROR: 'Needs your attention',
  }[status] || 'Ready when you are'), [status]);

  return (
    <div className={`app theme-${settings.appearance} ${settings.animations ? '' : 'motion-off'}`} style={{ '--intensity': settings.intensity / 100 }}>
      <div className="ambient ambient-a"/><div className="ambient ambient-b"/><div className="noise"/>
      
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><span/><span/><span/><span/></div>
          <div className="brand-copy"><strong>INAYA</strong><span>PERSONAL INTELLIGENCE</span></div>
        </div>
        <div className="topbar-center">
          <span className={`online-dot ${connection ? '' : 'offline'}`}/>
          <span>{connection ? 'BACKEND ONLINE' : 'BACKEND OFFLINE'}</span>
          <i/>
          <span className="demo-pill">{connection ? (backendHealth?.active_provider ? backendHealth.active_provider.toUpperCase() : 'LOCAL') : 'OFFLINE MODE'}</span>
        </div>
        <div className="topbar-right">
          <div className="clock-block">
            <strong>{clock.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}</strong>
            <span>{fmtDate(clock)}</span>
          </div>
          <button className="icon-btn" title="Settings" aria-label="Settings" onClick={() => setModal('settings')}><Icon name="settings"/></button>
          <button className="window-btn close-window" title="Close interface" aria-label="Close" onClick={() => setModal('close')}><Icon name="close" size={15}/></button>
        </div>
      </header>

      <div className="workspace">
        <aside className="sidebar glass-panel">
          <div className="side-label">WORKSPACE</div>
          <nav className="nav-list">
            <button className={`nav-item ${page === 'assistant' ? 'selected' : ''}`} onClick={() => changePage('assistant')}><Icon name="grid"/><span>Assistant</span><span className="nav-shortcut">01</span></button>
            <button className={`nav-item ${page === 'activity' ? 'selected' : ''}`} onClick={() => changePage('activity')}><Icon name="activity"/><span>Live activity</span><span className="nav-count">{activities.length}</span></button>
            <button className={`nav-item ${page === 'history' ? 'selected' : ''}`} onClick={() => changePage('history')}><Icon name="clock"/><span>Task history</span></button>
          </nav>
          
          <div className="side-separator"/>
          <div className="side-label">QUICK ACTIONS</div>
          <div className="quick-nav">
            <button onClick={() => runQuickAction('notepad')}><span className="quick-icon cyan"><Icon name="terminal" size={16}/></span><span>Notepad</span><Icon name="chevron" size={15}/></button>
            <button onClick={() => runQuickAction('calc')}><span className="quick-icon blue"><Icon name="cpu" size={16}/></span><span>Calculator</span><Icon name="chevron" size={15}/></button>
            <button onClick={() => runQuickAction('explorer')}><span className="quick-icon purple"><Icon name="grid" size={16}/></span><span>File Explorer</span><Icon name="chevron" size={15}/></button>
            <button onClick={() => runQuickAction('vscode')}><span className="quick-icon cyan"><Icon name="spark" size={16}/></span><span>VS Code</span><Icon name="chevron" size={15}/></button>
            <button onClick={() => runQuickAction('chrome')}><span className="quick-icon blue"><Icon name="sun" size={16}/></span><span>Chrome</span><Icon name="chevron" size={15}/></button>
            <button onClick={() => runQuickAction('status')}><span className="quick-icon purple"><Icon name="activity" size={16}/></span><span>System Telemetry</span><Icon name="chevron" size={15}/></button>
          </div>

          <div className="sidebar-spacer"/>
          <div className="privacy-card">
            <div className="privacy-icon"><Icon name="shield" size={17}/></div>
            <div>
              <strong>Secure D:\INAYA</strong>
              <p>Controlled Windows Automation &amp; Local Execution.</p>
            </div>
            <span className="privacy-dot"/>
          </div>
          <button className="profile-row" onClick={() => setModal('settings')}>
            <div className="avatar">T</div>
            <div className="profile-text"><strong>{backendHealth?.user_name || 'Thanveer'}</strong><span>Owner</span></div>
            <Icon name="settings" size={16}/>
          </button>
        </aside>

        <main className="main-content">
          {page === 'assistant' && (
            <>
              <div className="main-heading">
                <div>
                  <div className="eyebrow"><span className="eyebrow-line"/> INAYA CORE INTELLIGENCE <span className="eyebrow-line"/></div>
                  <h1>Intelligence, <em>in motion.</em></h1>
                  <p>Your futuristic personal assistant on Windows.</p>
                </div>
                <div className="session-chip">
                  <span className={`session-dot ${connection ? 'online' : 'offline'}`}/>
                  <div>
                    <span>ENGINE STATUS</span>
                    <strong>{connection ? `${backendHealth?.active_provider?.toUpperCase() || 'LOCAL'} ACTIVE` : 'BACKEND OFFLINE'}</strong>
                  </div>
                </div>
              </div>

              <section className="hero-orb">
                <div className="orb-top-label"><span className="tiny-spark">✳</span> ARC-REACTOR NEURAL CORE <span className="orb-label-line"/></div>
                <Orb
                  status={status}
                  animations={settings.animations}
                  intensity={settings.intensity}
                  onClick={() => {
                    const states = ['IDLE', 'LISTENING', 'THINKING', 'SPEAKING'];
                    const next = states[(states.indexOf(status) + 1) % states.length];
                    if (next === 'SPEAKING') startVoiceTest();
                    else if (next === 'LISTENING') toggleMic();
                    else setStatus(next);
                  }}
                />
                <div className="hero-status">
                  <span className={`status-indicator status-${status.toLowerCase()}`}/>
                  <span>{statusLabel}</span>
                  <span className="status-divider">/</span>
                  <span className="status-mono">{status}</span>
                </div>
                <Waveform active={['LISTENING', 'THINKING', 'SPEAKING', 'EXECUTING'].includes(status)}/>
                <div className="hero-prompt">
                  {status === 'IDLE' ? <>Hello <span>{backendHealth?.user_name || 'Thanveer'}.</span><br/>How can I assist you today?</> :
                   status === 'LISTENING' ? <>I'm listening<span>.</span><br/>Go ahead, speak clearly.</> :
                   status === 'THINKING' ? <>Processing with INAYA Brain<span>.</span><br/>Executing verified plan.</> :
                   status === 'SPEAKING' ? <>Here's what I have<span>.</span><br/>Speaking response now.</> :
                   status === 'ERROR' ? <>Attention required<span>.</span><br/>Check system notice.</> :
                   <>Executing Windows Action<span>.</span><br/>Verified safety policy.</>}
                </div>
                <div className="orb-footnote">
                  <span>CORE V.1.0</span>
                  <span className="footnote-dot"/>
                  <span>D:\INAYA ROOT</span>
                  <span className="footnote-dot"/>
                  <span>LOCAL-FIRST</span>
                </div>
              </section>

              <section className="chat-panel glass-panel">
                <div className="chat-head">
                  <div className="chat-title">
                    <div className="chat-title-icon"><Icon name="message" size={17}/></div>
                    <div>
                      <strong>Conversation</strong>
                      <span>{messages.length} messages · {connection ? 'FastAPI pipeline' : 'offline fallback'}</span>
                    </div>
                  </div>
                  <div className="chat-tools">
                    <span className="demo-pill">{connection ? (backendHealth?.active_provider ? backendHealth.active_provider.toUpperCase() : 'LOCAL') : 'OFFLINE'}</span>
                    <button className="icon-btn small" title="Clear conversation" aria-label="Clear conversation" onClick={clearChat}><Icon name="trash" size={16}/></button>
                  </div>
                </div>

                <div className="messages" aria-live="polite">
                  {messages.slice(-7).map(msg => (
                    <div className={`message ${msg.role}`} key={msg.id}>
                      <div className={`message-avatar ${msg.role === 'assistant' ? 'ai-avatar' : ''}`}>
                        {msg.role === 'assistant' ? <span className="mini-logo">✳</span> : 'T'}
                      </div>
                      <div className="message-content">
                        <div className="message-meta">
                          <strong>{msg.role === 'assistant' ? 'INAYA' : 'THANVEER'}</strong>
                          <span>{fmtTime(msg.time)}</span>
                          {msg.provider && <span className="message-demo">{msg.provider.toUpperCase()}</span>}
                        </div>
                        <p style={{ whiteSpace: 'pre-line' }}>{msg.text}</p>
                        {msg.tools_executed && msg.tools_executed.length > 0 && (
                          <div style={{ marginTop: '0.6rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                            {msg.tools_executed.map((t, idx) => {
                              const isSuccess = t.result?.success !== false;
                              return (
                                <div
                                  key={idx}
                                  style={{
                                    fontSize: '0.82rem',
                                    padding: '0.45rem 0.65rem',
                                    background: isSuccess ? 'rgba(0, 243, 255, 0.08)' : 'rgba(255, 80, 80, 0.1)',
                                    borderRadius: '6px',
                                    border: isSuccess ? '1px solid rgba(0, 243, 255, 0.25)' : '1px solid rgba(255, 80, 80, 0.3)',
                                    color: isSuccess ? '#e0f7fa' : '#ffcdd2',
                                  }}
                                >
                                  <strong>{isSuccess ? '✓ Action Executed' : '✗ Action Blocked / Failed'}:</strong>{' '}
                                  <span>{t.result?.details || t.result?.message || t.result?.error || t.tool || t.name}</span>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {status === 'THINKING' && (
                    <div className="message assistant">
                      <div className="message-avatar ai-avatar"><span className="mini-logo">✳</span></div>
                      <div className="message-content">
                        <div className="message-meta"><strong>INAYA</strong><span>now</span></div>
                        <div className="typing"><i/><i/><i/><span>Processing request via INAYA Brain</span></div>
                      </div>
                    </div>
                  )}
                </div>

                {error && (
                  <div className="inline-error">
                    <Icon name="alert" size={15}/>
                    <span>{error}</span>
                    <button onClick={() => setError('')} aria-label="Dismiss error"><Icon name="close" size={14}/></button>
                  </div>
                )}

                <form className="composer" onSubmit={e => { e.preventDefault(); sendMessage(); }}>
                  <input
                    ref={inputRef}
                    value={draft}
                    onChange={e => setDraft(e.target.value)}
                    placeholder="Message INAYA... (e.g., 'Open Notepad', 'System status', 'Open Calculator')"
                    aria-label="Message INAYA"
                  />
                  <button
                    type="button"
                    className={`composer-tool ${listening ? 'recording' : ''}`}
                    onClick={toggleMic}
                    title={listening ? 'Stop microphone' : 'Start microphone dictation'}
                    aria-label="Toggle microphone"
                  >
                    <Icon name="mic" size={18}/>
                  </button>
                  <button
                    type="button"
                    className="composer-tool stop-tool"
                    onClick={stopSpeaking}
                    title="Stop speaking"
                    aria-label="Stop speaking"
                  >
                    <Icon name="stop" size={16}/>
                  </button>
                  <button type="submit" className="send-btn" aria-label="Send message" disabled={!draft.trim()}>
                    <Icon name="send" size={17}/>
                  </button>
                </form>

                <div className="composer-foot">
                  <span><Icon name="shield" size={12}/> Safe Windows execution registry active</span>
                  <span>ENTER TO SEND <kbd>↵</kbd></span>
                </div>
              </section>

              <section className="quick-actions-section">
                <div className="section-heading">
                  <div>
                    <div className="eyebrow">COMMAND SHORTCUTS</div>
                    <h2>Quick Actions</h2>
                  </div>
                  <span className="section-caption">VERIFIED DESKTOP CAPABILITIES</span>
                </div>
                <div className="action-grid">
                  <button className="action-card" onClick={() => runQuickAction('notepad')}>
                    <div className="action-icon icon-cyan"><Icon name="terminal" size={19}/></div>
                    <div><strong>Open Notepad</strong><span>Launch text editor</span></div>
                    <Icon name="chevron" size={16} className="action-arrow"/>
                  </button>
                  <button className="action-card" onClick={() => runQuickAction('calc')}>
                    <div className="action-icon icon-blue"><Icon name="cpu" size={19}/></div>
                    <div><strong>Open Calculator</strong><span>Launch Windows calc</span></div>
                    <Icon name="chevron" size={16} className="action-arrow"/>
                  </button>
                  <button className="action-card" onClick={() => runQuickAction('explorer')}>
                    <div className="action-icon icon-purple"><Icon name="grid" size={19}/></div>
                    <div><strong>File Explorer</strong><span>Browse files</span></div>
                    <Icon name="chevron" size={16} className="action-arrow"/>
                  </button>
                  <button className="action-card" onClick={() => runQuickAction('vscode')}>
                    <div className="action-icon icon-cyan"><Icon name="spark" size={19}/></div>
                    <div><strong>Open VS Code</strong><span>Launch code editor</span></div>
                    <Icon name="chevron" size={16} className="action-arrow"/>
                  </button>
                  <button className="action-card" onClick={() => runQuickAction('chrome')}>
                    <div className="action-icon icon-blue"><Icon name="sun" size={19}/></div>
                    <div><strong>Open Chrome</strong><span>Web browser</span></div>
                    <Icon name="chevron" size={16} className="action-arrow"/>
                  </button>
                  <button className="action-card" onClick={() => runQuickAction('status')}>
                    <div className="action-icon icon-purple"><Icon name="activity" size={19}/></div>
                    <div><strong>System Telemetry</strong><span>Live CPU, RAM &amp; Disk</span></div>
                    <Icon name="chevron" size={16} className="action-arrow"/>
                  </button>
                </div>
              </section>
            </>
          )}

          {page === 'activity' && (
            <section className="page-card glass-panel">
              <div className="page-title-row">
                <div>
                  <div className="eyebrow">SYSTEM MONITOR</div>
                  <h1>Live <em>Activity.</em></h1>
                  <p>Every tool and command verified and timestamped.</p>
                </div>
                <span className="demo-pill">{connection ? 'BACKEND LOGS' : 'LOCAL LOGS'}</span>
              </div>
              <div className="progress-card">
                <div className="progress-top">
                  <span>Current Task Progress</span>
                  <strong>{progress}%</strong>
                </div>
                <div className="progress-track"><i style={{ width: `${progress}%` }}/></div>
                <p>{progress ? 'Executing requested action...' : 'No active tasks. INAYA is standing by.'}</p>
              </div>
              <div className="activity-list full-activity">
                {activities.map(a => (
                  <div className="activity-row" key={a.id}>
                    <div className={`activity-status ${a.state}`}>
                      <Icon name={a.state === 'error' ? 'close' : a.state === 'running' ? 'clock' : 'check'} size={14}/>
                    </div>
                    <div className="activity-copy">
                      <strong>{a.title}</strong>
                      <p>{a.detail}</p>
                    </div>
                    <time>{fmtTime(a.time)}</time>
                  </div>
                ))}
              </div>
            </section>
          )}

          {page === 'history' && (
            <section className="page-card glass-panel">
              <div className="page-title-row">
                <div>
                  <div className="eyebrow">SESSION HISTORY</div>
                  <h1>Recent <em>Interactions.</em></h1>
                  <p>Interactions from this local session.</p>
                </div>
                <Icon name="clock" size={25} className="muted-icon"/>
              </div>
              <div className="history-list">
                {activities.map(a => (
                  <div className="history-item" key={a.id}>
                    <div className="history-date"><span>{fmtTime(a.time)}</span><i/></div>
                    <div className="history-card">
                      <strong>{a.title}</strong>
                      <p>{a.detail}</p>
                      <span className={`history-state ${a.state}`}>{a.state.toUpperCase()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </main>

        <aside className="right-panel">
          <div className="right-heading">
            <div>
              <div className="eyebrow">SYSTEM OVERVIEW</div>
              <h2>At a glance</h2>
            </div>
            <span className="live-tag"><i/> LIVE</span>
          </div>

          <section className="status-card glass-panel">
            <div className="panel-title"><span>ASSISTANT STATUS</span><Icon name="activity" size={16}/></div>
            <div className="status-large">
              <span className={`status-indicator status-${status.toLowerCase()}`}/>
              <strong>{status}</strong>
            </div>
            <p>{statusLabel}</p>
            <div className="status-divider-line"/>
            <div className="status-metrics">
              <div>
                <span>AI PROVIDER</span>
                <strong>{backendHealth?.active_provider ? backendHealth.active_provider.toUpperCase() : 'LOCAL'}</strong>
              </div>
              <div>
                <span>SERVER</span>
                <strong className={connection ? 'text-cyan' : ''}>{connection ? '127.0.0.1:8000' : 'Offline'}</strong>
              </div>
            </div>
          </section>

          <section className="status-card glass-panel">
            <div className="panel-title"><span>HARDWARE TELEMETRY</span><Icon name="cpu" size={16}/></div>
            <div className="status-metrics" style={{ gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div>
                <span>CPU USAGE</span>
                <strong>{backendHealth?.system?.cpu_usage !== undefined ? `${backendHealth.system.cpu_usage}%` : '--'}</strong>
              </div>
              <div>
                <span>RAM USAGE</span>
                <strong>{backendHealth?.system?.ram_usage !== undefined ? `${backendHealth.system.ram_usage}%` : '--'}</strong>
              </div>
              <div>
                <span>D: FREE SPACE</span>
                <strong className="text-cyan">{backendHealth?.system?.d_drive_free_gb !== undefined ? `${backendHealth.system.d_drive_free_gb} GB` : '--'}</strong>
              </div>
              <div>
                <span>UPTIME</span>
                <strong>{backendHealth?.system?.uptime || '--'}</strong>
              </div>
            </div>
          </section>

          <section className="activity-card glass-panel">
            <div className="panel-title">
              <span>LIVE ACTIVITY</span>
              <button className="text-button" onClick={() => changePage('activity')}>View all <Icon name="chevron" size={13}/></button>
            </div>
            <div className="activity-list">
              {activities.slice(0, 5).map(a => (
                <div className="activity-item" key={a.id}>
                  <div className={`activity-dot ${a.state}`}>
                    {a.state === 'error' ? <Icon name="close" size={10}/> : a.state === 'running' ? <Icon name="clock" size={10}/> : <Icon name="check" size={10}/>}
                  </div>
                  <div className="activity-item-copy">
                    <strong>{a.title}</strong>
                    <span>{a.detail}</span>
                    <time>{fmtTime(a.time)}</time>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <div className="right-footer">
            <span>INAYA SYSTEM · v1.0</span>
            <span><i/> D:\INAYA</span>
          </div>
        </aside>
      </div>

      {modal === 'settings' && (
        <Modal title="Interface Settings" onClose={() => setModal('')}>
          <div className="settings-content">
            <div className="settings-group">
              <div className="setting-copy"><strong>Theme intensity</strong><span>Adjust the glow of the cyan accents</span></div>
              <div className="range-row">
                <input type="range" min="15" max="100" value={settings.intensity} onChange={e => setSettings(s => ({ ...s, intensity: Number(e.target.value) }))}/>
                <strong>{settings.intensity}%</strong>
              </div>
            </div>
            <div className="settings-group">
              <div className="setting-copy"><strong>Interface appearance</strong><span>Choose the interface palette</span></div>
              <div className="theme-options">
                {[['midnight','Midnight'],['ocean','Ocean'],['violet','Violet']].map(([value,label]) => (
                  <button key={value} className={`theme-option ${settings.appearance === value ? 'active' : ''}`} onClick={() => setSettings(s => ({ ...s, appearance: value }))}>
                    <span className={`theme-swatch ${value}`}/>{label}{settings.appearance === value && <Icon name="check" size={14}/>}
                  </button>
                ))}
              </div>
            </div>
            <div className="settings-group setting-line">
              <div className="setting-copy"><strong>Voice responses</strong><span>Speak replies using speech synthesis</span></div>
              <Toggle checked={settings.voice} onChange={v => setSettings(s => ({ ...s, voice: v }))} label="Voice responses"/>
            </div>
            <div className="settings-group setting-line">
              <div className="setting-copy"><strong>Animations</strong><span>Orb rings, particles and transitions</span></div>
              <Toggle checked={settings.animations} onChange={v => setSettings(s => ({ ...s, animations: v }))} label="Animations"/>
            </div>
            <div className="modal-actions">
              <button className="secondary-btn" onClick={() => setSettings(DEFAULT_SETTINGS)}>Reset defaults</button>
              <button className="primary-btn" onClick={() => { setModal(''); setToast('Settings saved locally'); }}>Save settings <Icon name="check" size={15}/></button>
            </div>
          </div>
        </Modal>
      )}

      {modal === 'status' && (
        <Modal title="System Telemetry & Health" onClose={() => setModal('')}>
          <div className="status-modal-content">
            <div className="health-banner">
              <span className="health-icon"><Icon name={connection ? 'check' : 'alert'} size={20}/></span>
              <div>
                <strong>{connection ? 'FastAPI Backend is Online' : 'Backend is Offline'}</strong>
                <p>{connection ? `Running on http://${backendHealth?.system ? '127.0.0.1:8000' : 'localhost:8000'}` : 'Start backend via: python run.py'}</p>
              </div>
              <span className="health-state">{connection ? 'OPERATIONAL' : 'DISCONNECTED'}</span>
            </div>
            
            <div className="system-row">
              <div><strong>Active AI Provider</strong><span>Configured brain engine</span></div>
              <span className="state-good">{backendHealth?.active_provider ? backendHealth.active_provider.toUpperCase() : 'LOCAL ENGINE'}</span>
            </div>
            <div className="system-row">
              <div><strong>CPU Usage</strong><span>Processor load</span></div>
              <span className="state-good">{backendHealth?.system?.cpu_usage !== undefined ? `${backendHealth.system.cpu_usage}%` : 'N/A'}</span>
            </div>
            <div className="system-row">
              <div><strong>RAM Usage</strong><span>System memory</span></div>
              <span className="state-good">{backendHealth?.system?.ram_usage !== undefined ? `${backendHealth.system.ram_usage}%` : 'N/A'}</span>
            </div>
            <div className="system-row">
              <div><strong>D: Drive Free Storage</strong><span>Project disk space</span></div>
              <span className="state-good">{backendHealth?.system?.d_drive_free_gb !== undefined ? `${backendHealth.system.d_drive_free_gb} GB` : 'N/A'}</span>
            </div>
            <div className="system-row">
              <div><strong>System Uptime</strong><span>Windows OS runtime</span></div>
              <span className="state-good">{backendHealth?.system?.uptime || 'N/A'}</span>
            </div>
            <div className="system-row">
              <div><strong>Desktop Automation</strong><span>Safe Windows registry</span></div>
              <span className="state-good">Active (Notepad, Calc, Explorer, CMD)</span>
            </div>
          </div>
        </Modal>
      )}

      {modal === 'close' && (
        <Modal title="Close INAYA" onClose={() => setModal('')}>
          <div className="close-modal-copy">
            <div className="close-emblem"><Icon name="moon" size={24}/></div>
            <h3>INAYA Session Running</h3>
            <p>Your INAYA instance is safely running from D:\INAYA. To stop the server, press Ctrl+C in your PowerShell terminal.</p>
            <div className="modal-actions">
              <button className="primary-btn" onClick={() => setModal('')}>Keep Running</button>
            </div>
          </div>
        </Modal>
      )}

      {toast && <div className="toast"><span className="toast-check"><Icon name="check" size={14}/></span>{toast}</div>}
    </div>
  );
}
