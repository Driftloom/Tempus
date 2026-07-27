import React, { useState } from 'react';
import { TempusClient } from '@tempus/core-sdk';

export default function QuickCapture() {
  const [input, setInput] = useState('');
  const [parsed, setParsed] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
    setParsed(null);
  };

  const handleParse = async () => {
    if (!input.trim()) return;

    setLoading(true);
    try {
      const client = new TempusClient();
      const parsed = await client.parseTask(input);
      setParsed(parsed);
    } catch (error) {
      console.error('Failed to parse input:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!parsed) return;

    try {
      const client = new TempusClient();
      await client.createTask(parsed.title, 'chrome-extension');
      chrome.runtime.sendMessage({
        type: 'QUICK_ADD_TASK',
        payload: {
          input: parsed.title,
          source: 'chrome-extension'
        }
      });
      setInput('');
      setParsed(null);
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  return (
    <div className="quick-capture">
      <h2>Quick Capture</h2>
      <input
        type="text"
        value={input}
        onChange={handleInputChange}
        placeholder="Enter task (e.g., 'Complete report by tomorrow #urgent')"
        className="capture-input"
      />
      <button onClick={handleParse} disabled={loading || !input.trim()}>
        {loading ? 'Parsing...' : 'Parse'}
      </button>

      {parsed && (
        <div className="parsed-result">
          <h3>Parsed Task</h3>
          <div className="parsed-field">
            <strong>Title:</strong> {parsed.title}
          </div>
          {parsed.due_at && (
            <div className="parsed-field">
              <strong>Due:</strong> {new Date(parsed.due_at).toLocaleString()}
            </div>
          )}
          {parsed.estimated_minutes && (
            <div className="parsed-field">
              <strong>Estimate:</strong> {parsed.estimated_minutes} min
            </div>
          )}
          {parsed.tags && parsed.tags.length > 0 && (
            <div className="parsed-field">
              <strong>Tags:</strong> {parsed.tags.join(', ')}
            </div>
          )}
          <div className="parsed-actions">
            <button onClick={handleCreate}>Create Task</button>
            <button onClick={() => setParsed(null)}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}
