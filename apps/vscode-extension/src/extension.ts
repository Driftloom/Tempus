import * as vscode from 'vscode';
import { TimerStatusBarItem } from './status-bar/timer-status-bar';
import { TodoCodelensProvider } from './codelens/todo-codelens-provider';
import { registerStartStopTimerCommand } from './commands/start-stop-timer';
import { registerQuickAddTaskCommand } from './commands/quick-add-task';
import { registerAskAssistantCommand } from './commands/ask-assistant';
import { DashboardPanel } from './webview/dashboard-panel';
import { NotificationBridge } from './notifications/notification-bridge';

let timerStatusBarItem: TimerStatusBarItem;
let todoCodelensProvider: TodoCodelensProvider;
let notificationBridge: NotificationBridge;

export function activate(context: vscode.ExtensionContext) {
  console.log('TEMPUS VS Code Extension is now active');

  // Initialize timer status bar
  timerStatusBarItem = new TimerStatusBarItem();

  // Initialize TODO CodeLens provider
  todoCodelensProvider = new TodoCodelensProvider();
  vscode.languages.registerCodeLensProvider('*', todoCodelensProvider);

  // Register commands
  registerStartStopTimerCommand(context);
  registerQuickAddTaskCommand(context);
  registerAskAssistantCommand(context);

  // Register track as task command for CodeLens
  const trackAsTaskCommand = vscode.commands.registerCommand(
    'tempus.trackAsTask',
    async (uri: vscode.Uri, range: vscode.Range, taskText: string) => {
      // In production, would call Core API via SDK with file+line reference
      vscode.window.showInformationMessage(`Tracking task: ${taskText}`);
    }
  );
  context.subscriptions.push(trackAsTaskCommand);

  // Register open dashboard command
  const openDashboardCommand = vscode.commands.registerCommand(
    'tempus.openDashboard',
    () => {
      DashboardPanel.createOrShow(context.extensionUri);
    }
  );
  context.subscriptions.push(openDashboardCommand);

  // Initialize notification bridge
  notificationBridge = new NotificationBridge();

  // Store auth token in SecretStorage
  const token = context.secrets.get('tempusAuthToken');
  if (!token) {
    // In production, would trigger OAuth flow
    console.log('No auth token found, would trigger OAuth');
  }

  context.subscriptions.push(timerStatusBarItem);
  context.subscriptions.push(notificationBridge);
}

export function deactivate() {
  console.log('TEMPUS VS Code Extension is now deactivated');
  
  if (timerStatusBarItem) {
    timerStatusBarItem.dispose();
  }
  
  if (notificationBridge) {
    notificationBridge.dispose();
  }
  
  if (DashboardPanel.currentPanel) {
    DashboardPanel.currentPanel.dispose();
  }
}
