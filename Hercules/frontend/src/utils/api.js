const API_BASE = '';

export async function startScan(config) {
  const res = await fetch(`${API_BASE}/api/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to start scan');
  }
  return res.json();
}

export async function getScan(scanId) {
  const res = await fetch(`${API_BASE}/api/scan/${scanId}`);
  if (!res.ok) throw new Error('Scan not found');
  return res.json();
}

export async function listScans() {
  const res = await fetch(`${API_BASE}/api/scans`);
  if (!res.ok) throw new Error('Failed to list scans');
  return res.json();
}

export async function getReport(scanId) {
  const res = await fetch(`${API_BASE}/api/report/${scanId}`);
  if (!res.ok) throw new Error('Report not available');
  return res.text();
}
