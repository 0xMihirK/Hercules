import React from 'react';
import { Search, Shield, Zap, FileText, CheckCircle2 } from 'lucide-react';

const PHASES = [
  { id: 'discovery', label: 'Discovery', icon: Search },
  { id: 'analysis', label: 'Analysis', icon: Shield },
  { id: 'exploitation', label: 'Exploitation', icon: Zap },
  { id: 'reporting', label: 'Reporting', icon: FileText }
];

const PHASE_MAPPING = {
  idle: 'discovery',
  pending: 'discovery',
  initializing: 'discovery',
  reconnaissance: 'discovery',
  enumeration: 'discovery',
  web_app_testing: 'discovery',
  vulnerability_scan: 'analysis',
  routing: 'analysis',
  exploitation: 'exploitation',
  post_exploitation: 'exploitation',
  reporting: 'reporting',
  completed: 'reporting',
  error: 'reporting'
};

export default function PhaseTracker({ currentPhase, completedPhases = [], progress = 0, ctfMode = false }) {
  
  const activePhases = PHASES.filter(p => ctfMode || p.id !== 'exploitation');
  
  const mappedCurrentPhase = PHASE_MAPPING[currentPhase] || 'discovery';
  const currentIndex = activePhases.findIndex(p => p.id === mappedCurrentPhase);

  const getPhaseState = (phaseId) => {
    const phaseIndex = activePhases.findIndex(p => p.id === phaseId);
    if (currentPhase === 'completed') return 'completed';
    if (phaseIndex < currentIndex) return 'completed';
    if (phaseIndex === currentIndex) return 'current';
    return 'pending';
  };

  return (
    <div className="card" style={{ padding: '32px 40px', marginBottom: '40px' }}>
      <h3 style={{ fontSize: '16px', fontWeight: '500', marginBottom: '24px', color: 'var(--colors-text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
        Audit Progress
        {progress > 0 && progress < 100 && (
          <span style={{ fontSize: '14px', color: 'var(--colors-primary)' }}>({progress}%)</span>
        )}
      </h3>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', position: 'relative' }}>
        {/* Background line */}
        <div style={{ 
          position: 'absolute', 
          top: '20px', 
          left: '40px', 
          right: '40px', 
          height: '2px', 
          background: 'var(--colors-border)',
          zIndex: 1
        }} />
        
        {/* Progress line */}
        <div style={{ 
          position: 'absolute', 
          top: '20px', 
          left: '40px', 
          width: `calc(${Math.max(0, currentIndex) / (activePhases.length - 1) * 100}% - 40px)`, 
          height: '2px', 
          background: 'var(--colors-primary)',
          transition: 'width 0.5s ease',
          zIndex: 2
        }} />

        {activePhases.map((phase, idx) => {
          const state = getPhaseState(phase.id);
          const Icon = state === 'completed' ? CheckCircle2 : phase.icon;
          
          let bgColor = 'var(--colors-surface)';
          let iconColor = 'var(--colors-text-tertiary)';
          let borderColor = 'var(--colors-border)';
          
          if (state === 'completed') {
            bgColor = 'var(--colors-primary)';
            iconColor = '#ffffff';
            borderColor = 'var(--colors-primary)';
          } else if (state === 'current') {
            bgColor = '#ffffff';
            iconColor = 'var(--colors-primary)';
            borderColor = 'var(--colors-primary)';
          }

          return (
            <div key={phase.id} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', zIndex: 3, position: 'relative', background: 'var(--colors-surface)', padding: '0 16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: bgColor,
                border: `2px solid ${borderColor}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.3s ease',
                boxShadow: state === 'current' ? '0 0 0 4px rgba(204, 120, 92, 0.1)' : 'none'
              }}>
                <Icon size={18} color={iconColor} />
              </div>
              <span style={{ 
                fontSize: '14px', 
                fontWeight: state === 'current' ? '600' : '400',
                color: state === 'pending' ? 'var(--colors-text-tertiary)' : 'var(--colors-text-primary)'
              }}>
                {phase.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
