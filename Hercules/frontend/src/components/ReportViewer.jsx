import React from 'react';
import { FileText, Download, ExternalLink } from 'lucide-react';

export default function ReportViewer({ scanId }) {
  if (!scanId) return null;

  return (
    <div className="card" style={{ padding: '0', overflow: 'hidden', marginTop: '40px' }}>
      <div style={{ 
        padding: '24px', 
        borderBottom: '1px solid var(--colors-border)', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        background: '#ffffff'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <FileText size={24} color="var(--colors-primary)" />
          <div>
            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '500' }}>Executive Summary</h2>
            <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: 'var(--colors-text-tertiary)' }}>
              Final compilation of findings and evidence
            </p>
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            onClick={() => {
              const iframe = document.getElementById('report-iframe');
              if (iframe && iframe.contentWindow) {
                iframe.contentWindow.postMessage('print_report', '*');
              }
            }}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '8px' }}
          >
            <Download size={16} />
            Download PDF
          </button>
          
          <a 
            href={`http://localhost:8000/api/report/${scanId}`} 
            target="_blank" 
            rel="noreferrer"
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '8px', textDecoration: 'none' }}
          >
            <ExternalLink size={16} />
            Open Full Window
          </a>
        </div>
      </div>
      
      <div style={{ background: '#faf9f5', padding: '24px' }}>
        <div style={{ 
          background: '#ffffff',
          border: '1px solid var(--colors-border)',
          borderRadius: '8px',
          boxShadow: 'var(--shadow-sm)',
          overflow: 'hidden'
        }}>
          <iframe 
            id="report-iframe"
            src={`http://localhost:8000/api/report/${scanId}`}
            style={{ 
              width: '100%', 
              height: '800px', 
              border: 'none',
              background: '#ffffff'
            }}
            title="Scan Report"
          />
        </div>
      </div>
    </div>
  );
}
