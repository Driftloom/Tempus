import React from 'react';
import TodayTasks from './components/TodayTasks';
import QuickCapture from './components/QuickCapture';
import MemorySearch from './components/MemorySearch';
import ConnectorStatus from './components/ConnectorStatus';
import PermissionRequests from './components/PermissionRequests';

function App() {
  return (
    <div className="tempus-side-panel">
      <h1>TEMPUS</h1>
      <p className="subtitle">Personal Intelligence Layer</p>
      
      <TodayTasks />
      <QuickCapture />
      <MemorySearch />
      <ConnectorStatus />
      <PermissionRequests />
    </div>
  );
}

export default App;
