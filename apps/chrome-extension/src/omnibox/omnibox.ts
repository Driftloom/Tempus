/**
 * TEMPUS Chrome Extension Omnibox Handler
 * Quick task capture via address bar
 */

chrome.omnibox.onInputEntered.addListener((text, disposition) => {
  // Send to background for task creation
  chrome.runtime.sendMessage({
    type: 'QUICK_ADD_TASK',
    payload: {
      input: text,
      source: 'omnibox'
    }
  });
});

chrome.omnibox.onInputChanged.addListener((text, suggest) => {
  // Provide suggestions based on recent tasks or common patterns
  const suggestions = [
    { content: text, description: `Create task: ${text}` }
  ];
  suggest(suggestions);
});
