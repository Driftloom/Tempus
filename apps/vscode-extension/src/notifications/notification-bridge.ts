/**
 * TEMPUS VS Code Extension - Notification Bridge
 * WS event → VS Code native notification
 */

import * as vscode from 'vscode';

export class NotificationBridge {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;

  constructor() {
    this.connectWebSocket();
  }

  private connectWebSocket() {
    const wsUrl = 'ws://localhost:8000/ws';
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      console.log('Connected to TEMPUS Core WebSocket');
    };
    
    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleCoreMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket connection closed, reconnecting in 5s...');
      this.reconnectTimer = setTimeout(() => this.connectWebSocket(), 5000);
    };
  }

  private handleCoreMessage(message: any) {
    switch (message.type) {
      case 'NOTIFICATION':
        this.showNativeNotification(message.payload);
        break;
      case 'TASK_DUE':
        this.showNativeNotification({
          title: 'Task Due',
          body: message.payload.task_title
        });
        break;
    }
  }

  private showNativeNotification(payload: any) {
    vscode.window.showInformationMessage(
      payload.title || 'TEMPUS',
      payload.body || ''
    );
  }

  dispose() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    if (this.ws) {
      this.ws.close();
    }
  }
}
