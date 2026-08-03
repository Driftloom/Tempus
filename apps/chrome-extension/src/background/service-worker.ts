/**
 * TEMPUS Chrome Extension Background Service Worker
 * WebSocket connection, event relay, notification bridge
 */

const CORE_WS_URL = 'ws://localhost:8000/ws';
let ws: WebSocket | null = null;
let reconnectTimer: number | null = null;
let isConnected = false;

// WebSocket connection management
function connectWebSocket() {
  ws = new WebSocket(CORE_WS_URL);

  ws.onopen = () => {
    console.log('TEMPUS: Connected to Core');
    isConnected = true;
    updateBadge();
    clearReconnectTimer();
  };

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    handleCoreMessage(message);
  };

  ws.onerror = (error) => {
    console.error('TEMPUS: WebSocket error', error);
  };

  ws.onclose = () => {
    console.log('TEMPUS: WebSocket closed, reconnecting...');
    isConnected = false;
    updateBadge();
    scheduleReconnect();
  };
}

function scheduleReconnect() {
  if (reconnectTimer) return;
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connectWebSocket();
  }, 5000); // 5 second backoff
}

function clearReconnectTimer() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
}

// Handle messages from Core
function handleCoreMessage(message: any) {
  switch (message.type) {
    case 'TASK_UPDATED':
      relayToSidePanel(message);
      updateBadge();
      break;
    case 'NOTIFICATION':
      showNativeNotification(message.payload);
      break;
    case 'CONNECTOR_STATUS':
      relayToSidePanel(message);
      break;
    default:
      console.log('TEMPUS: Unknown message type', message.type);
  }
}

// Relay messages to side panel
function relayToSidePanel(message: any) {
  chrome.runtime.sendMessage({
    type: 'CORE_EVENT',
    payload: message
  });
}

// Show native Chrome notification
function showNativeNotification(payload: any) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon128.png',
    title: payload.title || 'TEMPUS',
    message: payload.body || '',
    priority: 2
  });
}

// Update extension badge
function updateBadge() {
  if (isConnected) {
    chrome.action.setBadgeText({ text: '' });
    chrome.action.setBadgeBackgroundColor({ color: '#4CAF50' });
  } else {
    chrome.action.setBadgeText({ text: '!' });
    chrome.action.setBadgeBackgroundColor({ color: '#F44336' });
  }
}

// Handle extension install
chrome.runtime.onInstalled.addListener(() => {
  console.log('TEMPUS Chrome Extension installed');
  connectWebSocket();
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  // TODO: Implement side panel when API is available
  console.log('TEMPUS: Extension icon clicked');
});

// Handle messages from content scripts and side panel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {
    case 'CAPTURE_TO_MEMORY':
      if (ws && isConnected) {
        ws.send(JSON.stringify({
          type: 'MEMORY_INGEST',
          payload: message.payload
        }));
      }
      break;
    case 'QUICK_ADD_TASK':
      if (ws && isConnected) {
        ws.send(JSON.stringify({
          type: 'TASK_CREATE',
          payload: message.payload
        }));
      }
      break;
  }
  return true;
});
