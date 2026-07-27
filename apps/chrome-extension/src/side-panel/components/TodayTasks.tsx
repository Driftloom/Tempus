import React, { useState, useEffect } from 'react';
import { TempusClient } from '@tempus/core-sdk';

interface Task {
  id: string;
  title: string;
  status: string;
  priority: string;
  due_at: string | null;
}

export default function TodayTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    // Listen for connection status
    const handleConnectionStatus = (message: any) => {
      if (message.type === 'CONNECTION_STATUS') {
        setIsConnected(message.payload.connected);
      }
    };

    // Listen for task updates
    const handleTaskUpdate = (message: any) => {
      if (message.type === 'TASK_UPDATED') {
        // Refresh tasks
        fetchTasks();
      }
    };

    chrome.runtime.onMessage.addListener(handleConnectionStatus);
    chrome.runtime.onMessage.addListener(handleTaskUpdate);

    fetchTasks();

    return () => {
      chrome.runtime.onMessage.removeListener(handleConnectionStatus);
      chrome.runtime.onMessage.removeListener(handleTaskUpdate);
    };
  }, []);

  const fetchTasks = async () => {
    try {
      const client = new TempusClient();
      const response = await client.getTasks();
      setTasks(response.tasks);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeTask = async (taskId: string) => {
    try {
      const client = new TempusClient();
      await client.completeTask(taskId);
      setTasks(tasks.map(t => t.id === taskId ? { ...t, status: 'completed' } : t));
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  const snoozeTask = async (taskId: string, minutes: number = 10) => {
    try {
      const client = new TempusClient();
      await client.snoozeTask(taskId, minutes);
      fetchTasks();
    } catch (error) {
      console.error('Failed to snooze task:', error);
    }
  };

  if (!isConnected) {
    return (
      <div className="disconnected-banner">
        <p>⚠️ Disconnected from TEMPUS Core</p>
        <p>Retrying connection...</p>
      </div>
    );
  }

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  return (
    <div className="today-tasks">
      <h2>Today's Tasks</h2>
      <div className="task-list">
        {tasks.map(task => (
          <div key={task.id} className={`task-item priority-${task.priority}`}>
            <div className="task-header">
              <span className="task-title">{task.title}</span>
              <span className={`task-status ${task.status}`}>
                {task.status}
              </span>
            </div>
            {task.due_at && (
              <div className="task-due">
                Due: {new Date(task.due_at).toLocaleString()}
              </div>
            )}
            {task.status !== 'completed' && (
              <div className="task-actions">
                <button onClick={() => completeTask(task.id)}>Complete</button>
                <button onClick={() => snoozeTask(task.id)}>Snooze</button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
