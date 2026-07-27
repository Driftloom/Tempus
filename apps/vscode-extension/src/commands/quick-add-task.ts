/**
 * TEMPUS VS Code Extension - Quick Add Task Command
 */

import * as vscode from 'vscode';

export function registerQuickAddTaskCommand(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand(
    'tempus.quickAddTask',
    async () => {
      const input = await vscode.window.showInputBox({
        prompt: 'Enter task description',
        placeHolder: 'e.g., Complete the feature by Friday'
      });

      if (input) {
        // In production, would call Core API's NL parser via SDK
        vscode.window.showInformationMessage(`Task created: ${input}`);
      }
    }
  );

  context.subscriptions.push(disposable);
}
