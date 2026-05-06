import React, { useState, useEffect, useCallback, useRef } from 'react';
import Header from './components/Header';
import CommandBar from './components/CommandBar';
import LiveAgentFeed from './components/LiveAgentFeed';
import PhaseTracker from './components/PhaseTracker';
import ReportViewer from './components/ReportViewer';
import { startScan, getScan, listScans } from './utils/api';
import { ScanWebSocket } from './utils/websocket';

export default function App() {
  const [currentView, setCurrentView] = useState('config');
  const [activeScanId, setActiveScanId] = useState(null);
  const [activeScan, setActiveScan] = useState(null);
  const [isLaunching, setIsLaunching] = useState(false);

  const [messages, setMessages] = useState([]);
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [progress, setProgress] = useState(0);
  const [currentPhase, setCurrentPhase] = useState('idle');
  const [phasesCompleted, setPhasesCompleted] = useState([]);

  const wsRef = useRef(null);
  const pollRef = useRef(null);

  const handleWsMessage = useCallback((msg) => {
    setMessages(prev => [...prev, msg]);
    if (msg.progress !== undefined) setProgress(msg.progress);
    if (msg.phase) setCurrentPhase(msg.phase);
  }, []);

  function connectWs(scanId) {
    if (wsRef.current) wsRef.current.disconnect();
    const ws = new ScanWebSocket(scanId, handleWsMessage, setWsStatus);
    ws.connect();
    wsRef.current = ws;
  }

  function disconnectWs() {
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
    }
  }

  useEffect(() => {
    if (!activeScanId) return;
    async function poll() {
      try {
        const scan = await getScan(activeScanId);
        setActiveScan(scan);
        if (scan.phases_completed) setPhasesCompleted(scan.phases_completed);
        if (scan.status === 'completed' || scan.status === 'error') {
          clearInterval(pollRef.current);
        }
      } catch (e) {}
    }
    poll();
    pollRef.current = setInterval(poll, 3000);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [activeScanId]);

  useEffect(() => {
    return () => {
      disconnectWs();
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  async function handleStartScan(config) {
    setIsLaunching(true);
    try {
      const result = await startScan(config);
      const scanId = result.scan_id;

      setActiveScanId(scanId);
      setActiveScan(result);
      setMessages([]);
      setProgress(0);
      setCurrentPhase('pending');
      setPhasesCompleted([]);
      setCurrentView('monitor');
      connectWs(scanId);

    } catch (e) {
      alert(`Failed to start scan: ${e.message}`);
    } finally {
      setIsLaunching(false);
    }
  }

  function renderMainContent() {
    if (currentView === 'config') {
      return (
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1, justifyContent: 'center', minHeight: 'calc(100vh - 64px)' }}>
          <div className="hero-band animate-fade-in" style={{ padding: 0 }}>
            <h1 className="display-xl" style={{ marginBottom: '16px' }}>Hi I Am Hercules</h1>
            <p className="body-md" style={{ color: 'var(--colors-muted)', marginBottom: '48px', maxWidth: '600px', margin: '0 auto 48px auto' }}>
              Automated pentesting and CTF Solving Agent. Enter a target below to launch a comprehensive security assessment.
            </p>
            <CommandBar onStartScan={handleStartScan} isScanning={isLaunching} />
          </div>
        </div>
      );
    }

    if (currentView === 'monitor') {
      return (
        <div className="animate-fade-in" style={{ paddingTop: '48px' }}>
          <div className="monitor-header">
            <div>
              <h2 className="display-sm">
                Scanning <span style={{ color: 'var(--colors-primary)' }}>{activeScan?.target || 'Target'}</span>
              </h2>
              <div className="caption" style={{ color: 'var(--colors-muted)', marginTop: '8px' }}>
                Scan ID: {activeScanId} • Mode: {activeScan?.ctf_mode ? 'CTF' : 'Standard'}
              </div>
            </div>
            {activeScan?.status === 'completed' && (
              <button className="btn btn-primary" onClick={() => setCurrentView('report')}>
                View Report
              </button>
            )}
          </div>

          <PhaseTracker
            currentPhase={currentPhase}
            completedPhases={phasesCompleted}
            ctfMode={activeScan?.ctf_mode}
            progress={progress}
            errors={activeScan?.errors}
          />

          <LiveAgentFeed events={messages} wsStatus={wsStatus} />
        </div>
      );
    }

    if (currentView === 'report') {
      return (
        <div className="animate-fade-in" style={{ paddingTop: '48px' }}>
          <ReportViewer scanId={activeScanId} scanStatus={activeScan?.status} />
        </div>
      );
    }
  }

  return (
    <div className="app-layout">
      <Header />
      <main className="app-main">
        {renderMainContent()}
      </main>
    </div>
  );
}
