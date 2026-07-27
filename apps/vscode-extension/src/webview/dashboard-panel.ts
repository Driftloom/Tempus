/**
 * TEMPUS VS Code Extension - Webview Dashboard Panel
 * Loads React dashboard build
 */

import * as vscode from 'vscode';

export class DashboardPanel {
  public static currentPanel: DashboardPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  public static createOrShow(extensionUri: vscode.Uri) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    if (DashboardPanel.currentPanel) {
      DashboardPanel.currentPanel._panel.reveal(column);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      'tempusDashboard',
      'TEMPUS Dashboard',
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true
      }
    );

    DashboardPanel.currentPanel = new DashboardPanel(panel, extensionUri);
  }

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this._panel = panel;

    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    this._panel.webview.html = this._getHtmlForWebview();
  }

  private _getHtmlForWebview() {
    // TEMPUS Dashboard - connects to Core API
    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TEMPUS Dashboard</title>
        <style>
          body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
          }
          h1 {
            color: var(--vscode-foreground);
          }
          .dashboard-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
          }
          .dashboard-section {
            padding: 15px;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
          }
          .loading {
            color: var(--vscode-descriptionForeground);
          }
          .task-item {
            padding: 8px;
            margin: 4px 0;
            border-left: 3px solid var(--vscode-textLink-foreground);
          }
        </style>
      </head>
      <body>
        <h1>TEMPUS Dashboard</h1>
        <div class="dashboard-container">
          <div class="dashboard-section">
            <h2>Today's Tasks</h2>
            <div id="tasks-container" class="loading">Loading tasks...</div>
          </div>
          <div class="dashboard-section">
            <h2>Quick Capture</h2>
            <input type="text" id="task-input" placeholder="Enter task..." style="width: 100%; padding: 8px; margin: 10px 0;">
            <button id="add-task-btn" style="padding: 8px 16px;">Add Task</button>
          </div>
        </div>
        <script>
          const vscode = acquireVsCodeApi();
          
          // Load tasks from Core API
          async function loadTasks() {
            try {
              const response = await fetch('http://localhost:8000/api/v1/tasks');
              const data = await response.json();
              const container = document.getElementById('tasks-container');
              container.innerHTML = data.tasks.map(task => 
                '<div class="task-item">' + task.title + '</div>'
              ).join('');
            } catch (error) {
              document.getElementById('tasks-container').innerHTML = 'Failed to load tasks';
            }
          }
          
          // Add task
          document.getElementById('add-task-btn').addEventListener('click', async () => {
            const input = document.getElementById('task-input');
            if (input.value) {
              try {
                await fetch('http://localhost:8000/api/v1/tasks', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ input: input.value, source: 'vscode' })
                });
                input.value = '';
                loadTasks();
              } catch (error) {
                console.error('Failed to add task:', error);
              }
            }
          });
          
          loadTasks();
        </script>
      </body>
      </html>
    `;
  }

  public dispose() {
    DashboardPanel.currentPanel = undefined;
    this._panel.dispose();
    while (this._disposables.length) {
      const disposable = this._disposables.pop();
      if (disposable) {
        disposable.dispose();
      }
    }
  }
}
