# Kortix (Suna) - AI Agent Platform Copilot Instructions

## Architecture Overview

Kortix is a full-stack platform for building AI agents, featuring:
- **Backend**: Python FastAPI with Dramatiq workers, Redis caching, Supabase DB
- **Frontend**: Next.js 14+ React app with TypeScript, TailwindCSS, shadcn/ui
- **Mobile**: React Native Expo app with NativeWind (TailwindCSS)
- **Agent System**: Custom AgentPress framework with tool execution and streaming

## Key Development Patterns

### Message System Architecture
- **UnifiedMessage** (`frontend/src/components/thread/types.ts`): Core message interface with `message_id`, `thread_id`, `agent_id`, `type`, and JSON `content`/`metadata` fields
- **Message Types**: `'user' | 'assistant' | 'tool' | 'system' | 'status' | 'browser_state' | 'image_context'`
- **ThreadContent** component groups messages by agent and handles streaming states
- **Tool execution** uses XML format: `<function_calls><invoke name="tool_name"><parameter>...</parameter></invoke></function_calls>`

### Backend Agent Execution
- **ThreadManager** (`backend/core/agentpress/thread_manager.py`): Central orchestrator for LLM conversations and tool execution
- **Dramatiq workers** handle agent execution asynchronously via `run_agent_background.py`
- **Tools**: Extend `Tool` base class with `execute()` method, registered via `ToolRegistry`
- **Streaming**: Real-time message streaming through WebSocket-like endpoints

### Development Workflow

#### Starting Development Stack
```bash
# Backend (3 terminals)
cd backend
docker compose up redis                                    # Terminal 1: Redis
uv run dramatiq --processes 4 --threads 4 run_agent_background  # Terminal 2: Workers  
uv run api.py                                             # Terminal 3: API server

# Frontend
cd frontend && npm install && npm run dev                 # Port 3000

# Mobile (if needed)  
cd apps/mobile && npm install && npm start               # Expo dev server
```

#### Environment Setup
- Run `python setup.py` from root to auto-configure all `.env` files
- Backend uses `uv` for Python package management
- Frontend connects to `http://localhost:8000/api`

### Frontend Conventions

#### Component Organization
- **Co-locate by feature**: `/components/thread/`, `/components/input/`, etc.
- **Index exports**: Use `index.ts` files for clean imports
- **Types**: Define interfaces in `types.ts` alongside components
- **Hooks**: Custom logic in `/hooks/` directory

#### Styling System
- **Design tokens only**: Use semantic tokens from `global.css` (`bg-background`, `text-foreground`, etc.)
- **Never hardcode colors**: Always use design system tokens with opacity variants (`bg-primary/10`)
- **TailwindCSS**: Primary styling approach with custom design system

#### State Management
- **React Query**: Server state and caching (agents, messages, files)
- **Zustand stores**: Client state (`agent-selection-store.ts`)
- **Context providers**: Auth, theme, and global state

### Backend Conventions

#### Core Services
- **DBConnection**: Supabase integration with typed queries
- **AgentPress**: Custom framework for agent conversation management  
- **Tool System**: Modular tools extending base `Tool` class
- **Billing Integration**: Usage tracking and limits

#### Message Processing
- **Streaming responses**: Use `StreamingResponse` with async generators
- **Tool execution**: Parsed from XML in message content, executed via registry
- **Error handling**: Structured error responses with status codes

### Mobile App Patterns (React Native + Expo)
- **NativeWind**: TailwindCSS for React Native styling
- **Expo Router**: File-based routing system
- **Custom fonts**: Roobert font family loaded via assets
- **Design system**: Consistent with web using same tokens

## Common Development Tasks

### Adding New Tools
1. Create tool class extending `Tool` in `backend/core/tools/`
2. Implement `execute()` method with proper error handling
3. Register in `ToolRegistry` initialization
4. Add frontend UI for tool results in `ThreadContent`

### Adding New Agent Types  
1. Configure agent in `backend/core/agent_service.py`
2. Add agent-specific prompts in `backend/core/prompts/`
3. Update frontend agent selection UI
4. Test with streaming and tool execution

### Debugging Agent Issues
- Check Dramatiq worker logs for execution errors
- Monitor Redis for queued jobs: `redis-cli monitor`
- Use `debugMode` prop in `ThreadContent` for raw message inspection
- Check Supabase logs for database constraint violations

## Integration Points

- **Supabase**: Auth, database, real-time subscriptions
- **Redis**: Caching and Dramatiq job queue  
- **Langfuse**: LLM observability and tracing
- **External APIs**: OpenAI, Anthropic, Ollama for LLM calls
- **Tool integrations**: Composio, Firecrawl, Tavily, etc.

## File Patterns to Follow

- **Environment**: Use `setup.py` to generate all config files
- **Types**: Match backend schema exactly in frontend types
- **Components**: Keep `ThreadContent` pattern for complex message rendering
- **API**: Follow FastAPI patterns with proper error handling and validation
- **Mobile**: Follow `.cursorrules` conventions for React Native structure