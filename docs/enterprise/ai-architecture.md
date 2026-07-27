# AI Architecture - TEMPUS

## Executive Summary

This document provides a comprehensive overview of the AI/LLM architecture in TEMPUS, including the hybrid LLM routing strategy, multi-agent orchestration, connector architecture, extension/plugin architecture, and prompt engineering practices.

## AI Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           TEMPUS AI Architecture                                  │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                        Application Layer                                 │  │
│  │                                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ Task Service │  │Memory Service│  │Agent Runtime │  │Email Intel   │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │  │
│  └─────────┼────────────────┼────────────────┼────────────────┼───────────────┘  │
│            │                │                │                │                  │
│  ┌─────────┼────────────────┼────────────────┼────────────────┼───────────────┐  │
│  │         │                │                │                │                  │  │
│  │  ┌──────┴────────────────┴────────────────┴────────────────┴──────────┐  │  │
│  │  │                     Router Service (Hybrid LLM Router)               │  │  │
│  │  │                                                                   │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │              Routing Decision Engine                          │  │  │  │
│  │  │  │                                                             │  │  │  │
│  │  │  │  - Sensitivity Analysis (PII, sensitive data)              │  │  │  │
│  │  │  │  - Complexity Analysis (token count, reasoning required)    │  │  │  │
│  │  │  │  - Budget Analysis (user budget, cost constraints)          │  │  │  │
│  │  │  │  - Latency Requirements (real-time vs async)                │  │  │  │
│  │  │  │  - Quality Requirements (accuracy vs speed)                 │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                           │  │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │  │
│  │  │                        Provider Layer                             │  │  │
│  │  │                                                                   │  │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │  │
│  │  │  │   Local      │  │   Cloud      │  │   Specialized│          │  │  │
│  │  │  │   Providers  │  │   Providers  │  │   Providers  │          │  │  │
│  │  │  │              │  │              │  │              │          │  │  │
│  │  │  │  ┌──────────┐│  │  ┌──────────┐│  │  ┌──────────┐│          │  │  │
│  │  │  │  │ Ollama   ││  │  │ Anthropic││  │  │ OpenAI   ││          │  │  │
│  │  │  │  │ Llama 3  ││  │  │ Claude   ││  │  │ GPT-4    ││          │  │  │
│  │  │  │  │ Mistral  ││  │  │ Haiku    ││  │  │ GPT-3.5  ││          │  │  │
│  │  │  │  │ Gemma    ││  │  │ Opus     ││  │  │ DALL-E   ││          │  │  │
│  │  │  │  └──────────┘│  │  └──────────┘│  │  └──────────┘│          │  │  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                           │  │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │  │
│  │  │                      Caching Layer                                │  │  │
│  │  │                                                                   │  │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │  │
│  │  │  │ Response     │  │ Semantic     │  │ Prompt       │          │  │  │
│  │  │  │ Cache        │  │ Cache        │  │ Cache        │          │  │  │
│  │  │  │ (Redis)      │  │ (Redis)      │  │ (Redis)      │          │  │  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                     Multi-Agent Orchestration                             │  │
│  │                                                                           │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  │                        Supervisor                                     │  │
│  │  │                                                                   │  │  │
│  │  │  - Agent Registration                                             │  │  │
│  │  │  - Agent Orchestration (concurrent/sequential)                     │  │  │
│  │  │  - Result Merging                                                  │  │  │
│  │  │  - Cancellation Coordination                                       │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ Researcher   │  │ Planner      │  │ Executor     │  │ Analyst      │  │  │
│  │  │ Agent        │  │ Agent        │  │ Agent        │  │ Agent        │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                      Connector Architecture                               │  │
│  │                                                                           │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  │                        MCP Host                                      │  │
│  │  │                                                                   │  │  │
│  │  │  - Connector Lifecycle Management                                 │  │  │
│  │  │  - Skill Execution with Sandboxing                                 │  │  │
│  │  │  - Permission Management                                           │  │  │
│  │  │  - Tool Dispatch                                                   │  │  │
│  │  │  - Audit Logging                                                    │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ Gmail        │  │ Outlook      │  │ GitHub       │  │ Calendar     │  │  │
│  │  │ Connector    │  │ Connector    │  │ Connector    │  │ Connector    │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                    Extension/Plugin Architecture                           │  │
│  │                                                                           │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  │                        Core SDK                                        │  │
│  │  │                                                                   │  │  │
│  │  │  - TypeScript Client                                                │  │  │
│  │  │  - Python Client                                                     │  │  │
│  │  │  - REST API Wrapper                                                 │  │  │
│  │  │  - WebSocket Client                                                  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │  │
│  │  │ Chrome       │  │ VS Code      │  │ Custom       │                  │  │
│  │  │ Extension    │  │ Extension    │  │ Extensions   │                  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Hybrid LLM Routing Strategy

### Routing Decision Engine

The Router Service implements a hybrid routing strategy that intelligently routes requests to the most appropriate LLM provider based on multiple factors.

#### Routing Factors

**1. Sensitivity Analysis**
- **PII Detection**: Detects personally identifiable information
- **Sensitive Data**: Detects financial, health, or confidential data
- **Routing Decision**: High sensitivity → Local provider (Ollama)
- **Rationale**: Keep sensitive data on-premises

**2. Complexity Analysis**
- **Token Count**: Estimates input/output token requirements
- **Reasoning Required**: Determines if complex reasoning is needed
- **Routing Decision**: High complexity → High-capability cloud provider (Claude Opus, GPT-4)
- **Rationale**: Cloud providers have better reasoning capabilities

**3. Budget Analysis**
- **User Budget**: Checks user's monthly budget
- **Cost Estimation**: Estimates cost for request
- **Routing Decision**: Budget constraint → Local or cheaper cloud provider (Claude Haiku, GPT-3.5)
- **Rationale**: Stay within user budget

**4. Latency Requirements**
- **Real-time**: Requires sub-second response
- **Async**: Can tolerate longer response times
- **Routing Decision**: Real-time → Local or fast cloud provider
- **Rationale**: Minimize latency for real-time interactions

**5. Quality Requirements**
- **Accuracy**: Requires high accuracy
- **Speed**: Requires fast response
- **Routing Decision**: High accuracy → High-capability provider
- **Rationale**: Quality over speed for critical tasks

### Provider Selection Matrix

| Sensitivity | Complexity | Budget | Latency | Quality | Provider |
|-------------|------------|--------|---------|---------|----------|
| High | Low | Low | Low | Medium | Ollama (Llama 3) |
| High | High | Low | Low | High | Ollama (Mistral) |
| Low | Low | Low | High | Medium | Claude Haiku |
| Low | High | High | Low | High | Claude Opus |
| Low | Medium | Medium | Medium | Medium | GPT-3.5 |
| Low | High | High | Medium | High | GPT-4 |

### Routing Algorithm

```
def route_request(prompt, context):
    # Analyze sensitivity
    sensitivity = analyze_sensitivity(prompt, context)
    
    # Analyze complexity
    complexity = analyze_complexity(prompt)
    
    # Check budget
    budget = get_user_budget(context.user_id)
    cost_estimate = estimate_cost(prompt, complexity)
    
    # Check latency requirements
    latency_req = get_latency_requirement(context)
    
    # Check quality requirements
    quality_req = get_quality_requirement(context)
    
    # Select provider
    if sensitivity == HIGH:
        return select_local_provider(complexity)
    elif budget < cost_estimate:
        return select_cheap_provider(complexity, latency_req)
    elif complexity == HIGH and quality_req == HIGH:
        return select_premium_provider(latency_req)
    elif latency_req == REALTIME:
        return select_fast_provider(complexity)
    else:
        return select_balanced_provider(complexity, budget)
```

### Caching Strategy

**1. Response Cache**
- **Key**: Hash of prompt + provider + model
- **TTL**: 1 hour
- **Invalidation**: Time-based
- **Use Case**: Exact prompt repeats

**2. Semantic Cache**
- **Key**: Vector embedding of prompt
- **Similarity Threshold**: 0.95 cosine similarity
- **TTL**: 24 hours
- **Invalidation**: Manual
- **Use Case**: Similar prompts with different wording

**3. Prompt Cache**
- **Key**: Hash of prompt template
- **TTL**: 7 days
- **Invalidation**: Manual
- **Use Case**: Reusable prompt templates

### Cost Tracking

**Budget Enforcement**
- Per-user monthly budget
- Per-request cost estimation
- Budget alerts at 50%, 75%, 90%
- Budget enforcement (block when exceeded)

**Cost Calculation**
```
cost = (input_tokens * input_price) + (output_tokens * output_price)
```

**Cost Reporting**
- Daily cost summaries
- Per-user cost breakdown
- Per-provider cost analysis
- Cost optimization recommendations

## Multi-Agent Orchestration

### Agent Types

**1. Researcher Agent**
- **Purpose**: Research and information gathering
- **Capabilities**: Web search, document analysis, summarization
- **Tools**: Search API, Document Parser, Summarizer
- **Typical Use Case**: Research a topic, gather information

**2. Planner Agent**
- **Purpose**: Planning and task decomposition
- **Capabilities**: Goal decomposition, dependency analysis, timeline generation
- **Tools**: Task Parser, Dependency Analyzer, Timeline Generator
- **Typical Use Case**: Plan a project, break down into tasks

**3. Executor Agent**
- **Purpose**: Task execution and automation
- **Capabilities**: API calls, tool execution, workflow automation
- **Tools**: API Client, Tool Executor, Workflow Engine
- **Typical Use Case**: Execute tasks, automate workflows

**4. Analyst Agent**
- **Purpose**: Analysis and insight generation
- **Capabilities**: Data analysis, trend detection, insight generation
- **Tools**: Data Analyzer, Trend Detector, Insight Generator
- **Typical Use Case**: Analyze data, generate insights

### Agent Lifecycle

**1. Registration**
- Agent types registered with Supervisor
- Agent capabilities advertised
- Agent dependencies declared

**2. Execution**
- Agent instantiated with goal
- Plan-act-observe-reflect loop executed
- State persisted for resumption

**3. Orchestration**
- Concurrent execution: Multiple agents run in parallel
- Sequential execution: Agents run in sequence
- Mixed execution: Combination of concurrent and sequential

**4. Result Merging**
- Results from multiple agents merged
- Conflicts resolved via priority
- Final result returned to user

### Plan-Act-Observe-Reflect Loop

**Plan Phase**
- Generate plan using LLM
- Validate plan with guardrails
- Estimate cost and time
- Check budget constraints

**Act Phase**
- Execute planned actions
- Call tools via MCP Host
- Track execution time
- Monitor cost

**Observe Phase**
- Observe action results
- Ingest observations into memory
- Update agent state
- Check completion criteria

**Reflect Phase**
- Reflect on progress
- Adjust plan if needed
- Decide next action
- Check for completion

### Agent State Management

**State Persistence**
- Agent state saved to database
- State includes: plan, observations, reflections, budget
- State versioned for rollback
- State encrypted for security

**State Resumption**
- Agent can be paused and resumed
- State restored from database
- Execution continues from last step
- Budget tracking continues

**State Versioning**
- Each state change versioned
- Rollback to previous version
- Audit trail of state changes
- Debugging support

## Connector Architecture

### MCP Host

The Model Context Protocol (MCP) Host manages connectors and skills.

**Connector Lifecycle**
1. **Registration**: Connector registered with MCP Host
2. **Authentication**: OAuth2 flow for external services
3. **Synchronization**: Periodic data sync
4. **Error Handling**: Retry logic, error reporting
5. **Deactivation**: Graceful deactivation

**Skill Execution**
- Skills executed in sandboxed environment
- Permission checks before execution
- Tool dispatch via MCP Host
- Result validation and sanitization
- Audit logging of all actions

**Permission Management**
- Skills declare required permissions
- User grants permissions per skill
- Runtime permission checks
- Permission revocation support
- Audit trail of permission usage

### Connector Types

**1. Gmail Connector**
- **Purpose**: Email synchronization and processing
- **Capabilities**: Sync emails, classify, extract entities
- **OAuth**: Google OAuth2
- **Sync Frequency**: Every 15 minutes
- **Data**: Email headers, body, attachments

**2. Outlook Connector**
- **Purpose**: Email synchronization and processing
- **Capabilities**: Sync emails, classify, extract entities
- **OAuth**: Microsoft OAuth2
- **Sync Frequency**: Every 15 minutes
- **Data**: Email headers, body, attachments

**3. GitHub Connector**
- **Purpose**: Repository integration
- **Capabilities**: Sync issues, PRs, commits
- **OAuth**: GitHub OAuth2
- **Sync Frequency**: Every 30 minutes
- **Data**: Issues, PRs, commits, comments

**4. Calendar Connector**
- **Purpose**: Calendar integration
- **Capabilities**: Sync events, create events
- **OAuth**: Google/Microsoft OAuth2
- **Sync Frequency**: Every 5 minutes
- **Data**: Events, reminders, attendees

### Skill Architecture

**Skill Definition**
- Name and description
- Required permissions
- Input/output schema
- Execution code (Python/JavaScript)
- Metadata (version, author, tags)

**Skill Execution**
- Skill loaded into sandbox
- Input validated against schema
- Permissions checked
- Code executed
- Output validated
- Result returned

**Skill Permissions**
- `read_tasks`: Read user tasks
- `write_tasks`: Create/update/delete tasks
- `read_memory`: Read user memory
- `write_memory`: Create/update/delete memory
- `read_email`: Read user emails
- `send_email`: Send emails
- `read_calendar`: Read calendar events
- `write_calendar`: Create/update calendar events

## Extension/Plugin Architecture

### Core SDK

**TypeScript Client**
- REST API client
- WebSocket client
- Type definitions
- Error handling
- Retry logic

**Python Client**
- REST API client
- WebSocket client
- Type hints
- Error handling
- Retry logic

### Chrome Extension

**Components**
- Side Panel: Main UI
- Quick Capture: Fast task creation
- Memory Search: Memory query
- Today's Tasks: Task list
- Notifications: Real-time alerts

**Architecture**
- React + TypeScript
- Core SDK integration
- WebSocket for real-time
- Local storage for persistence
- OAuth2 for authentication

### VS Code Extension

**Components**
- Dashboard Panel: Task overview
- Timer: Time tracking
- TODO Integration: TODO to task conversion
- Command Palette: Quick actions

**Architecture**
- VS Code API
- Core SDK integration
- WebSocket for real-time
- Local storage for persistence
- Device authentication

### Plugin Architecture

**Plugin Definition**
- Plugin manifest
- Entry points
- Permissions
- Dependencies
- Metadata

**Plugin Lifecycle**
1. **Installation**: Plugin installed from registry
2. **Activation**: Plugin activated on demand
3. **Execution**: Plugin code executed
4. **Deactivation**: Plugin deactivated
5. **Uninstallation**: Plugin removed

**Plugin Permissions**
- Read access to tasks
- Write access to tasks
- Read access to memory
- Write access to memory
- Custom permissions

## Prompt Engineering

### Prompt Templates

**Task Parsing Template**
```
Parse the following natural language input into a task structure.
Extract: title, due date, priority, description.

Input: {input}

Output format:
{
  "title": "...",
  "due_at": "ISO 8601 date or null",
  "priority": "low|medium|high|urgent",
  "description": "..."
}
```

**Memory Classification Template**
```
Classify the following memory into one of four layers:
- working: Current context, temporary
- short_term: Recent information, hours to days
- semantic: Long-term knowledge, concepts
- long_term: Permanent knowledge, rarely changes

Memory: {memory}
Source: {source}

Output: {layer}
```

**Agent Planning Template**
```
Given the following goal, create a step-by-step plan.
Each step should include: action, tool, expected_result.

Goal: {goal}
Available tools: {tools}

Output format:
[
  {
    "step": 1,
    "action": "...",
    "tool": "...",
    "expected_result": "..."
  }
]
```

### Prompt Optimization

**Token Efficiency**
- Remove redundant instructions
- Use concise language
- Minimize examples
- Use structured output

**Quality Optimization**
- Include relevant context
- Use few-shot examples
- Specify output format
- Add quality constraints

**Cost Optimization**
- Cache prompt templates
- Reuse prompts across requests
- Use cheaper models for simple tasks
- Batch similar requests

### Prompt Testing

**Evaluation Framework**
- Golden dataset for prompt evaluation
- LLM-as-judge for subjective metrics
- Automated metrics (accuracy, relevance)
- A/B testing for prompt variants

**Prompt Versioning**
- Version control for prompts
- A/B testing in production
- Rollback capability
- Performance tracking

## Guardrails

### Input Validation

**PII Detection**
- Detect personally identifiable information
- Redact or block PII
- Log PII detection events
- Alert on PII violations

**Injection Detection**
- Detect prompt injection attempts
- Block malicious inputs
- Log injection attempts
- Alert on repeated violations

**Length Validation**
- Enforce maximum input length
- Truncate or reject long inputs
- Log length violations
- Alert on repeated violations

### Output Filtering

**Content Filtering**
- Filter harmful content
- Filter biased content
- Filter inappropriate content
- Log filtering events

**PII Redaction**
- Redact PII from outputs
- Verify redaction quality
- Log redaction events
- Alert on redaction failures

**Quality Validation**
- Validate output format
- Validate output completeness
- Validate output relevance
- Log quality issues

## Monitoring and Observability

### AI-Specific Metrics

**Routing Metrics**
- Provider selection distribution
- Routing decision accuracy
- Cache hit rate
- Routing latency

**Agent Metrics**
- Agent execution time
- Agent success rate
- Agent step count
- Agent cost

**Connector Metrics**
- Connector sync frequency
- Connector success rate
- Connector error rate
- Connector latency

**Prompt Metrics**
- Prompt token count
- Prompt success rate
- Prompt quality score
- Prompt cost

### AI-Specific Logging

**Routing Logs**
- Routing decisions
- Provider selection
- Cache hits/misses
- Cost calculations

**Agent Logs**
- Agent lifecycle events
- Plan-act-observe-reflect steps
- State changes
- Tool calls

**Connector Logs**
- Connector sync events
- OAuth flows
- Skill executions
- Permission checks

## Conclusion

The TEMPUS AI architecture provides a comprehensive framework for LLM integration, multi-agent orchestration, connector management, and extension development. The hybrid routing strategy balances cost, quality, and privacy while the multi-agent system enables complex task automation. The connector architecture integrates with external services, and the extension architecture enables rich client applications.

Key architectural strengths:
1. Hybrid routing for optimal provider selection
2. Multi-agent orchestration for complex tasks
3. Connector architecture for external integrations
4. Extension architecture for rich clients
5. Comprehensive guardrails for safety
6. Prompt engineering best practices
7. AI-specific monitoring and observability
