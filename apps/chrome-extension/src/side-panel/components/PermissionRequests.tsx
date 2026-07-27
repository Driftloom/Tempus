import React, { useState, useEffect } from 'react';
import { TempusClient } from '@tempus/core-sdk';

interface PermissionRequest {
  id: string;
  skill_id: string;
  skill_name: string;
  permissions: string[];
  requested_at: string;
}

export default function PermissionRequests() {
  const [requests, setRequests] = useState<PermissionRequest[]>([]);

  useEffect(() => {
    const fetchRequests = async () => {
      try {
        const client = new TempusClient();
        const response = await client.getPermissionRequests();
        setRequests(response.requests);
      } catch (error) {
        console.error('Failed to fetch permission requests:', error);
      }
    };
    fetchRequests();
  }, []);

  const handleApprove = async (requestId: string) => {
    try {
      const client = new TempusClient();
      await client.approvePermissionRequest(requestId);
      setRequests(requests.filter(r => r.id !== requestId));
    } catch (error) {
      console.error('Failed to approve permission:', error);
    }
  };

  const handleDeny = async (requestId: string) => {
    try {
      const client = new TempusClient();
      await client.denyPermissionRequest(requestId);
      setRequests(requests.filter(r => r.id !== requestId));
    } catch (error) {
      console.error('Failed to deny permission:', error);
    }
  };

  if (requests.length === 0) {
    return null;
  }

  return (
    <div className="permission-requests">
      <h2>Permission Requests</h2>
      {requests.map(request => (
        <div key={request.id} className="permission-request">
          <div className="request-info">
            <strong>{request.skill_name}</strong>
            <div className="permissions">
              {request.permissions.map(perm => (
                <span key={perm} className="permission-tag">
                  {perm}
                </span>
              ))}
            </div>
          </div>
          <div className="request-actions">
            <button onClick={() => handleApprove(request.id)}>Approve</button>
            <button onClick={() => handleDeny(request.id)}>Deny</button>
          </div>
        </div>
      ))}
    </div>
  );
}
