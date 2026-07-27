# TEMPUS Connectors

This directory contains MCP (Model Context Protocol) connectors for external data sources.

## Connector Structure
Each connector is a separate directory with:
- `manifest.json` - Connector metadata and capabilities
- `connector.py` - Main connector implementation
- `README.md` - Connector documentation

## Example Connectors
- `gmail/` - Gmail email connector
- `outlook/` - Outlook email connector  
- `google-calendar/` - Google Calendar connector
- `slack/` - Slack connector
- `github/` - GitHub connector

Connectors register with the MCP Host in `apps/core/app/mcp/host/` to expose their capabilities to TEMPUS.
