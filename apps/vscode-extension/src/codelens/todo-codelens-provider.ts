/**
 * TEMPUS VS Code Extension - TODO CodeLens Provider
 * Shows "Track as task" action on TODO/FIXME comments
 */

import * as vscode from 'vscode';

export class TodoCodelensProvider implements vscode.CodeLensProvider {
  private codeLenses: vscode.CodeLens[] = [];
  private _onDidChangeCodeLenses = new vscode.EventEmitter<void>();
  readonly onDidChangeCodeLenses = this._onDidChangeCodeLenses.event;

  provideCodeLenses(
    document: vscode.TextDocument,
    token: vscode.CancellationToken
  ): vscode.CodeLens[] | Thenable<vscode.CodeLens[]> {
    this.codeLenses = [];
    const text = document.getText();
    const lines = text.split('\n');

    lines.forEach((line, index) => {
      const todoMatch = line.match(/\/\/\s*(TODO|FIXME|XXX):\s*(.*)/i);
      if (todoMatch) {
        const range = new vscode.Range(
          new vscode.Position(index, 0),
          new vscode.Position(index, line.length)
        );
        const codeLens = new vscode.CodeLens(range, {
          title: 'Track as task',
          command: 'tempus.trackAsTask',
          arguments: [
            document.uri,
            range,
            todoMatch[2] || todoMatch[1]
          ]
        });
        this.codeLenses.push(codeLens);
      }
    });

    return this.codeLenses;
  }

  refresh() {
    this._onDidChangeCodeLenses.fire();
  }
}
