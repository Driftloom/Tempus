/**
 * TEMPUS VS Code Extension - Start/Stop Timer Command
 */

import * as vscode from 'vscode';

export function registerStartStopTimerCommand(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand(
    'tempus.toggleTimer',
    async () => {
      // In production, would call Core API via SDK
      // For now, show quick pick
      const options = [
        { label: 'Start Timer', description: 'Start a new timer' },
        { label: 'Stop Timer', description: 'Stop current timer' },
        { label: 'Switch Task', description: 'Switch to different task' }
      ];

      const selected = await vscode.window.showQuickPick(options);
      
      if (selected) {
        vscode.window.showInformationMessage(`Selected: ${selected.label}`);
        // In production, would call Core API
      }
    }
  );

  context.subscriptions.push(disposable);
}
