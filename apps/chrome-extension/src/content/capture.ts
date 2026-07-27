/**
 * TEMPUS Chrome Extension Content Script
 * Handles context menu capture and page content saving
 */

// Context menu item for capturing selection
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'save-to-tempus',
    title: 'Save selection to TEMPUS',
    contexts: ['selection']
  });
});

// Handle context menu click
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'save-to-tempus' && info.selectionText && tab) {
    captureSelection(info.selectionText, tab.url || '', tab.title || '');
  }
});

async function captureSelection(text: string, url: string, title: string) {
  try {
    // Send to background service worker for processing
    chrome.runtime.sendMessage({
      type: 'CAPTURE_TO_MEMORY',
      payload: {
        content: text,
        source: 'browser',
        source_ref: url,
        metadata: {
          title,
          url
        }
      }
    });
  } catch (error) {
    console.error('Failed to capture selection:', error);
  }
}
