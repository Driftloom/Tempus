/**
 * TEMPUS VS Code Extension - Timer Status Bar
 * Shows current active task/timer, click to switch/start/stop
 */

import * as vscode from 'vscode';

export class TimerStatusBarItem {
  private statusBarItem: vscode.StatusBarItem;
  private currentTask: string | null = null;
  private timerActive: boolean = false;

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this.statusBarItem.command = 'tempus.toggleTimer';
    this.statusBarItem.show();
    this.updateStatusBar();
  }

  updateTimerState(task: string | null, active: boolean) {
    this.currentTask = task;
    this.timerActive = active;
    this.updateStatusBar();
  }

  private updateStatusBar() {
    if (this.timerActive && this.currentTask) {
      this.statusBarItem.text = `$(clock) ${this.currentTask}`;
      this.statusBarItem.tooltip = 'Click to stop timer';
    } else if (this.timerActive) {
      this.statusBarItem.text = '$(clock) Timer running';
      this.statusBarItem.tooltip = 'Click to stop timer';
    } else {
      this.statusBarItem.text = '$(clock) TEMPUS';
      this.statusBarItem.tooltip = 'Click to start timer';
    }
  }

  dispose() {
    this.statusBarItem.dispose();
  }
}
