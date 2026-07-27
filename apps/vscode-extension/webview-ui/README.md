# TEMPUS VS Code Extension Webview UI

This directory contains the React webview dashboard for the VS Code extension.

The webview UI should:
- Reuse components from packages/ui-kit
- Include Today's Tasks, Quick Capture, and Memory Search views
- Be built via Vite and bundled into the extension

To build:
```bash
cd webview-ui
pnpm install
pnpm build
```

The build output should be copied to the extension's dist directory.
