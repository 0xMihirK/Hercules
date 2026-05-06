import React, { useRef, useEffect } from 'react';
import { Activity, ShieldAlert, CheckCircle, Terminal, Info, ChevronRight } from 'lucide-react';

export default function LiveAgentFeed({ events }) {
  const feedEndRef = useRef(null);

  useEffect(() => {
    feedEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  const getIcon = (phase) => {
    switch(phase) {
      case 'discovery': return <Activity size={18} color="var(--colors-accent-teal)" />;
      case 'vulnerability_analysis': return <ShieldAlert size={18} color="var(--colors-accent-amber)" />;
      case 'exploitation': return <Terminal size={18} color="var(--colors-primary)" />;
      case 'reporting': return <CheckCircle size={18} color="var(--colors-success)" />;
      case 'error': return <ShieldAlert size={18} color="var(--colors-error)" />;
      default: return <Info size={18} color="var(--colors-text-tertiary)" />;
    }
  };

  const getBadgeColor = (phase) => {
    switch(phase) {
      case 'discovery': return { bg: '#e8f5f3', color: 'var(--colors-accent-teal)' };
      case 'vulnerability_analysis': return { bg: '#fef3e6', color: 'var(--colors-accent-amber)' };
      case 'exploitation': return { bg: '#faebe6', color: 'var(--colors-primary)' };
      case 'reporting': return { bg: '#eefcf1', color: 'var(--colors-success)' };
      case 'error': return { bg: '#fef1f2', color: 'var(--colors-error)' };
      default: return { bg: '#f1f1f1', color: 'var(--colors-text-tertiary)' };
    }
  };

  if (!events || events.length === 0) {
    return (
      <div className="card" style={{ padding: '48px', textAlign: 'center', border: '1px dashed var(--colors-border)' }}>
        <Terminal size={32} color="var(--colors-text-tertiary)" style={{ margin: '0 auto 16px auto' }} />
        <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '20px', color: 'var(--colors-text-secondary)', marginBottom: '8px' }}>Awaiting Assignment</h3>
        <p style={{ color: 'var(--colors-text-tertiary)', fontSize: '15px' }}>Start an audit to see real-time agent activity.</p>
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
      <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--colors-border)', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Activity size={20} color="var(--colors-text-primary)" />
        <h2 style={{ fontSize: '18px', fontWeight: '500', margin: 0 }}>Agent Activity Log</h2>
      </div>
      
      <div style={{ padding: '24px', maxHeight: '500px', overflowY: 'auto' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {events.map((evt, idx) => {
            const badgeStyle = getBadgeColor(evt.phase);
            return (
              <div key={idx} style={{ 
                display: 'flex', 
                gap: '16px', 
                alignItems: 'flex-start',
                paddingBottom: idx !== events.length - 1 ? '16px' : '0',
                borderBottom: idx !== events.length - 1 ? '1px solid var(--colors-border)' : 'none'
              }}>
                <div style={{ 
                  marginTop: '2px',
                  width: '32px', 
                  height: '32px', 
                  borderRadius: '50%', 
                  background: badgeStyle.bg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  {getIcon(evt.phase)}
                </div>
                
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ 
                      fontSize: '12px', 
                      fontWeight: '600', 
                      textTransform: 'uppercase', 
                      letterSpacing: '0.05em',
                      color: badgeStyle.color
                    }}>
                      {evt.phase.replace('_', ' ')}
                    </span>
                    <span style={{ fontSize: '13px', color: 'var(--colors-text-tertiary)' }}>
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div style={{ 
                    fontSize: '15px', 
                    color: 'var(--colors-text-primary)',
                    lineHeight: '1.6',
                    fontFamily: evt.message.includes('```') ? 'var(--font-mono)' : 'var(--font-body)'
                  }}>
                    {evt.message}
                  </div>
                </div>
              </div>
            );
          })}
          <div ref={feedEndRef} />
        </div>
      </div>
    </div>
  );
}
