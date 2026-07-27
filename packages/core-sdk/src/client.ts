/**
 * TEMPUS Core SDK - Typed client for TEMPUS Core API
 */

interface Task {
  id: string;
  title: string;
  status: 'pending' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high';
  due_at: string | null;
  created_at: string;
  updated_at: string;
}

interface MemoryResult {
  id: string;
  content: string;
  layer: 'working' | 'episodic' | 'semantic';
  importance_score: number;
  created_at: string;
}

interface ParsedTask {
  title: string;
  due_at: string | null;
  estimated_minutes: number;
  tags: string[];
}

interface Connector {
  id: string;
  name: string;
  type: 'email' | 'calendar' | 'other';
  status: 'active' | 'inactive' | 'error';
}

interface PermissionRequest {
  id: string;
  skill_id: string;
  skill_name: string;
  permissions: string[];
  requested_at: string;
}

export class TempusClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  setToken(token: string): void {
    this.token = token;
  }

  clearToken(): void {
    this.token = null;
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request('/health/live');
  }

  // Task operations
  async getTasks(): Promise<{ tasks: Task[] }> {
    return this.request('/api/v1/tasks');
  }

  async createTask(input: string, source: string = 'api'): Promise<{ task: Task }> {
    return this.request('/api/v1/tasks', {
      method: 'POST',
      body: JSON.stringify({ input, source }),
    });
  }

  async completeTask(taskId: string): Promise<{ task: Task }> {
    return this.request(`/api/v1/tasks/${taskId}/complete`, {
      method: 'POST',
    });
  }

  async snoozeTask(taskId: string, minutes: number = 10): Promise<{ task: Task }> {
    return this.request(`/api/v1/tasks/${taskId}/snooze`, {
      method: 'POST',
      body: JSON.stringify({ minutes }),
    });
  }

  // Memory operations
  async searchMemory(query: string): Promise<{ results: MemoryResult[] }> {
    return this.request('/api/v1/memory/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  async ingestMemory(content: string, source: string = 'api'): Promise<{ memory: MemoryResult }> {
    return this.request('/api/v1/memory', {
      method: 'POST',
      body: JSON.stringify({ content, source }),
    });
  }

  // Natural language parsing
  async parseTask(input: string): Promise<ParsedTask> {
    return this.request('/api/v1/tasks/parse', {
      method: 'POST',
      body: JSON.stringify({ input }),
    });
  }

  // Connector operations
  async getConnectors(): Promise<{ connectors: Connector[] }> {
    return this.request('/api/v1/connectors');
  }

  async reconnectConnector(connectorId: string): Promise<{ connector: Connector }> {
    return this.request(`/api/v1/connectors/${connectorId}/reconnect`, {
      method: 'POST',
    });
  }

  // Permission operations
  async getPermissionRequests(): Promise<{ requests: PermissionRequest[] }> {
    return this.request('/api/v1/permissions/requests');
  }

  async approvePermissionRequest(requestId: string): Promise<{ success: boolean }> {
    return this.request(`/api/v1/permissions/requests/${requestId}/approve`, {
      method: 'POST',
    });
  }

  async denyPermissionRequest(requestId: string): Promise<{ success: boolean }> {
    return this.request(`/api/v1/permissions/requests/${requestId}/deny`, {
      method: 'POST',
    });
  }
}
