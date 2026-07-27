import React, { useState, useEffect } from 'react';
import { TempusClient } from '@tempus/core-sdk';

interface Connector {
  id: string;
  name: string;
  type: string;
  status: string;
}

export default function ConnectorStatus() {
  const [connectors, setConnectors] = useState<Connector[]>([]);

  useEffect(() => {
    const fetchConnectors = async () => {
      try {
        const client = new TempusClient();
        const response = await client.getConnectors();
        setConnectors(response.connectors);
      } catch (error) {
        console.error('Failed to fetch connectors:', error);
      }
    };
    fetchConnectors();
  }, []);

  const handleReconnect = async (connectorId: string) => {
    try {
      const client = new TempusClient();
      await client.reconnectConnector(connectorId);
      const response = await client.getConnectors();
      setConnectors(response.connectors);
    } catch (error) {
      console.error('Failed to reconnect connector:', error);
    }
  };

  return (
    <div className="connector-status">
      <h2>Connector Status</h2>
      <div className="connector-list">
        {connectors.map(connector => (
          <div key={connector.id} className={`connector-item status-${connector.status}`}>
            <div className="connector-info">
              <span className="connector-name">{connector.name}</span>
              <span className={`connector-status-badge ${connector.status}`}>
                {connector.status}
              </span>
            </div>
            {connector.status === 'inactive' && (
              <button onClick={() => handleReconnect(connector.id)}>
                Reconnect
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
