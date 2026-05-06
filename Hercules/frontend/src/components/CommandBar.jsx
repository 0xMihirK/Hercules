import React, { useState } from 'react';
import { Target, Shield, Flag, ArrowRight, AlertCircle } from 'lucide-react';

// --- Validation patterns ---
const VALIDATORS = {
  ip: {
    regex: /^(\d{1,3}\.){3}\d{1,3}$/,
    test: (v) => {
      if (!VALIDATORS.ip.regex.test(v)) return false;
      return v.split('.').every(n => { const num = parseInt(n, 10); return num >= 0 && num <= 255; });
    },
    hint: 'Enter a valid IPv4 address (e.g. 192.168.1.1)',
  },
  ip_range: {
    regex: /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/,
    test: (v) => {
      if (!VALIDATORS.ip_range.regex.test(v)) return false;
      const [ip, cidr] = v.split('/');
      const cidrNum = parseInt(cidr, 10);
      if (cidrNum < 0 || cidrNum > 32) return false;
      return ip.split('.').every(n => { const num = parseInt(n, 10); return num >= 0 && num <= 255; });
    },
    hint: 'Enter a valid CIDR range (e.g. 10.0.0.0/24)',
  },
  website: {
    regex: /^(https?:\/\/)?([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(:\d{1,5})?(\/.*)?$/,
    test: (v) => VALIDATORS.website.regex.test(v),
    hint: 'Enter a valid domain or URL (e.g. example.com or https://example.com)',
  },
};

export default function CommandBar({ onStartScan, isScanning }) {
  const [target, setTarget] = useState('');
  const [targetType, setTargetType] = useState('ip');
  const [ctfMode, setCtfMode] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [error, setError] = useState('');

  const validate = (value, type) => {
    if (!value.trim()) { setError(''); return false; }
    const validator = VALIDATORS[type];
    if (!validator.test(value.trim())) {
      setError(validator.hint);
      return false;
    }
    setError('');
    return true;
  };

  const handleTargetChange = (e) => {
    const value = e.target.value;
    setTarget(value);
    if (error) validate(value, targetType);       // re-validate on change if error shown
  };

  const handleTypeChange = (e) => {
    const newType = e.target.value;
    setTargetType(newType);
    if (target) validate(target, newType);         // re-validate with new type
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!target.trim()) { setError('Target cannot be empty'); return; }
    if (!validate(target, targetType)) return;
    onStartScan({
      target: target.trim(),
      target_type: targetType,
      ctf_mode: ctfMode,
      special_instructions: '',
      compliance_framework: 'None'
    });
  };

  return (
    <div className="card" style={{ padding: '40px', textAlign: 'center', marginBottom: '40px' }}>
      <h1 className="hero-title" style={{ marginBottom: '16px' }}>What shall we audit today?</h1>
      <p className="hero-subtitle" style={{ marginBottom: '32px' }}>
        Enter an IP, domain, or URL to begin automated discovery and reconnaissance.
      </p>
      
      <form onSubmit={handleSubmit} style={{ maxWidth: '600px', margin: '0 auto' }}>
        <div 
          className="input-group" 
          style={{ 
            display: 'flex', 
            background: '#ffffff',
            borderRadius: '16px',
            padding: '8px',
            boxShadow: error ? '0 0 0 2px #ef4444' : (isFocused ? '0 0 0 2px var(--colors-primary)' : 'var(--shadow-sm)'),
            transition: 'var(--transition-fast)',
            border: error ? '1px solid #ef4444' : '1px solid var(--colors-border)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', padding: '0 16px', borderRight: '1px solid var(--colors-border)' }}>
            <select 
              value={targetType}
              onChange={handleTypeChange}
              style={{
                border: 'none',
                background: 'transparent',
                fontSize: '15px',
                fontFamily: 'var(--font-body)',
                color: 'var(--colors-text-secondary)',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value="ip">IP Address</option>
              <option value="ip_range">IP Range</option>
              <option value="website">Website</option>
            </select>
          </div>
          
          <input 
            type="text"
            className="search-input"
            placeholder={targetType === 'ip' ? 'e.g. 192.168.1.1' : targetType === 'ip_range' ? 'e.g. 10.0.0.0/24' : 'e.g. example.com'}
            value={target}
            onChange={handleTargetChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => { setIsFocused(false); if (target) validate(target, targetType); }}
            disabled={isScanning}
            style={{
              flex: 1,
              border: 'none',
              background: 'transparent',
              padding: '12px 16px',
              fontSize: '16px',
              fontFamily: 'var(--font-body)',
              color: 'var(--colors-text-primary)',
              outline: 'none',
            }}
          />
          
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isScanning || !target || !!error}
            style={{ padding: '8px 24px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            {isScanning ? 'Scanning...' : 'Start Audit'}
            {!isScanning && <ArrowRight size={18} />}
          </button>
        </div>
        
        {/* Validation error message */}
        {error && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            marginTop: '10px', padding: '8px 14px',
            background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px',
            color: '#dc2626', fontSize: '13px', fontWeight: '500',
          }}>
            <AlertCircle size={15} />
            {error}
          </div>
        )}
        
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '24px', gap: '24px' }}>
          <div 
            onClick={() => setCtfMode(!ctfMode)}
            title="CTF Mode enables aggressive Nmap scanning and active Metasploit exploitation. Normal mode restricts tools to detection-only."
            style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
          >
            {/* Toggle Switch */}
            <div style={{
              width: '44px',
              height: '24px',
              backgroundColor: ctfMode ? 'var(--colors-primary)' : 'var(--colors-border)',
              borderRadius: '12px',
              position: 'relative',
              transition: 'background-color 0.3s ease',
            }}>
              <div style={{
                width: '20px',
                height: '20px',
                backgroundColor: '#ffffff',
                borderRadius: '50%',
                position: 'absolute',
                top: '2px',
                left: ctfMode ? '22px' : '2px',
                transition: 'left 0.3s ease',
                boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
              }} />
            </div>
            
            {/* Label */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', color: ctfMode ? 'var(--colors-text-primary)' : 'var(--colors-text-secondary)', fontWeight: '500', transition: 'color 0.3s ease' }}>
              <Flag size={16} color={ctfMode ? 'var(--colors-primary)' : 'currentColor'} />
              Enable CTF Flag Hunter Mode
              <span style={{ 
                display: 'inline-flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                width: '16px', 
                height: '16px', 
                borderRadius: '50%', 
                background: 'var(--colors-surface-soft)', 
                border: '1px solid var(--colors-border)',
                color: 'var(--colors-muted)',
                fontSize: '10px',
                marginLeft: '4px'
              }}>?</span>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
