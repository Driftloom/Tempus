/**
 * TEMPUS VS Code Extension - Ask Assistant Command
 */

import * as vscode from 'vscode';

export function registerAskAssistantCommand(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand(
    'tempus.askAssistant',
    async () => {
      const input = await vscode.window.showInputBox({
        prompt: 'Ask TEMPUS Assistant',
        placeHolder: 'e.g., Plan my day'
      });

      if (input) {
        // In production, would route to Core which dispatches to appropriate skill
        vscode.window.showInformationMessage(`Processing: ${input}`);
      }
    }
  );

  context.subscriptions.push(disposable);
}
