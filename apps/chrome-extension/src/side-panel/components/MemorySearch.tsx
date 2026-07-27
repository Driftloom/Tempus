import React, { useState } from 'react';
import { TempusClient } from '@tempus/core-sdk';

interface MemoryResult {
  id: string;
  content: string;
  layer: string;
  importance_score: number;
  created_at: string;
}

export default function MemorySearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<MemoryResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const client = new TempusClient();
      const response = await client.searchMemory(query);
      setResults(response.results);
    } catch (error) {
      console.error('Failed to search memory:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="memory-search">
      <h2>Memory Search</h2>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search your memory..."
        className="search-input"
      />
      <button onClick={handleSearch} disabled={loading || !query.trim()}>
        {loading ? 'Searching...' : 'Search'}
      </button>

      {results.length > 0 && (
        <div className="search-results">
          <h3>Results</h3>
          {results.map(result => (
            <div key={result.id} className="memory-result">
              <div className="memory-content">{result.content}</div>
              <div className="memory-meta">
                <span className={`memory-layer ${result.layer}`}>
                  {result.layer}
                </span>
                <span className="memory-importance">
                  {Math.round(result.importance_score * 100)}% relevant
                </span>
                <span className="memory-date">
                  {new Date(result.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
