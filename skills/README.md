# TEMPUS Skills

This directory contains MCP (Model Context Protocol) skills - single-shot, deterministic capabilities.

## Skill Structure
Each skill is a separate directory with:
- `manifest.json` - Skill metadata and required permissions
- `skill.py` - Main skill implementation
- `README.md` - Skill documentation

## Example Skills
- `plan-my-day/` - Daily planning skill
- `email-triage/` - Email triage and prioritization
- `weekly-review/` - Weekly review and consolidation
- `summarize/` - Content summarization

Skills register with the MCP Host in `apps/core/app/mcp/skills/` and can be invoked by agents or directly via the API.
