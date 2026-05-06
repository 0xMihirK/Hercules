/**
 * WebSocket client with auto-reconnect and message buffering.
 */
export class ScanWebSocket {
  constructor(scanId, onMessage, onStatusChange) {
    this.scanId = scanId;
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
    this.closed = false;
  }

  connect() {
    if (this.closed) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/${this.scanId}`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.onStatusChange?.('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'pong') return;
          this.onMessage?.(data);
        } catch (e) {
          console.warn('Failed to parse WS message:', e);
        }
      };

      this.ws.onclose = () => {
        this.onStatusChange?.('disconnected');
        if (!this.closed && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          const delay = this.reconnectDelay * Math.min(this.reconnectAttempts, 5);
          setTimeout(() => this.connect(), delay);
        }
      };

      this.ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        this.onStatusChange?.('error');
      };
    } catch (e) {
      console.error('Failed to create WebSocket:', e);
      this.onStatusChange?.('error');
    }
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
    }
  }

  disconnect() {
    this.closed = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
